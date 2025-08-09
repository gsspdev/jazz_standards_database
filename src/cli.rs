//! Command-line interface definitions
//! 
//! This module defines the CLI structure, commands, and argument parsing
//! using the clap library.

use clap::{Parser, Subcommand};

/// Command-line interface for the Jazz Standards Database
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
    pub command: Commands,
}

/// Available CLI commands
#[derive(Subcommand)]
pub enum Commands {
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