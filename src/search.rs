//! Search and filtering functionality
//! 
//! This module provides functions for searching and filtering the jazz standards
//! database by various criteria such as title, composer, key, rhythm, etc.

use crate::models::Song;

/// Search songs by title or composer using partial matching
/// 
/// Performs case-insensitive partial matching on both song titles and composer names.
/// 
/// # Arguments
/// 
/// * `songs` - Slice of songs to search through
/// * `term` - Search term to match against titles and composers
/// 
/// # Returns
/// 
/// A vector of references to matching songs
/// 
/// # Examples
/// 
/// ```no_run
/// use jazz_standards_database::{load_jazz_standards, search_songs};
/// 
/// let songs = load_jazz_standards()?;
/// let results = search_songs(&songs, "miles");
/// println!("Found {} songs matching 'miles'", results.len());
/// ```
pub fn search_songs<'a>(songs: &'a [Song], term: &str) -> Vec<&'a Song> {
    let term_lower = term.to_lowercase();
    songs
        .iter()
        .filter(|song| {
            song.title.to_lowercase().contains(&term_lower)
                || song.composer
                    .as_ref()
                    .map_or(false, |c| c.to_lowercase().contains(&term_lower))
        })
        .collect()
}

/// Filter songs by multiple criteria
/// 
/// Filters songs based on various musical criteria. All specified criteria
/// must match for a song to be included in the results.
/// 
/// # Arguments
/// 
/// * `songs` - Slice of songs to filter
/// * `key` - Optional key filter (case-insensitive exact match)
/// * `rhythm` - Optional rhythm filter (case-insensitive partial match)
/// * `time` - Optional time signature filter (exact match)
/// * `composer` - Optional composer filter (case-insensitive partial match)
/// 
/// # Returns
/// 
/// A vector of references to songs matching all specified criteria
/// 
/// # Examples
/// 
/// ```no_run
/// use jazz_standards_database::{load_jazz_standards, filter_songs};
/// 
/// let songs = load_jazz_standards()?;
/// 
/// // Find all songs in C major with swing rhythm
/// let results = filter_songs(&songs, Some("C"), Some("swing"), None, None);
/// 
/// // Find all Miles Davis compositions
/// let miles_songs = filter_songs(&songs, None, None, None, Some("miles davis"));
/// ```
pub fn filter_songs<'a>(
    songs: &'a [Song], 
    key: Option<&str>, 
    rhythm: Option<&str>, 
    time: Option<&str>, 
    composer: Option<&str>
) -> Vec<&'a Song> {
    songs
        .iter()
        .filter(|song| {
            // Key filter - case-insensitive exact match
            if let Some(k) = key {
                if !song.key.as_ref().map_or(false, |sk| sk.eq_ignore_ascii_case(k)) {
                    return false;
                }
            }
            
            // Rhythm filter - case-insensitive partial match
            if let Some(r) = rhythm {
                if !song.rhythm.as_ref().map_or(false, |sr| sr.to_lowercase().contains(&r.to_lowercase())) {
                    return false;
                }
            }
            
            // Time signature filter - exact match
            if let Some(t) = time {
                if !song.time_signature.as_ref().map_or(false, |st| st == t) {
                    return false;
                }
            }
            
            // Composer filter - case-insensitive partial match
            if let Some(c) = composer {
                if !song.composer.as_ref().map_or(false, |sc| sc.to_lowercase().contains(&c.to_lowercase())) {
                    return false;
                }
            }
            
            true
        })
        .collect()
}