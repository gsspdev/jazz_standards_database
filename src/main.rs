use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::error::Error;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Song {
    pub title: String,
    pub composer: Option<String>,
    pub key: Option<String>,
    pub rhythm: Option<String>,
    pub time_signature: Option<String>,
    pub sections: Option<Vec<Section>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Section {
    pub label: Option<String>,
    pub repeats: Option<u32>,
    pub main_segment: Option<Segment>,
    pub endings: Option<Vec<Segment>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Segment {
    pub chords: Option<String>,
}

#[derive(Parser)]
#[command(name = "jazz-db")]
#[command(about = "A CLI tool for searching and analyzing the Jazz Standards database")]
#[command(long_about = "
A comprehensive CLI tool for exploring the Jazz Standards database containing 1,382 songs.
Search by title/composer, filter by musical criteria, view detailed chord progressions, 
and analyze database statistics.

Examples:
  jazz-db search \"miles davis\"
  jazz-db filter --key C --rhythm swing
  jazz-db show \"All Blues\"
  jazz-db stats --detailed
")]
#[command(version)]
pub struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Search songs by title or composer (partial matching)
    #[command(long_about = "Search for songs by title or composer name using partial matching.
    
Examples:
  jazz-db search \"miles\"          # Find all songs by Miles Davis
  jazz-db search \"blue\"           # Find songs with 'blue' in title
  jazz-db search \"monk\" --detailed # Show chord progressions")]
    Search {
        /// Search term (searches both title and composer)
        term: String,
        /// Show detailed information including chord progressions
        #[arg(short, long, help = "Include full song structure and chord progressions")]
        detailed: bool,
    },
    /// Filter songs by musical criteria
    #[command(long_about = "Filter the database by specific musical criteria.
    
Examples:
  jazz-db filter --key C                    # All songs in C major
  jazz-db filter --rhythm \"bossa nova\"      # All bossa nova songs  
  jazz-db filter --composer \"thelonious\"    # All Monk compositions
  jazz-db filter --key F --rhythm swing     # F major swing songs")]
    Filter {
        /// Filter by key (e.g., "C", "Am", "F#")
        #[arg(short, long, help = "Musical key (use 'jazz-db list keys' to see options)")]
        key: Option<String>,
        /// Filter by rhythm/style (e.g., "Swing", "Bossa Nova")
        #[arg(short, long, help = "Rhythm/style (use 'jazz-db list rhythms' to see options)")]
        rhythm: Option<String>,
        /// Filter by time signature (e.g., "4/4", "3/4")
        #[arg(short, long, help = "Time signature (use 'jazz-db list time' to see options)")]
        time: Option<String>,
        /// Filter by composer name (partial matching)
        #[arg(short, long, help = "Composer name (partial matching allowed)")]
        composer: Option<String>,
        /// Show detailed information including chord progressions
        #[arg(short, long, help = "Include full song structure and chord progressions")]
        detailed: bool,
    },
    /// Show database statistics and analysis
    #[command(long_about = "Display comprehensive statistics about the jazz standards database.
    
Examples:
  jazz-db stats            # Basic statistics
  jazz-db stats --detailed # Top composers, keys, rhythms")]
    Stats {
        /// Show detailed breakdown by category
        #[arg(short, long, help = "Show top 10 lists for keys, rhythms, and composers")]
        detailed: bool,
    },
    /// List all unique values for a specific field
    #[command(long_about = "List all unique values for database fields.
    
Examples:
  jazz-db list keys            # All available keys
  jazz-db list rhythms         # All rhythm styles  
  jazz-db list composers       # All composer names
  jazz-db list time-signatures # All time signatures")]
    List {
        /// Field to list: keys, rhythms, composers, time-signatures
        #[arg(help = "Field to list", value_parser = ["keys", "rhythms", "composers", "time-signatures", "time"])]
        field: String,
    },
    /// Show detailed information about a specific song
    #[command(long_about = "Display complete information about a specific song including chord progressions.
    
Examples:
  jazz-db show \"All Blues\"
  jazz-db show \"Giant Steps\"  
  jazz-db show \"Body and Soul\"")]
    Show {
        /// Exact song title (case-insensitive)
        #[arg(help = "Song title (use quotes for multi-word titles)")]
        title: String,
    },
}

fn load_jazz_standards() -> Result<Vec<Song>, Box<dyn Error>> {
    // Embed the JSON data directly into the binary at compile time
    // This makes the CLI tool completely self-contained with no external dependencies
    let json_content = include_str!("../JazzStandards.json");
    let songs: Vec<Song> = serde_json::from_str(json_content)?;
    Ok(songs)
}

