#!/bin/bash

# Jazz Standards Database CLI Installer
# Supports macOS and Linux

set -e

REPO_URL="https://github.com/user/jazz-db"  # Update with actual repo
VERSION="1.0.0"
BINARY_NAME="jazz-db"
INSTALL_DIR="/usr/local/bin"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}🎵 Jazz Standards Database CLI Installer${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Detect OS and architecture
detect_system() {
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    case $OS in
        Darwin)
            OS="macos"
            ;;
        Linux)
            OS="linux"
            ;;
        *)
            print_error "Unsupported operating system: $OS"
            exit 1
            ;;
    esac
    
    case $ARCH in
        x86_64|amd64)
            ARCH="x86_64"
            ;;
        aarch64|arm64)
            ARCH="aarch64"
            ;;
        *)
            print_error "Unsupported architecture: $ARCH"
            exit 1
            ;;
    esac
    
    print_info "Detected system: $OS-$ARCH"
}

# Check if running as root for system-wide install
check_permissions() {
    if [[ $EUID -ne 0 ]] && [[ -w "$INSTALL_DIR" ]]; then
        print_info "Installing to $INSTALL_DIR"
    elif [[ $EUID -ne 0 ]]; then
        print_warning "System-wide installation requires sudo privileges"
        print_info "You may be prompted for your password"
        SUDO="sudo"
    else
        print_info "Installing to $INSTALL_DIR as root"
    fi
}

# Check if Homebrew is available (macOS)
check_homebrew() {
    if command -v brew &> /dev/null && [[ "$OS" == "macos" ]]; then
        echo
        read -p "$(echo -e ${YELLOW}🍺 Homebrew detected. Install via Homebrew instead? [y/N]: ${NC})" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_homebrew
            exit 0
        fi
    fi
}

# Install via Homebrew
install_homebrew() {
    print_info "Installing via Homebrew..."
    # Note: This would require publishing the formula to a tap
    print_warning "Homebrew formula not yet available. Using direct installation."
    install_direct
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
        print_error "Either curl or wget is required for installation"
        exit 1
    fi
    
    if command -v curl &> /dev/null; then
        DOWNLOADER="curl"
        DOWNLOAD_CMD="curl -fsSL"
    else
        DOWNLOADER="wget"
        DOWNLOAD_CMD="wget -qO-"
    fi
    
    print_success "Found $DOWNLOADER for downloading"
}

# Download and install binary
install_direct() {
    print_info "Installing Jazz DB CLI..."
    
    # For now, since we don't have releases, we'll use the local binary
    # In a real scenario, this would download from GitHub releases
    
    BINARY_URL="${REPO_URL}/releases/download/v${VERSION}/${BINARY_NAME}-${OS}-${ARCH}"
    TEMP_FILE="/tmp/${BINARY_NAME}"
    
    print_info "This installer would download from: $BINARY_URL"
    print_warning "For this demo, copying local binary instead"
    
    # Copy the local binary (for demo purposes)
    if [[ -f "target/release/jazz-db" ]]; then
        cp "target/release/jazz-db" "$TEMP_FILE"
        print_success "Binary prepared for installation"
    else
        print_error "Local binary not found. Please run 'cargo build --release' first."
        exit 1
    fi
    
    # Install binary
    print_info "Installing binary to $INSTALL_DIR..."
    $SUDO chmod +x "$TEMP_FILE"
    $SUDO mv "$TEMP_FILE" "$INSTALL_DIR/$BINARY_NAME"
    
    print_success "Binary installed to $INSTALL_DIR/$BINARY_NAME"
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    if command -v "$BINARY_NAME" &> /dev/null; then
        VERSION_OUTPUT=$($BINARY_NAME --version 2>&1)
        print_success "Installation successful!"
        print_info "Installed version: $VERSION_OUTPUT"
    else
        print_error "Installation failed. Binary not found in PATH."
        print_info "You may need to add $INSTALL_DIR to your PATH"
        exit 1
    fi
}

# Show usage examples
show_usage() {
    echo
    echo -e "${GREEN}🎵 Jazz DB is now installed!${NC}"
    echo
    echo -e "${BLUE}Try these commands:${NC}"
    echo "  jazz-db --help                    # Show all available commands"
    echo "  jazz-db stats                     # Database statistics"
    echo "  jazz-db search \"miles davis\"      # Search for songs"
    echo "  jazz-db filter --key C            # Filter by key"
    echo "  jazz-db show \"All Blues\"          # Show song details"
    echo
    echo -e "${BLUE}Database contains 1,382 jazz standards with full chord progressions!${NC}"
    echo
}

# Main installation flow
main() {
    print_header
    
    detect_system
    check_permissions
    check_homebrew
    check_dependencies
    install_direct
    verify_installation
    show_usage
    
    print_success "Installation complete! 🎉"
}

# Handle interruption
trap 'print_error "Installation interrupted"; exit 1' INT TERM

# Run main installation
main "$@"