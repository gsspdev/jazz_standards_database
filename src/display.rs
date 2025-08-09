//! Display and formatting functionality
//! 
//! This module provides functions for formatting and displaying song information
//! in various formats (summary and detailed views).

use crate::models::Song;

/// Print a concise summary of a song
/// 
/// Displays basic song information including title, composer, key, rhythm,
/// time signature, and section count.
/// 
/// # Arguments
/// 
/// * `song` - The song to display
/// 
/// # Examples
/// 
/// ```no_run
/// use jazz_standards_database::{load_jazz_standards, print_song_summary};
/// 
/// let songs = load_jazz_standards()?;
/// if let Some(song) = songs.first() {
///     print_song_summary(song);
/// }
/// ```
pub fn print_song_summary(song: &Song) {
    println!("📄 {}", song.title);
    
    if let Some(composer) = &song.composer {
        println!("   🎵 Composer: {}", composer);
    }
    
    if let Some(key) = &song.key {
        println!("   🎹 Key: {}", key);
    }
    
    if let Some(rhythm) = &song.rhythm {
        println!("   🎤 Rhythm: {}", rhythm);
    }
    
    if let Some(time_sig) = &song.time_signature {
        println!("   ⏱️  Time: {}", time_sig);
    }
    
    if let Some(sections) = &song.sections {
        println!("   📋 Sections: {}", sections.len());
    }
}

/// Print detailed information about a song including chord progressions
/// 
/// Displays complete song information including full chord progressions
/// for all sections, alternative endings, and repeat information.
/// 
/// # Arguments
/// 
/// * `song` - The song to display in detail
/// 
/// # Examples
/// 
/// ```no_run
/// use jazz_standards_database::{load_jazz_standards, print_song_detailed};
/// 
/// let songs = load_jazz_standards()?;
/// if let Some(song) = songs.first() {
///     print_song_detailed(song);
/// }
/// ```
pub fn print_song_detailed(song: &Song) {
    println!("\n═══════════════════════════════════════");
    println!("📄 {}", song.title);
    println!("═══════════════════════════════════════");
    
    if let Some(composer) = &song.composer {
        println!("🎵 Composer: {}", composer);
    }
    
    if let Some(key) = &song.key {
        println!("🎹 Key: {}", key);
    }
    
    if let Some(rhythm) = &song.rhythm {
        println!("🎤 Rhythm: {}", rhythm);
    }
    
    if let Some(time_sig) = &song.time_signature {
        println!("⏱️  Time Signature: {}", time_sig);
    }

    if let Some(sections) = &song.sections {
        println!("\n📋 Song Structure ({} sections):", sections.len());
        println!("───────────────────────────────────────");
        
        for (i, section) in sections.iter().enumerate() {
            // Print section header
            if let Some(label) = &section.label {
                print!("  Section {}", label);
                if let Some(repeats) = section.repeats {
                    print!(" (repeats: {})", repeats);
                }
                println!();
            } else {
                println!("  Section {}", i + 1);
            }
            
            // Print main chord progression
            if let Some(main_seg) = &section.main_segment {
                if let Some(chords) = &main_seg.chords {
                    println!("    🎼 Main: {}", chords);
                }
            }
            
            // Print alternative endings
            if let Some(endings) = &section.endings {
                for (j, ending) in endings.iter().enumerate() {
                    if let Some(chords) = &ending.chords {
                        println!("    🔚 Ending {}: {}", j + 1, chords);
                    }
                }
            }
            
            println!();
        }
    }
}