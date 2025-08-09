# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Note
**Only work with these core files/directories:**
- `src/` - Rust source code
- `JazzStandards.json` - Main consolidated database
- `JazzStandards/` - Individual song JSON files

**Ignore all other files and directories** including README.md, scraper files, and other output directories.

## Development Commands

### Rust Commands
- `cargo check` - Validate Rust code compilation
- `cargo build` - Build the project
- `cargo run` - Execute the main Rust application
- `cargo test` - Run tests (currently no tests defined)

### Justfile Commands
- `just build` - Build debug version
- `just build-release` - Build optimized release version
- `just install` - Install to system (requires sudo)
- `just clean` - Clean build artifacts
- `just info` - Show binary information and database stats

## Project Architecture

### Core Purpose
This project manages a jazz standards database with detailed chord progression data stored in JSON format.

### Data Structure

#### Rust Data Model (`src/main.rs`)
The Rust code defines the core data structures:

```rust
struct Song {
    title: String,
    composer: Option<String>,
    key: Option<String>,
    rhythm: Option<String>,
    time_signature: Option<String>,
    sections: Option<Vec<Section>>,
}

struct Section {
    label: Option<String>,
    repeats: Option<u32>,
    main_segment: Option<Segment>,
}

struct Segment {
    chords: Option<String>,
}
```

#### JSON Data Format
The actual JSON data follows a slightly different structure with PascalCase naming:
- **Title**: Song name
- **Composer**: Primary composer
- **Key**: Musical key
- **Rhythm**: Tempo and feel (e.g., "Medium Swing", "Medium Up Swing")
- **TimeSignature**: Time signature (e.g., "4/4")
- **Sections**: Array of song sections with:
  - **Label**: Section identifier (A, B, etc.)
  - **MainSegment**: Contains chord progressions
    - **Chords**: Chord sequence as pipe-separated string
  - **Endings**: Alternative endings for sections

### Directory Structure
- `src/` - Rust source code organized into modules
  - `main.rs` - Application entry point and command handlers
  - `lib.rs` - Library module exports and documentation
  - `models.rs` - Data structures (Song, Section, Segment)
  - `database.rs` - Database loading with embedded JSON
  - `search.rs` - Search and filtering functionality
  - `display.rs` - Output formatting and display functions
  - `stats.rs` - Statistical analysis functions
  - `cli.rs` - Command-line interface definitions
- `JazzStandards.json` - Main consolidated database (embedded at compile time)
- `JazzStandards/` - Individual song JSON files

### Code Architecture
- **Modular Design**: Code is organized into logical modules for maintainability
- **Library Structure**: Core functionality is in a library crate, binary uses it
- **Embedded Database**: JSON data is compiled into the binary using `include_str!`
- **CLI Framework**: Uses clap for robust command-line argument parsing
- **Self-Contained**: No external file dependencies at runtime

### Data Storage Architecture
- **Embedded Data**: Database is included in binary at compile time (no file I/O)
- **Individual Files**: Each song has its own JSON file in `JazzStandards/` directory
- **Consolidated Database**: `JazzStandards.json` contains all songs in a single array
- **Chord Notation**: Chords are stored as pipe-separated strings (e.g., "Fmaj7,Ab7|Dbmaj7,E7")

### Current Implementation Status
The application is fully functional with comprehensive CLI interface, search capabilities, statistical analysis, and detailed song display with chord progressions. The code is well-modularized and documented.