---
license: cc-by-sa-4.0
task_categories:
  - automatic-speech-recognition
  - speaker-diarization
language:
  - en
tags:
  - ttrpg
  - tabletop-rpg
  - multi-speaker
  - conversational
  - role-playing
  - discord
pretty_name: TTRPG Open Session Dataset
size_categories:
  - n<1K
---

# TTRPG Open Session Dataset

A community-contributed dataset of tabletop role-playing game (TTRPG) voice sessions recorded from Discord, with per-speaker audio tracks, aligned transcripts, and optional GM session notes.

## Dataset Description

### Summary

This dataset contains multi-track audio recordings of TTRPG sessions (D&D, Pathfinder, Call of Cthulhu, and other systems) contributed by game masters and players through the TTRPG Collector Discord bot. Each session includes:

- **Per-speaker WAV files** (48kHz, 16-bit, mono) — one track per consenting participant
- **Aligned transcripts** generated via automatic speech recognition
- **Session metadata** (game system, duration, participant count)
- **GM session notes** (optional, contributed by the game master)

All data was collected with explicit, informed consent from each participant.

### What Makes This Dataset Unique

- **Consent-first collection**: Every participant explicitly agreed to recording and public release
- **Per-speaker tracks**: Clean speaker separation without diarization — each speaker is a separate audio file
- **Multi-system coverage**: Sessions from multiple TTRPG systems, not just D&D
- **Role-playing speech**: Participants frequently alter their voices for character dialogue, creating a uniquely challenging diarization and ASR benchmark
- **Conversational + narrative**: Mix of out-of-character discussion, in-character dialogue, and GM narration

### Languages

English (primary). Other languages may appear as contributions grow.

## Dataset Structure

```
session_{id}/
  meta.json           — session metadata
  consent.json        — pseudonymized consent records
  audio/
    {pseudo_id}.wav   — per-speaker audio track
  transcript.json     — aligned transcript with speaker labels
  notes.md            — GM session notes (optional)
```

### Fields in `meta.json`

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Unique session identifier |
| started_at | string | ISO 8601 timestamp |
| ended_at | string | ISO 8601 timestamp |
| duration_seconds | float | Session duration |
| game_system | string | TTRPG system (e.g., "D&D 5e") |
| campaign_name | string | Campaign name (optional) |
| participant_count | int | Total participants |
| consented_audio_count | int | Participants who consented to audio |
| audio_format | object | Sample rate, bit depth, channels |
| quality_flags | object | Automated quality checks |

## Collection Process

1. A game master invites the TTRPG Collector Bot to their Discord server
2. Before a session, the GM runs `/record` in a voice channel
3. The bot posts a consent embed — each player must explicitly accept or decline
4. Recording starts only after all participants have responded
5. Audio is captured as separate per-speaker streams via Discord's voice API
6. On `/stop`, audio is converted to WAV and uploaded to cloud storage
7. A curation pipeline transcribes, checks for PII, and validates quality
8. Approved sessions are added to this dataset

### Consent

Every participant received the following information before consenting:
- Audio will be recorded as a separate per-speaker track
- Audio will be transcribed and reviewed for PII
- Audio and transcript will be released under CC BY-SA 4.0
- Discord identity will be pseudonymized
- Consent is withdrawable before publication

### Personal Information

- Discord user IDs are pseudonymized using a one-way hash with a session-specific salt (salt not stored)
- Display names are not included in the public dataset
- GM session notes are reviewed for PII before inclusion
- Participants who declined audio recording are not represented in the data

## Intended Uses

- Training and evaluating automatic speech recognition (ASR) models on conversational, multi-speaker audio
- Speaker diarization research, especially for speakers who alter their voices (character voices)
- Natural language processing on TTRPG dialogue and narrative
- Studying conversational dynamics in collaborative storytelling

## Limitations

- English-dominant (contributions in other languages welcome)
- Audio quality varies by participant's microphone and Discord connection
- Sessions may contain background noise, cross-talk, and ambient sound
- Character voice acting may cause speaker confusion in diarization systems
- GM notes quality and detail vary by contributor

## Citation

```bibtex
@dataset{ttrpg_open_sessions,
  title={TTRPG Open Session Dataset},
  year={2026},
  license={CC BY-SA 4.0},
  url={https://huggingface.co/datasets/[username]/ttrpg-open-sessions}
}
```

## License

CC BY-SA 4.0