fn search_songs<'a>(songs: &'a [Song], term: &str) -> Vec<&'a Song> {
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

fn filter_songs<'a>(songs: &'a [Song], key: Option<&str>, rhythm: Option<&str>, time: Option<&str>, composer: Option<&str>) -> Vec<&'a Song> {
    songs
        .iter()
        .filter(|song| {
            if let Some(k) = key {
                if !song.key.as_ref().map_or(false, |sk| sk.eq_ignore_ascii_case(k)) {
                    return false;
                }
            }
            if let Some(r) = rhythm {
                if !song.rhythm.as_ref().map_or(false, |sr| sr.to_lowercase().contains(&r.to_lowercase())) {
                    return false;
                }
            }
            if let Some(t) = time {
                if !song.time_signature.as_ref().map_or(false, |st| st == t) {
                    return false;
                }
            }
            if let Some(c) = composer {
                if !song.composer.as_ref().map_or(false, |sc| sc.to_lowercase().contains(&c.to_lowercase())) {
                    return false;
                }
            }
            true
        })
        .collect()
}

fn print_song_summary(song: &Song) {
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

fn print_song_detailed(song: &Song) {
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
            if let Some(label) = &section.label {
                print!("  Section {}", label);
                if let Some(repeats) = section.repeats {
                    print!(" (repeats: {})", repeats);
                }
                println!();
            } else {
                println!("  Section {}", i + 1);
            }
            
            if let Some(main_seg) = &section.main_segment {
                if let Some(chords) = &main_seg.chords {
                    println!("    🎼 Main: {}", chords);
                }
            }
            
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

fn show_statistics(songs: &[Song], detailed: bool) {
    println!("\n📊 Jazz Standards Database Statistics");
    println!("════════════════════════════════════════");
    println!("Total songs: {}", songs.len());

    let songs_with_composers = songs.iter().filter(|s| s.composer.is_some()).count();
    let songs_with_keys = songs.iter().filter(|s| s.key.is_some()).count();
    let songs_with_rhythms = songs.iter().filter(|s| s.rhythm.is_some()).count();
    let songs_with_time_sigs = songs.iter().filter(|s| s.time_signature.is_some()).count();
    let songs_with_sections = songs.iter().filter(|s| s.sections.is_some()).count();

    println!("Songs with composers: {}/{} ({:.1}%)", 
        songs_with_composers, songs.len(), 
        songs_with_composers as f64 / songs.len() as f64 * 100.0);
    println!("Songs with keys: {}/{} ({:.1}%)", 
        songs_with_keys, songs.len(),
        songs_with_keys as f64 / songs.len() as f64 * 100.0);
    println!("Songs with rhythms: {}/{} ({:.1}%)", 
        songs_with_rhythms, songs.len(),
        songs_with_rhythms as f64 / songs.len() as f64 * 100.0);
    println!("Songs with time signatures: {}/{} ({:.1}%)", 
        songs_with_time_sigs, songs.len(),
        songs_with_time_sigs as f64 / songs.len() as f64 * 100.0);
    println!("Songs with sections: {}/{} ({:.1}%)", 
        songs_with_sections, songs.len(),
        songs_with_sections as f64 / songs.len() as f64 * 100.0);

    if detailed {
        show_detailed_statistics(songs);
    }
}

fn show_detailed_statistics(songs: &[Song]) {
    println!("\n🎹 Key Distribution:");
    println!("──────────────────");
    let mut key_counts = HashMap::new();
    for song in songs {
        if let Some(key) = &song.key {
            *key_counts.entry(key.clone()).or_insert(0) += 1;
        }
    }
    let mut key_vec: Vec<_> = key_counts.iter().collect();
    key_vec.sort_by(|a, b| b.1.cmp(a.1));
    for (key, count) in key_vec.iter().take(10) {
        println!("  {:<6}: {:>4} songs", key, count);
    }

    println!("\n🎤 Rhythm Distribution:");
    println!("─────────────────────");
    let mut rhythm_counts = HashMap::new();
    for song in songs {
        if let Some(rhythm) = &song.rhythm {
            *rhythm_counts.entry(rhythm.clone()).or_insert(0) += 1;
        }
    }
    let mut rhythm_vec: Vec<_> = rhythm_counts.iter().collect();
    rhythm_vec.sort_by(|a, b| b.1.cmp(a.1));
    for (rhythm, count) in rhythm_vec.iter().take(10) {
        println!("  {:<20}: {:>4} songs", rhythm, count);
    }

    println!("\n🎵 Top Composers:");
    println!("───────────────");
    let mut composer_counts = HashMap::new();
    for song in songs {
        if let Some(composer) = &song.composer {
            *composer_counts.entry(composer.clone()).or_insert(0) += 1;
        }
    }
    let mut composer_vec: Vec<_> = composer_counts.iter().collect();
    composer_vec.sort_by(|a, b| b.1.cmp(a.1));
    for (composer, count) in composer_vec.iter().take(10) {
        println!("  {:<25}: {:>4} songs", composer, count);
    }
}

fn list_field_values(songs: &[Song], field: &str) {
    match field.to_lowercase().as_str() {
        "keys" | "key" => {
            let mut keys: Vec<_> = songs
                .iter()
                .filter_map(|s| s.key.as_ref())
                .collect::<std::collections::HashSet<_>>()
                .into_iter()
                .collect();
            keys.sort();
            println!("🎹 Available Keys ({}):", keys.len());
            for key in keys {
                println!("  {}", key);
            }
        }
        "rhythms" | "rhythm" => {
            let mut rhythms: Vec<_> = songs
                .iter()
                .filter_map(|s| s.rhythm.as_ref())
                .collect::<std::collections::HashSet<_>>()
                .into_iter()
                .collect();
            rhythms.sort();
            println!("🎤 Available Rhythms ({}):", rhythms.len());
            for rhythm in rhythms {
                println!("  {}", rhythm);
            }
        }
        "composers" | "composer" => {
            let mut composers: Vec<_> = songs
                .iter()
                .filter_map(|s| s.composer.as_ref())
                .collect::<std::collections::HashSet<_>>()
                .into_iter()
                .collect();
            composers.sort();
            println!("🎵 Available Composers ({}):", composers.len());
            for composer in composers {
                println!("  {}", composer);
            }
        }
        "time-signatures" | "time" => {
            let mut time_sigs: Vec<_> = songs
                .iter()
                .filter_map(|s| s.time_signature.as_ref())
                .collect::<std::collections::HashSet<_>>()
                .into_iter()
                .collect();
            time_sigs.sort();
            println!("⏱️  Available Time Signatures ({}):", time_sigs.len());
            for time_sig in time_sigs {
                println!("  {}", time_sig);
            }
        }
        _ => {
            println!("❌ Unknown field '{}'. Available fields: keys, rhythms, composers, time-signatures", field);
        }
    }
}

fn main() {
    let cli = Cli::parse();

    let songs = match load_jazz_standards() {
        Ok(songs) => songs,
        Err(e) => {
            eprintln!("❌ Error loading jazz standards database: {}", e);
            std::process::exit(1);
        }
    };

    match cli.command {
        Commands::Search { term, detailed } => {
            let results = search_songs(&songs, &term);
            if results.is_empty() {
                println!("🔍 No songs found matching '{}'", term);
            } else {
                println!("🔍 Found {} song(s) matching '{}':", results.len(), term);
                println!("───────────────────────────────────────");
                for song in results {
                    if detailed {
                        print_song_detailed(song);
                    } else {
                        print_song_summary(song);
                        println!();
                    }
                }
            }
        }
        Commands::Filter { key, rhythm, time, composer, detailed } => {
            let results = filter_songs(&songs, key.as_deref(), rhythm.as_deref(), time.as_deref(), composer.as_deref());
            if results.is_empty() {
                println!("🔍 No songs found matching the filter criteria");
            } else {
                println!("🔍 Found {} song(s) matching filter criteria:", results.len());
                println!("───────────────────────────────────────");
                for song in results {
                    if detailed {
                        print_song_detailed(song);
                    } else {
                        print_song_summary(song);
                        println!();
                    }
                }
            }
        }
        Commands::Stats { detailed } => {
            show_statistics(&songs, detailed);
        }
        Commands::List { field } => {
            list_field_values(&songs, &field);
        }
        Commands::Show { title } => {
            if let Some(song) = songs.iter().find(|s| s.title.eq_ignore_ascii_case(&title)) {
                print_song_detailed(song);
            } else {
                println!("❌ Song '{}' not found", title);
                println!("💡 Try using 'jazz-db search \"{}\"' for partial matches", title);
            }
        }
    }
}
