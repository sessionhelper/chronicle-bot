# Privacy Policy — TTRPG Collector Bot

**Last updated:** 2026-04-01

## What This Bot Does

The TTRPG Collector Bot records tabletop RPG voice sessions in Discord for the purpose of building an open, community-contributed audio transcription dataset. This dataset will be released under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

## What Data We Collect

### Audio Recordings
- Per-speaker audio tracks from Discord voice channels
- Audio is only captured from users who explicitly consent via the in-channel consent prompt
- Audio is recorded in WAV format (48kHz, 16-bit, mono)

### Session Metadata
- Game system (e.g., "D&D 5e") — provided optionally by the session initiator
- Campaign name — provided optionally by the session initiator
- Session number — provided optionally by the session initiator
- Session start/end timestamps
- Number of participants
- Audio quality metrics

### Consent Records
- A record of each user's consent decision (accept, decline audio, or decline)
- Timestamp of consent

### GM Session Notes
- Text notes submitted voluntarily by the game master after a session
- GMs are reminded not to include personal information about players

### What We Do NOT Collect
- Message content from text channels
- User profile information beyond what is needed for consent tracking
- Server configuration or channel lists
- Direct messages (except the consent notification DM to mid-session joiners)

## How We Identify You

### In Our Private Storage
- Your Discord user ID and display name are stored in a private file (`pii.json`) that is used only for internal session management
- This file is **never** included in the public dataset

### In the Public Dataset
- Your Discord user ID is replaced with a pseudonymized identifier (a one-way hash with a session-specific salt that is not stored)
- Your display name is not included
- Your audio track filename uses the pseudonymized identifier
- There is no way to reverse the pseudonymization to recover your Discord identity

## Where Data Is Stored

- **During recording:** Audio is buffered to the bot's local disk
- **After recording:** Session bundles are uploaded to Backblaze B2 (encrypted at rest)
- **Public dataset:** Validated sessions are published on HuggingFace

## How Data Is Used

Your contributed audio will be:
1. Transcribed using automatic speech recognition
2. Reviewed for personal information
3. Included in a public dataset for training and evaluating transcription models
4. Released under CC BY-SA 4.0

## Your Rights

### Before Dataset Publication
- You may request deletion of your audio from any session by contacting the project maintainer
- Your consent is revocable at any time before your audio is included in a published dataset release

### After Dataset Publication
- Published dataset releases under CC BY-SA 4.0 cannot be recalled, as the license grants irrevocable rights to recipients
- However, your audio will be removed from future dataset releases upon request

### GDPR (EU Users)
- **Lawful basis:** Explicit consent (Article 6(1)(a) and Article 9(2)(a) for biometric data)
- **Right to access:** You may request a copy of your data
- **Right to erasure:** You may request deletion (subject to the limitations above regarding published releases)
- **Right to withdraw consent:** You may withdraw consent at any time
- **Data controller contact:** See contact information below

## Data Retention

- Raw audio files are retained in private storage until included in a dataset release
- Sessions that are not included in a release are deleted within 90 days
- Consent records are retained indefinitely as legal documentation

## Age Requirement

You must be at least 18 years old to consent to recording. If you are under 18, you must have parental or guardian consent.

## Third-Party Services

- **Discord:** Audio is captured via Discord's voice API. Discord's own privacy policy applies to your use of Discord.
- **Backblaze B2:** Session data is stored using Backblaze's S3-compatible storage service.
- **HuggingFace:** The public dataset is hosted on HuggingFace's platform.

## Changes to This Policy

We may update this privacy policy. Changes will be reflected in the "Last updated" date above. Continued use of the bot after changes constitutes acceptance.

## Contact

For data requests, questions, or concerns, contact the project maintainer:
- GitHub Issues: [repository URL]
- Email: [project email]
