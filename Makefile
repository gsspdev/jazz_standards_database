# Jazz Standards Database CLI - Build and Distribution Makefile

.PHONY: help build build-release clean install uninstall package-deb package-rpm test-install

# Configuration
BINARY_NAME = jazz-db
VERSION = 1.0.0
INSTALL_PATH = /usr/local/bin
DEB_ARCH = amd64

# Default target
help:
	@echo "🎵 Jazz Standards Database CLI - Build System"
	@echo "============================================="
	@echo ""
	@echo "Available targets:"
	@echo "  build          - Build debug version"
	@echo "  build-release  - Build optimized release version"
	@echo "  install        - Install to system (requires sudo)"
	@echo "  uninstall      - Remove from system (requires sudo)"
	@echo "  clean          - Clean build artifacts"
	@echo "  package-deb    - Create Debian package (Linux)"
	@echo "  package-rpm    - Create RPM package (Linux)"
	@echo "  test-install   - Test installation script"
	@echo ""

# Build targets
build:
	@echo "🔨 Building debug version..."
	cargo build

build-release:
	@echo "🔨 Building release version..."
	cargo build --release
	@echo "✅ Binary created: target/release/$(BINARY_NAME)"
	@ls -lh target/release/$(BINARY_NAME)

# Installation targets
install: build-release
	@echo "📦 Installing $(BINARY_NAME) to $(INSTALL_PATH)..."
	sudo cp target/release/$(BINARY_NAME) $(INSTALL_PATH)/
	sudo chmod +x $(INSTALL_PATH)/$(BINARY_NAME)
	@echo "✅ Installation complete!"
	@echo "Try: $(BINARY_NAME) --help"

uninstall:
	@echo "🗑️  Removing $(BINARY_NAME) from $(INSTALL_PATH)..."
	sudo rm -f $(INSTALL_PATH)/$(BINARY_NAME)
	@echo "✅ Uninstallation complete!"

# Package creation (Linux)
package-deb: build-release
	@echo "📦 Creating Debian package..."
	@mkdir -p dist/deb/DEBIAN
	@mkdir -p dist/deb/usr/local/bin
	@mkdir -p dist/deb/usr/share/doc/$(BINARY_NAME)
	
	# Copy binary
	@cp target/release/$(BINARY_NAME) dist/deb/usr/local/bin/
	
	# Create control file
	@echo "Package: $(BINARY_NAME)" > dist/deb/DEBIAN/control
	@echo "Version: $(VERSION)" >> dist/deb/DEBIAN/control
	@echo "Section: utils" >> dist/deb/DEBIAN/control
	@echo "Priority: optional" >> dist/deb/DEBIAN/control
	@echo "Architecture: $(DEB_ARCH)" >> dist/deb/DEBIAN/control
	@echo "Maintainer: Jazz Database Team <team@example.com>" >> dist/deb/DEBIAN/control
	@echo "Description: CLI tool for searching and analyzing jazz standards" >> dist/deb/DEBIAN/control
	@echo " A comprehensive command-line interface for exploring a database" >> dist/deb/DEBIAN/control
	@echo " of 1,382 jazz standards with full chord progressions." >> dist/deb/DEBIAN/control
	
	# Create copyright file
	@echo "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/" > dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	@echo "Upstream-Name: $(BINARY_NAME)" >> dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	@echo "Source: https://github.com/user/jazz-db" >> dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	@echo "" >> dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	@echo "Files: *" >> dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	@echo "Copyright: 2024 Jazz Database Team" >> dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	@echo "License: MIT" >> dist/deb/usr/share/doc/$(BINARY_NAME)/copyright
	
	# Build package
	@dpkg-deb --build dist/deb dist/$(BINARY_NAME)_$(VERSION)_$(DEB_ARCH).deb
	@echo "✅ Debian package created: dist/$(BINARY_NAME)_$(VERSION)_$(DEB_ARCH).deb"

package-rpm: build-release
	@echo "📦 Creating RPM package..."
	@echo "⚠️  RPM packaging requires rpmbuild to be installed"
	@mkdir -p dist/rpm/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	
	# Create spec file
	@echo "Name: $(BINARY_NAME)" > dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "Version: $(VERSION)" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "Release: 1%{?dist}" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "Summary: CLI tool for searching and analyzing jazz standards" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "License: MIT" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "URL: https://github.com/user/jazz-db" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "Source0: %{name}-%{version}.tar.gz" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "%description" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "A comprehensive command-line interface for exploring a database" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "of 1,382 jazz standards with full chord progressions." >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "%install" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "mkdir -p %{buildroot}/usr/local/bin" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "cp %{_builddir}/$(BINARY_NAME) %{buildroot}/usr/local/bin/" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "%files" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	@echo "/usr/local/bin/$(BINARY_NAME)" >> dist/rpm/SPECS/$(BINARY_NAME).spec
	
	@cp target/release/$(BINARY_NAME) dist/rpm/BUILD/
	@echo "✅ RPM spec created. Run 'rpmbuild -bb dist/rpm/SPECS/$(BINARY_NAME).spec' to build"

# Testing
test-install:
	@echo "🧪 Testing installation script..."
	@./install.sh

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	cargo clean
	rm -rf dist/
	@echo "✅ Clean complete!"

# Show binary info
info: build-release
	@echo "📊 Binary Information:"
	@echo "======================"
	@echo "Path: target/release/$(BINARY_NAME)"
	@file target/release/$(BINARY_NAME)
	@echo "Size: $$(du -h target/release/$(BINARY_NAME) | cut -f1)"
	@echo "Version: $$(target/release/$(BINARY_NAME) --version)"
	@echo ""
	@echo "Database Statistics:"
	@target/release/$(BINARY_NAME) stats