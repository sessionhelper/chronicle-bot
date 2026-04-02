pub mod manager;
pub mod embeds;

pub use manager::{ConsentManager, ConsentScope, ConsentSession, SessionState};
pub use embeds::build_consent_embed;
