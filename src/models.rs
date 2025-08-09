//! Data models for jazz standards
//! 
//! This module contains the core data structures representing jazz standards,
//! their sections, and chord progressions.

use serde::{Deserialize, Serialize};

/// Represents a jazz standard song with metadata and chord progressions
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Song {
    /// Song title
    pub title: String,
    /// Composer(s) of the song
    pub composer: Option<String>,
    /// Musical key (e.g., "C", "Am", "F#")
    pub key: Option<String>,
    /// Rhythm style (e.g., "Medium Swing", "Bossa Nova")
    pub rhythm: Option<String>,
    /// Time signature (e.g., "4/4", "3/4")
    pub time_signature: Option<String>,
    /// Song sections with chord progressions
    pub sections: Option<Vec<Section>>,
}

/// Represents a section of a song (e.g., verse, chorus, bridge)
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Section {
    /// Section label (e.g., "A", "B", "Chorus")
    pub label: Option<String>,
    /// Number of times this section repeats
    pub repeats: Option<u32>,
    /// Main chord progression for this section
    pub main_segment: Option<Segment>,
    /// Alternative endings for this section
    pub endings: Option<Vec<Segment>>,
}

/// Represents a segment containing chord progressions
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Segment {
    /// Chord progression as a pipe-separated string
    pub chords: Option<String>,
}