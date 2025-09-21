# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dnuos is a console program that creates lists of music collections based on directory structure. It supports MP3, AAC, Musepack, Ogg Vorbis, and FLAC audio files, with quality profile detection including LAME preset information.

## Key Commands

### Build and Installation
```bash
# Build the project
python setup.py build

# Install locally
sudo python setup.py install

# Alternative: Using make
make build
make install

# Clean build artifacts
make clean
```

### Testing
```bash
# Run the test suite (requires testdata.zip in project root)
python setup.py test

# Test data can be downloaded from:
# https://bitheap.org/dnuos/files/testdata.zip
```

### Development Commands
```bash
# Build translations (.mo files from .po files)
python setup.py build_mo

# Run dnuos after installation
dnuos --help
dnuos [directory_path]
```

## Architecture Overview

The codebase is organized as a Python package with the following structure:

- **dnuos/** - Main package containing core functionality
  - **audiotype.py** - Audio file type detection and metadata extraction (MP3, FLAC, Ogg, etc.)
  - **audiodir.py** - Directory scanning and audio file collection logic
  - **conf.py** - Configuration and command-line argument parsing
  - **cache/** - SQLite-based caching system for audio metadata (Python 2.5+)
  - **id3/** - ID3 tag reading implementation
  - **output/** - Output formatters (plain text, HTML)
  - **locale/** - Internationalization support (French translation available)

- **dnuostests/** - Test suite using doctest framework
  - Individual test modules for different features (cache, tags, formats, etc.)

## Important Technical Details

- **Python Compatibility**: Originally written for Python 2, requires updates for Python 3 compatibility
- **Caching**: Uses SQLite for caching when available (Python 2.5+), falls back to simpler cache format otherwise
- **Cache Location**: Linux uses `~/.cache/dnuos` (`$XDG_CACHE_HOME/dnuos`)
- **Character Encoding**: Handles Unicode file paths and supports terminal's preferred encoding for output
- **Testing**: Uses doctest framework; test data must be downloaded separately
- **Quality Detection**: Includes sophisticated MP3 quality preset detection for LAME and other encoders