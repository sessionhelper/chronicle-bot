use std::collections::HashMap;
use std::io::Write;
use std::path::PathBuf;
use std::sync::Arc;

use serenity::async_trait;
use songbird::events::context_data::VoiceTick;
use songbird::{CoreEvent, Event, EventContext, EventHandler as VoiceEventHandler};
use tokio::sync::Mutex;
use tracing::info;

struct SpeakerWriter {
    file: std::fs::File,
    bytes_written: u64,
}

pub struct AudioReceiver {
    output_dir: PathBuf,
    writers: Arc<Mutex<HashMap<u32, SpeakerWriter>>>,
    ssrc_to_user: Arc<Mutex<HashMap<u32, u64>>>,
}

impl AudioReceiver {
    fn new(output_dir: PathBuf, ssrc_map: Arc<Mutex<HashMap<u32, u64>>>) -> Self {
        Self {
            output_dir,
            writers: Arc::new(Mutex::new(HashMap::new())),
            ssrc_to_user: ssrc_map,
        }
    }

    /// Register audio receiver and speaking tracker on a songbird Call.
    /// Returns the shared SSRC→user_id map.
    pub fn register(
        call: &mut songbird::Call,
        output_dir: PathBuf,
    ) -> Arc<Mutex<HashMap<u32, u64>>> {
        let ssrc_map = Arc::new(Mutex::new(HashMap::new()));

        let receiver = Self::new(output_dir, ssrc_map.clone());
        call.add_global_event(CoreEvent::VoiceTick.into(), receiver);

        let tracker = SpeakingTracker {
            ssrc_to_user: ssrc_map.clone(),
        };
        call.add_global_event(CoreEvent::SpeakingStateUpdate.into(), tracker);

        ssrc_map
    }
}

#[async_trait]
impl VoiceEventHandler for AudioReceiver {
    async fn act(&self, ctx: &EventContext<'_>) -> Option<Event> {
        if let EventContext::VoiceTick(VoiceTick {
            speaking, silent: _, ..
        }) = ctx
        {
            let mut writers = self.writers.lock().await;

            for (ssrc, data) in speaking {
                if let Some(decoded) = &data.decoded_voice {
                    let writer = writers.entry(*ssrc).or_insert_with(|| {
                        let path = self.output_dir.join(format!("{}.pcm", ssrc));
                        info!(ssrc = ssrc, path = %path.display(), "new_speaker");
                        let file =
                            std::fs::File::create(&path).expect("Failed to create PCM file");
                        SpeakerWriter {
                            file,
                            bytes_written: 0,
                        }
                    });

                    // Hot path — zero-copy reinterpret of &[i16] as &[u8]
                    let byte_len = decoded.len() * 2;
                    let bytes: &[u8] = unsafe {
                        std::slice::from_raw_parts(decoded.as_ptr() as *const u8, byte_len)
                    };
                    let _ = writer.file.write_all(bytes);
                    writer.bytes_written += byte_len as u64;
                }
            }
        }
        None
    }
}

/// Tracks SSRC → user_id mappings from Discord speaking events.
struct SpeakingTracker {
    ssrc_to_user: Arc<Mutex<HashMap<u32, u64>>>,
}

#[async_trait]
impl VoiceEventHandler for SpeakingTracker {
    async fn act(&self, ctx: &EventContext<'_>) -> Option<Event> {
        if let EventContext::SpeakingStateUpdate(speaking) = ctx {
            if let Some(uid) = speaking.user_id {
                let mut map = self.ssrc_to_user.lock().await;
                if !map.contains_key(&speaking.ssrc) {
                    info!(ssrc = speaking.ssrc, user_id = %uid, "ssrc_mapped");
                }
                map.insert(speaking.ssrc, uid.0);
            }
        }
        None
    }
}
