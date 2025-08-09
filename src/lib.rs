//! Jazz Standards Database Library
//! 
//! This library provides data structures and functionality for working with
//! a comprehensive database of jazz standards including chord progressions,
//! metadata, and search capabilities.

pub mod models;
pub mod database;
pub mod search;
pub mod display;
pub mod stats;
pub mod cli;

// Re-export commonly used types
pub use models::{Song, Section, Segment};
pub use database::load_jazz_standards;
pub use search::{search_songs, filter_songs};
pub use display::{print_song_summary, print_song_detailed};
pub use stats::{show_statistics, list_field_values};
pub use cli::{Cli, Commands};