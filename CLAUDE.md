# ttrpg-collector

Discord bot for collecting TTRPG session audio for an open dataset.

## Stack

- Rust (serenity + songbird)
- songbird `next` branch for DAVE E2EE voice receive
- aws-sdk-s3 for S3-compatible uploads (Hetzner Object Storage)
- ffmpeg for PCM → FLAC conversion

## Layout

```
voice-capture/
  src/
    main.rs              — entry point, serenity client, event handlers
    config.rs            — env var config (clap)
    state.rs             — shared app state
    commands/
      record.rs          — /record slash command
      stop.rs            — /stop slash command (finalize + upload)
    consent/
      manager.rs         — consent state machine, quorum logic
      embeds.rs          — Discord embed + button builders
    voice/
      receiver.rs        — VoiceTick handler, per-user PCM to disk, SSRC tracking
    storage/
      bundle.rs          — meta.json, consent.json, pseudonymization
      s3.rs              — S3 upload with retry
  Cargo.toml
scripts/
  sync-s3.sh             — download S3 data locally
legal/                   — privacy policy, ToS, consent text, dataset card
```

## Building

```bash
cd voice-capture
cargo build --release
```

Requires: cmake (for opus build), ffmpeg (runtime, for PCM→FLAC)

## Running

```bash
cp .env.example .env  # fill in credentials
cd voice-capture
cargo run --release
```

## Git Workflow

- **main** — production, deploys to VPS on push
- **dev** — integration branch
- **feature/*** — branch from dev, merge back via --no-ff

## Key Decisions

- Full Rust — py-cord's DAVE voice receive was fundamentally broken (~10% packet capture)
- Songbird handles DAVE/E2EE natively with near-zero packet loss
- PCM written to disk, converted to FLAC on /stop, uploaded to S3
- Per-user tracks via SSRC → user_id mapping from SpeakingStateUpdate events
- Simple SHA256 hash for pseudonymization (no salt — voice is public anyway)
