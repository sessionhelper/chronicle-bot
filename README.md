# ttrpg-collector

Discord bot that records TTRPG voice sessions for an open audio transcription dataset.

Records per-speaker audio tracks with explicit consent, bundles session metadata, and uploads to cloud storage for eventual release on HuggingFace under CC BY-SA 4.0.

## Setup

```bash
# Install dependencies
uv sync

# Configure
cp .env.example .env
# Edit .env — add your DISCORD_TOKEN (required) and S3 credentials (optional)

# Run
uv run python -m collector.bot
```

**System dependency:** `ffmpeg` must be installed for audio conversion.

### Docker

```bash
docker compose up -d
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/record` | Start recording the voice channel you're in |
| `/stop` | Stop the current recording |
| `/status` | Show recording status |
| `/notes` | Submit session notes (after recording) |

### `/record` Options

| Option | Description |
|--------|-------------|
| `system` | Game system (e.g., "D&D 5e") — autocomplete from common systems |
| `campaign` | Campaign name |
| `session_number` | Session number |

## How It Works

1. GM runs `/record` in a text channel while in a voice channel
2. Bot joins voice and posts a consent embed tagging all members
3. Each player clicks Accept, Decline Audio, or Decline
4. Recording starts after everyone responds
5. Mid-session joiners get a DM + channel prompt for consent
6. GM runs `/stop` — audio is converted to WAV and uploaded
7. GM can add session notes via `/notes`

## Session Bundle

Each session produces:

```
sessions/{guild_id}/{session_id}/
  meta.json        — system, duration, participants, quality flags
  consent.json     — pseudonymized consent records
  pii.json         — real Discord IDs (NEVER in public dataset)
  audio/
    {pseudo_id}.wav — per-speaker, 48kHz 16-bit mono
  notes.md         — GM notes (optional)
```

## Development

```bash
uv sync --extra dev
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
```

## License

[TBD — project code license]

Dataset contributions are released under CC BY-SA 4.0.
