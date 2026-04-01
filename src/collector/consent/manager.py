from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime

import discord
import structlog

from collector.config import settings
from collector.consent.types import ConsentScope, SessionState

log = structlog.get_logger()


@dataclass
class ParticipantConsent:
    user_id: int
    display_name: str
    scope: ConsentScope | None = None
    consented_at: datetime | None = None
    mid_session_join: bool = False


@dataclass
class ConsentSession:
    guild_id: int
    channel_id: int
    text_channel_id: int
    initiator_id: int
    state: SessionState = SessionState.IDLE
    participants: dict[int, ParticipantConsent] = field(default_factory=dict)
    _timeout_task: asyncio.Task | None = field(default=None, repr=False)
    _quorum_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)

    def add_participant(self, member: discord.Member, mid_session: bool = False) -> None:
        if member.id not in self.participants:
            self.participants[member.id] = ParticipantConsent(
                user_id=member.id,
                display_name=member.display_name,
                mid_session_join=mid_session,
            )

    def record_consent(self, user_id: int, scope: ConsentScope) -> None:
        if user_id not in self.participants:
            return
        p = self.participants[user_id]
        p.scope = scope
        p.consented_at = datetime.now(UTC)
        log.info("consent_recorded", user_id=user_id, scope=scope.value)
        if self._check_quorum():
            self._quorum_event.set()

    def remove_participant(self, user_id: int) -> None:
        """Remove a participant who left before consenting."""
        if user_id in self.participants and self.participants[user_id].scope is None:
            del self.participants[user_id]
            log.info("participant_removed_before_consent", user_id=user_id)
            if self._check_quorum():
                self._quorum_event.set()

    def _check_quorum(self) -> bool:
        """Check if all participants have responded."""
        if not self.participants:
            return False
        return all(p.scope is not None for p in self.participants.values())

    @property
    def has_any_decline(self) -> bool:
        return any(p.scope == ConsentScope.DECLINE for p in self.participants.values())

    @property
    def consented_user_ids(self) -> set[int]:
        return {uid for uid, p in self.participants.items() if p.scope == ConsentScope.FULL}

    @property
    def pending_user_ids(self) -> set[int]:
        return {uid for uid, p in self.participants.items() if p.scope is None}

    @property
    def consent_summary(self) -> str:
        lines = []
        for p in self.participants.values():
            if p.scope is None:
                status = "pending"
            elif p.scope == ConsentScope.FULL:
                status = "accepted"
            elif p.scope == ConsentScope.DECLINE_AUDIO:
                status = "declined audio"
            else:
                status = "declined"
            lines.append(f"  {p.display_name}: {status}")
        return "\n".join(lines)

    async def wait_for_quorum(self) -> bool:
        """Wait for all participants to respond.

        Returns True if quorum met, False if timed out or cancelled.
        """
        self.state = SessionState.AWAITING_CONSENT
        self._quorum_event.clear()

        # Already met (edge case: everyone already responded)
        if self._check_quorum():
            return self._evaluate_quorum()

        # Wait with timeout
        try:
            await asyncio.wait_for(
                self._quorum_event.wait(),
                timeout=settings.consent_timeout_seconds,
            )
            return self._evaluate_quorum()
        except TimeoutError:
            log.info("consent_timeout", pending=list(self.pending_user_ids))
            # Grace period — one more chance
            if self.pending_user_ids:
                self._quorum_event.clear()
                try:
                    await asyncio.wait_for(
                        self._quorum_event.wait(),
                        timeout=settings.consent_grace_seconds,
                    )
                    return self._evaluate_quorum()
                except TimeoutError:
                    log.info("consent_grace_timeout", pending=list(self.pending_user_ids))
                    self.state = SessionState.CANCELLED
                    return False

    def _evaluate_quorum(self) -> bool:
        if settings.require_all_consent and self.has_any_decline:
            self.state = SessionState.CANCELLED
            return False
        if len(self.consented_user_ids) < settings.min_participants:
            self.state = SessionState.CANCELLED
            return False
        return True

    def to_consent_json(self, pseudo_map: dict[int, str]) -> dict:
        """Export consent data with pseudonymized IDs."""
        participants = {}
        for uid, p in self.participants.items():
            if p.scope is None:
                continue
            pseudo_id = pseudo_map.get(uid, str(uid))
            participants[pseudo_id] = {
                "consented_at": p.consented_at.isoformat() if p.consented_at else None,
                "scope": p.scope.value,
                "audio_release": p.scope == ConsentScope.FULL,
                "mid_session_join": p.mid_session_join,
            }
        return {
            "consent_version": "1.0",
            "license": "CC BY-SA 4.0",
            "participants": participants,
        }


class ConsentManager:
    """Manages consent sessions across guilds. One active session per guild."""

    def __init__(self) -> None:
        self._sessions: dict[int, ConsentSession] = {}  # guild_id -> session

    def get_session(self, guild_id: int) -> ConsentSession | None:
        return self._sessions.get(guild_id)

    def create_session(
        self,
        guild_id: int,
        channel_id: int,
        text_channel_id: int,
        initiator_id: int,
        members: list[discord.Member],
    ) -> ConsentSession:
        session = ConsentSession(
            guild_id=guild_id,
            channel_id=channel_id,
            text_channel_id=text_channel_id,
            initiator_id=initiator_id,
        )
        for m in members:
            session.add_participant(m)
        self._sessions[guild_id] = session
        return session

    def remove_session(self, guild_id: int) -> None:
        self._sessions.pop(guild_id, None)

    def has_active_session(self, guild_id: int) -> bool:
        s = self._sessions.get(guild_id)
        if s is None:
            return False
        return s.state in (
            SessionState.AWAITING_CONSENT,
            SessionState.RECORDING,
            SessionState.FINALIZING,
        )
