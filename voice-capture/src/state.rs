use std::collections::HashMap;
use std::sync::Arc;

use tokio::sync::Mutex;

use crate::config::Config;
use crate::consent::ConsentManager;
use crate::storage::SessionBundle;

pub struct AppState {
    pub config: Config,
    pub consent: Arc<Mutex<ConsentManager>>,
    pub bundles: Arc<Mutex<HashMap<u64, SessionBundle>>>,
    /// guild_id -> ssrc_to_user_id map (populated by SpeakingStateUpdate)
    pub ssrc_maps: Arc<Mutex<HashMap<u64, Arc<Mutex<HashMap<u32, u64>>>>>>,
}

impl AppState {
    pub fn new(config: Config) -> Self {
        Self {
            config,
            consent: Arc::new(Mutex::new(ConsentManager::new())),
            bundles: Arc::new(Mutex::new(HashMap::new())),
            ssrc_maps: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}
