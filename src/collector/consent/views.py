from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from collector.consent.types import ConsentScope

if TYPE_CHECKING:
    from collector.consent.manager import ConsentSession


CONSENT_TEXT = (
    "This session will be recorded for the **TTRPG Open Dataset** project.\n\n"
    "Your audio will be:\n"
    "- Recorded as a separate per-speaker track\n"
    "- Transcribed and reviewed for PII\n"
    "- Released under **CC BY-SA 4.0**\n\n"
    "You can decline without leaving the voice channel — "
    "your audio simply won't be captured."
)


def build_consent_embed(session: ConsentSession) -> discord.Embed:
    pending = []
    accepted = []
    declined = []

    for p in session.participants.values():
        name = p.display_name
        if p.scope is None:
            pending.append(name)
        elif p.scope == ConsentScope.FULL:
            accepted.append(name)
        elif p.scope == ConsentScope.DECLINE_AUDIO:
            declined.append(f"{name} (audio only)")
        else:
            declined.append(name)

    embed = discord.Embed(
        title="Session Recording — Open Dataset",
        description=CONSENT_TEXT,
        color=0x5A5A5A,
    )

    if pending:
        embed.add_field(name="Waiting for", value="\n".join(pending), inline=True)
    if accepted:
        embed.add_field(name="Accepted", value="\n".join(accepted), inline=True)
    if declined:
        embed.add_field(name="Declined", value="\n".join(declined), inline=True)

    return embed


class ConsentView(discord.ui.View):
    """Button view for consent collection."""

    def __init__(self, session: ConsentSession, on_response: callable) -> None:
        super().__init__(timeout=None)  # timeout handled by ConsentSession
        self.session = session
        self.on_response = on_response

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="consent_accept")
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self._handle(interaction, ConsentScope.FULL)

    @discord.ui.button(
        label="Decline Audio",
        style=discord.ButtonStyle.secondary,
        custom_id="consent_decline_audio",
    )
    async def decline_audio(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        await self._handle(interaction, ConsentScope.DECLINE_AUDIO)

    @discord.ui.button(
        label="Decline", style=discord.ButtonStyle.danger, custom_id="consent_decline"
    )
    async def decline(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self._handle(interaction, ConsentScope.DECLINE)

    async def _handle(self, interaction: discord.Interaction, scope: ConsentScope) -> None:
        user_id = interaction.user.id
        if user_id not in self.session.participants:
            await interaction.response.send_message(
                "You're not in the voice channel for this session.",
                ephemeral=True,
            )
            return

        if self.session.participants[user_id].scope is not None:
            await interaction.response.send_message(
                "You've already responded.",
                ephemeral=True,
            )
            return

        self.session.record_consent(user_id, scope)

        # Update the embed
        embed = build_consent_embed(self.session)
        await interaction.response.edit_message(embed=embed, view=self)

        if self.on_response:
            await self.on_response(self.session)
