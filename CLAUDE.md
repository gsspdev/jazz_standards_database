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
- `src/main.rs` - Rust data structures and application entry point
- `JazzStandards.json` - Main consolidated database
- `JazzStandards/` - Individual song JSON files (e.g., "26-2.json", "All Blues.json")

### Data Storage Architecture
- **Individual Files**: Each song has its own JSON file in `JazzStandards/` directory
- **Consolidated Database**: `JazzStandards.json` contains all songs in a single array
- **Chord Notation**: Chords are stored as pipe-separated strings (e.g., "Fmaj7,Ab7|Dbmaj7,E7")

### Current Implementation Status
The Rust application currently only defines data structures but doesn't implement functionality to read or process the JSON files. The main function is empty except for the struct definitions.