# 🎵 Jazz Standards Database CLI - Installation Guide

Multiple installation methods are available for macOS and Linux systems.

## Quick Install (Recommended)

### One-line install script:
```bash
curl -fsSL https://raw.githubusercontent.com/user/jazz-db/main/install.sh | bash
```

or with wget:
```bash
wget -qO- https://raw.githubusercontent.com/user/jazz-db/main/install.sh | bash
```

## Installation Methods

### 1. 🍺 Homebrew (macOS)

```bash
# Add tap (once available)
brew tap user/jazz-db

# Install
brew install jazz-db

# Verify
jazz-db --version
```

### 2. 📦 Package Managers (Linux)

#### Debian/Ubuntu (.deb):
```bash
# Download package
wget https://github.com/user/jazz-db/releases/download/v1.0.0/jazz-db_1.0.0_amd64.deb

# Install
sudo dpkg -i jazz-db_1.0.0_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f
```

#### Red Hat/CentOS (.rpm):
```bash
# Download package  
wget https://github.com/user/jazz-db/releases/download/v1.0.0/jazz-db-1.0.0-1.x86_64.rpm

# Install
sudo rpm -ivh jazz-db-1.0.0-1.x86_64.rpm
```

### 3. 🔧 Manual Installation

#### Download pre-compiled binary:
```bash
# macOS (Intel)
curl -L -o jazz-db https://github.com/user/jazz-db/releases/download/v1.0.0/jazz-db-macos-x86_64

# macOS (Apple Silicon)
curl -L -o jazz-db https://github.com/user/jazz-db/releases/download/v1.0.0/jazz-db-macos-aarch64

# Linux (x86_64)
curl -L -o jazz-db https://github.com/user/jazz-db/releases/download/v1.0.0/jazz-db-linux-x86_64

# Make executable and install
chmod +x jazz-db
sudo mv jazz-db /usr/local/bin/
```

### 4. 🦀 From Source (Rust required)

```bash
# Clone repository
git clone https://github.com/user/jazz-db.git
cd jazz-db

# Build and install
just install

# Or manually with cargo
cargo build --release
sudo cp target/release/jazz-db /usr/local/bin/
```

## Verification

Test your installation:

```bash
# Check version
jazz-db --version

# View help
jazz-db --help

# Test basic functionality
jazz-db stats
jazz-db search "miles davis"
jazz-db show "All Blues"
```

## Troubleshooting

### Command not found
If you get "command not found", ensure `/usr/local/bin` is in your PATH:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export PATH="/usr/local/bin:$PATH"

# Reload your shell
source ~/.bashrc  # or ~/.zshrc
```

### Permission denied
If installation fails with permission errors:

```bash
# Ensure you have write access or use sudo
sudo just install

# Or install to user directory
cargo install --path . --root ~/.local
export PATH="$HOME/.local/bin:$PATH"
```

### Missing dependencies
The binary is self-contained and requires no runtime dependencies. If you're building from source, you need:

- Rust 1.70+ (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)

## Uninstallation

### Remove binary:
```bash
# Using justfile
just uninstall

# Or manually
sudo rm /usr/local/bin/jazz-db
```

### Package managers:
```bash
# Homebrew
brew uninstall jazz-db

# Debian/Ubuntu
sudo apt remove jazz-db

# Red Hat/CentOS
sudo rpm -e jazz-db
```

## System Requirements

- **macOS**: 10.12 Sierra or later
- **Linux**: Any modern distribution (glibc 2.17+)
- **Architecture**: x86_64 (Intel/AMD) or aarch64 (ARM64)
- **Disk Space**: ~2MB for binary + database
- **Memory**: Minimal (~10MB runtime)

## Database Information

The CLI tool includes an embedded database containing:
- **1,382 jazz standards** from The Real Book Volume I Sixth Edition
- **Full chord progressions** organized by song sections
- **Metadata**: composers, keys, rhythms, time signatures
- **No external files** required - completely self-contained

## Getting Started

After installation, try these commands:

```bash
# Explore the database
jazz-db stats --detailed

# Search for songs
jazz-db search "blue"
jazz-db search "thelonious monk"

# Filter by criteria  
jazz-db filter --key C
jazz-db filter --rhythm "bossa nova"
jazz-db filter --composer "miles davis" --detailed

# View specific songs
jazz-db show "Giant Steps"
jazz-db show "Body and Soul"

# List available options
jazz-db list keys
jazz-db list rhythms
jazz-db list composers
```

---

## Support

- **Issues**: Report bugs at https://github.com/user/jazz-db/issues
- **Documentation**: Full CLI help available with `jazz-db --help`
- **Updates**: Check for new releases at https://github.com/user/jazz-db/releases

Happy jazz exploring! 🎵