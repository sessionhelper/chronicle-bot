# ttrpg-collector

Discord bot that records TTRPG voice sessions for an open audio transcription dataset.

Records per-speaker audio tracks with explicit consent, bundles session metadata, and uploads to S3-compatible storage for eventual release on HuggingFace under CC BY-SA 4.0.

## Building

```bash
cd voice-capture
cargo build --release
```

Requires `cmake` and `ffmpeg`.

## Running

```bash
cp .env.example .env
# Edit .env — add DISCORD_TOKEN and S3 credentials
cd voice-capture
cargo run --release
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/record` | Start recording the voice channel you're in |
| `/stop` | Stop the current recording |

### `/record` Options

| Option | Description |
|--------|-------------|
| `system` | Game system (e.g., "D&D 5e") |
| `campaign` | Campaign name |

## How It Works

1. GM runs `/record` in a text channel while in a voice channel
2. Bot posts a consent embed — each player clicks Accept, Decline Audio, or Decline
3. Recording starts after everyone responds
4. Bot joins voice, captures per-user audio via DAVE E2EE
5. GM runs `/stop` — audio is converted to FLAC and uploaded to S3

## License

Dataset contributions are released under CC BY-SA 4.0.
