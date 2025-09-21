#!/usr/bin/env python3
"""Build translations (.mo files from .po files) for dnuos."""

import os
import sys
from glob import glob


def compile_po_to_mo(po_file):
    """Compile a .po file to .mo file."""
    mo_file = po_file.replace('.po', '.mo')

    try:
        # Use the local msgfmt module
        import msgfmt
        msgfmt.compile_catalog(po_file)
        print(f"Compiled {po_file} -> {mo_file}")
        return True
    except Exception as e:
        print(f"Failed to compile {po_file}: {e}", file=sys.stderr)
        return False


def build_translations():
    """Build all translation files."""
    po_files = glob('./dnuos/locale/*/LC_MESSAGES/*.po')
    if not po_files:
        print("No .po files found")
        return True

    success = True
    for po_file in po_files:
        if not compile_po_to_mo(po_file):
            success = False

    return success


if __name__ == '__main__':
    sys.exit(0 if build_translations() else 1)