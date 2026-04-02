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
    user_id: Option<u64>,
}

pub struct AudioReceiver {
    output_dir: PathBuf,
    writers: Arc<Mutex<HashMap<u32, SpeakerWriter>>>,
    ssrc_to_user: Arc<Mutex<HashMap<u32, u64>>>,
}

impl AudioReceiver {
    pub fn new(output_dir: PathBuf) -> Self {
        Self {
            output_dir,
            writers: Arc::new(Mutex::new(HashMap::new())),
            ssrc_to_user: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Map an SSRC to a user ID (called from SpeakingStateUpdate)
    pub fn ssrc_map(&self) -> Arc<Mutex<HashMap<u32, u64>>> {
        self.ssrc_to_user.clone()
    }

    /// Register this receiver on a songbird Call
    pub fn register(call: &mut songbird::Call, output_dir: PathBuf) -> Arc<Mutex<HashMap<u32, u64>>> {
        let receiver = Self::new(output_dir);
        let ssrc_map = receiver.ssrc_map();
        call.add_global_event(CoreEvent::VoiceTick.into(), receiver);
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
                        // Check if we know the user ID for this SSRC
                        let path = self.output_dir.join(format!("{}.pcm", ssrc));
                        info!(ssrc = ssrc, path = %path.display(), "new_speaker");
                        let file =
                            std::fs::File::create(&path).expect("Failed to create PCM file");
                        SpeakerWriter {
                            file,
                            bytes_written: 0,
                            user_id: None,
                        }
                    });

                    // Hot path — no allocations, no logging
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
