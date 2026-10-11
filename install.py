#!/usr/bin/env python3
"""
DAGMAS Brain Vault - One-Click CLI Skill & MCP Installer
Usage:
    python3 install.py
    python3 install.py --verify-only
    python3 install.py --uninstall
"""

import sys
from pathlib import Path

# Add repo root to sys.path
repo_root = Path(__file__).resolve().parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.installer import main

if __name__ == "__main__":
    sys.exit(main())
