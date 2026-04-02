use serenity::all::*;
use tracing::info;

use crate::consent::SessionState;
use crate::state::AppState;
use crate::storage::pseudonymize;

pub async fn handle_stop(
    ctx: &Context,
    command: &CommandInteraction,
    state: &AppState,
) -> Result<(), serenity::Error> {
    let guild_id = command.guild_id.unwrap();

    // Check for active recording
    let session = {
        let manager = state.consent.lock().await;
        match manager.get_session(guild_id.get()) {
            Some(s) if s.state == SessionState::Recording => {
                // Verify caller is initiator or admin
                if s.initiator_id != command.user.id {
                    command
                        .create_response(
                            &ctx.http,
                            CreateInteractionResponse::Message(
                                CreateInteractionResponseMessage::new()
                                    .content(
                                        "Only the person who started the recording can stop it.",
                                    )
                                    .ephemeral(true),
                            ),
                        )
                        .await?;
                    return Ok(());
                }
                s.session_id.clone()
            }
            _ => {
                command
                    .create_response(
                        &ctx.http,
                        CreateInteractionResponse::Message(
                            CreateInteractionResponseMessage::new()
                                .content("No active recording in this server.")
                                .ephemeral(true),
                        ),
                    )
                    .await?;
                return Ok(());
            }
        }
    };

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new().content("Stopping recording..."),
            ),
        )
        .await?;

    // Leave voice channel
    let manager = songbird::get(ctx).await.unwrap();
    let _ = manager.leave(guild_id).await;

    // Finalize session
    {
        let mut consent_mgr = state.consent.lock().await;
        if let Some(s) = consent_mgr.get_session_mut(guild_id.get()) {
            s.state = SessionState::Finalizing;
        }
    }

    // Write bundle files
    {
        let consent_mgr = state.consent.lock().await;
        let mut bundles = state.bundles.lock().await;

        if let (Some(consent), Some(bundle)) = (
            consent_mgr.get_session(guild_id.get()),
            bundles.get_mut(&guild_id.get()),
        ) {
            bundle.ended_at = Some(chrono::Utc::now());

            // Rename PCM files from SSRC to pseudo ID
            let ssrc_map = state.ssrc_maps.lock().await;
            if let Some(map) = ssrc_map.get(&guild_id.get()) {
                let map = map.lock().await;
                for (ssrc, user_id) in map.iter() {
                    let pseudo = pseudonymize(*user_id);
                    let src = bundle.pcm_dir().join(format!("{}.pcm", ssrc));
                    let dst = bundle.pcm_dir().join(format!("{}.pcm", pseudo));
                    if src.exists() {
                        let _ = std::fs::rename(&src, &dst);
                        info!(ssrc = ssrc, pseudo = %pseudo, "track_renamed");
                    }
                }
            }

            // TODO: Convert PCM to FLAC, upload to S3

            bundle.write_meta(consent);
            bundle.write_consent(consent);

            info!(session_id = %session, "session_finalized");
        }
    }

    // Cleanup
    {
        let mut consent_mgr = state.consent.lock().await;
        consent_mgr.remove_session(guild_id.get());
    }
    {
        let mut bundles = state.bundles.lock().await;
        bundles.remove(&guild_id.get());
    }

    command
        .channel_id
        .say(&ctx.http, "Recording complete.")
        .await?;

    Ok(())
}
