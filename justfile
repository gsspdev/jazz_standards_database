# Jazz Standards Database CLI - Build and Distribution Justfile

# Configuration
binary_name := "jazz-db"
version := "1.0.0"
install_path := "/usr/local/bin"
deb_arch := "amd64"

# Default recipe shows help
default:
    @echo "🎵 Jazz Standards Database CLI - Build System"
    @echo "============================================="
    @echo ""
    @echo "Available recipes:"
    @echo "  build          - Build debug version"
    @echo "  build-release  - Build optimized release version" 
    @echo "  install        - Install to system (requires sudo)"
    @echo "  uninstall      - Remove from system (requires sudo)"
    @echo "  clean          - Clean build artifacts"
    @echo "  package-deb    - Create Debian package (Linux)"
    @echo "  package-rpm    - Create RPM package (Linux)"
    @echo "  info           - Show binary information"
    @echo ""

# Build debug version
build:
    @echo "🔨 Building debug version..."
    cargo build

# Build optimized release version
build-release:
    @echo "🔨 Building release version..."
    cargo build --release
    @echo "✅ Binary created: target/release/{{binary_name}}"
    @ls -lh target/release/{{binary_name}}

# Install to system
install: build-release
    @echo "📦 Installing {{binary_name}} to {{install_path}}..."
    sudo cp target/release/{{binary_name}} {{install_path}}/
    sudo chmod +x {{install_path}}/{{binary_name}}
    @echo "✅ Installation complete!"
    @echo "Try: {{binary_name}} --help"

# Remove from system
uninstall:
    @echo "🗑️  Removing {{binary_name}} from {{install_path}}..."
    sudo rm -f {{install_path}}/{{binary_name}}
    @echo "✅ Uninstallation complete!"

# Create Debian package
package-deb: build-release
    @echo "📦 Creating Debian package..."
    mkdir -p dist/deb/DEBIAN
    mkdir -p dist/deb/usr/local/bin
    mkdir -p dist/deb/usr/share/doc/{{binary_name}}
    
    # Copy binary
    cp target/release/{{binary_name}} dist/deb/usr/local/bin/
    
    # Create control file
    echo "Package: {{binary_name}}" > dist/deb/DEBIAN/control
    echo "Version: {{version}}" >> dist/deb/DEBIAN/control
    echo "Section: utils" >> dist/deb/DEBIAN/control
    echo "Priority: optional" >> dist/deb/DEBIAN/control
    echo "Architecture: {{deb_arch}}" >> dist/deb/DEBIAN/control
    echo "Maintainer: Jazz Database Team <team@example.com>" >> dist/deb/DEBIAN/control
    echo "Description: CLI tool for searching and analyzing jazz standards" >> dist/deb/DEBIAN/control
    echo " A comprehensive command-line interface for exploring a database" >> dist/deb/DEBIAN/control
    echo " of 1,382 jazz standards with full chord progressions." >> dist/deb/DEBIAN/control
    
    # Create copyright file
    echo "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/" > dist/deb/usr/share/doc/{{binary_name}}/copyright
    echo "Upstream-Name: {{binary_name}}" >> dist/deb/usr/share/doc/{{binary_name}}/copyright
    echo "Source: https://github.com/user/jazz-db" >> dist/deb/usr/share/doc/{{binary_name}}/copyright
    echo "" >> dist/deb/usr/share/doc/{{binary_name}}/copyright
    echo "Files: *" >> dist/deb/usr/share/doc/{{binary_name}}/copyright
    echo "Copyright: 2024 Jazz Database Team" >> dist/deb/usr/share/doc/{{binary_name}}/copyright
    echo "License: MIT" >> dist/deb/usr/share/doc/{{binary_name}}/copyright
    
    # Build package
    dpkg-deb --build dist/deb dist/{{binary_name}}_{{version}}_{{deb_arch}}.deb
    @echo "✅ Debian package created: dist/{{binary_name}}_{{version}}_{{deb_arch}}.deb"

# Create RPM package
package-rpm: build-release
    @echo "📦 Creating RPM package..."
    @echo "⚠️  RPM packaging requires rpmbuild to be installed"
    mkdir -p dist/rpm/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    
    # Create spec file
    echo "Name: {{binary_name}}" > dist/rpm/SPECS/{{binary_name}}.spec
    echo "Version: {{version}}" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "Release: 1%{?dist}" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "Summary: CLI tool for searching and analyzing jazz standards" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "License: MIT" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "URL: https://github.com/user/jazz-db" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "Source0: %{name}-%{version}.tar.gz" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "%description" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "A comprehensive command-line interface for exploring a database" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "of 1,382 jazz standards with full chord progressions." >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "%install" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "mkdir -p %{buildroot}/usr/local/bin" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "cp %{_builddir}/{{binary_name}} %{buildroot}/usr/local/bin/" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "%files" >> dist/rpm/SPECS/{{binary_name}}.spec
    echo "/usr/local/bin/{{binary_name}}" >> dist/rpm/SPECS/{{binary_name}}.spec
    
    cp target/release/{{binary_name}} dist/rpm/BUILD/
    @echo "✅ RPM spec created. Run 'rpmbuild -bb dist/rpm/SPECS/{{binary_name}}.spec' to build"

# Clean build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    cargo clean
    rm -rf dist/
    @echo "✅ Clean complete!"

# Show binary information
info: build-release
    @echo "📊 Binary Information:"
    @echo "======================"
    @echo "Path: target/release/{{binary_name}}"
    @file target/release/{{binary_name}}
    @echo "Size: $(du -h target/release/{{binary_name}} | cut -f1)"
    @echo "Version: $(target/release/{{binary_name}} --version)"
    @echo ""
    @echo "Database Statistics:"
    @target/release/{{binary_name}} stats