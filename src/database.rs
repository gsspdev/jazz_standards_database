//! Database loading functionality
//! 
//! This module handles loading the embedded jazz standards database from
//! the compiled binary.

use std::error::Error;
use crate::models::Song;

/// Load the jazz standards database from embedded JSON data
/// 
/// The JSON database is embedded into the binary at compile time using
/// the `include_str!` macro, making the CLI tool completely self-contained.
/// 
/// # Returns
/// 
/// A `Result` containing either:
/// - `Ok(Vec<Song>)` - Successfully parsed songs from the database
/// - `Err(Box<dyn Error>)` - JSON parsing error
/// 
/// # Examples
/// 
/// ```no_run
/// use jazz_standards_database::load_jazz_standards;
/// 
/// let songs = load_jazz_standards()?;
/// println!("Loaded {} songs", songs.len());
/// ```
pub fn load_jazz_standards() -> Result<Vec<Song>, Box<dyn Error>> {
    // Embed the JSON data directly into the binary at compile time
    // This makes the CLI tool completely self-contained with no external dependencies
    let json_content = include_str!("../JazzStandards.json");
    let songs: Vec<Song> = serde_json::from_str(json_content)?;
    Ok(songs)
}