#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Autonomous Environment Scanner & Skill Generator
Scans workspace tools, scripts, and repetitive processes, automatically generating
standardized SKILL.md bundles and background launchd/cron automation descriptors.
"""

import os
from pathlib import Path
from typing import Dict, Any, List

import xml.sax.saxutils

class AutonomousAutomator:
    """Discovers repetitive workflows and scaffolds ready-to-run SKILL.md bundles."""

    def __init__(self, vault_skills_dir: Path):
        self.vault_skills_dir = Path(vault_skills_dir)
        self.vault_skills_dir.mkdir(parents=True, exist_ok=True)

    def scan_and_generate_skills(self, scan_directory: str) -> List[Dict[str, Any]]:
        """Scans directory for automatable scripts and packages, turning them into skills."""
        scan_path = Path(scan_directory)
        discovered = []

        if not scan_path.exists():
            return discovered

        # Scan for common automation candidates (python scripts, shell scripts, bun/node scripts)
        for root, dirs, files in os.walk(scan_path):
            # Avoid node_modules, .git, venv
            dirs[:] = [d for d in dirs if d not in [".git", "node_modules", ".venv", "venv", "__pycache__"]]
            
            for file in files:
                fpath = Path(root) / file
                if file.endswith((".sh", ".py", ".ts")) and not file.startswith("__"):
                    skill_meta = self._create_skill_for_script(fpath)
                    if skill_meta:
                        discovered.append(skill_meta)

        return discovered

    def _create_skill_for_script(self, script_path: Path) -> Dict[str, Any]:
        """Scaffolds a clean SKILL.md bundle for a discovered script."""
        name = script_path.stem.lower().replace("_", "-")
        skill_dir = self.vault_skills_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        skill_file = skill_dir / "SKILL.md"
        ext = script_path.suffix

        runner = "python3" if ext == ".py" else ("bun run" if ext == ".ts" else "bash")

        content = f"""---
name: {name}
description: "Autonomous skill auto-generated from {script_path.name}."
version: 1.0.0
---

# {name.replace('-', ' ').title()} Automation

## Purpose
Automates execution of `{script_path.name}` within the secure brain vault sandbox.

## CLI Execution
```bash
{runner} {script_path.resolve()}
```

## Directives
- Always run through the security gate before execution.
- Maintain exit 0 verification on completion.
"""
        skill_file.write_text(content)
        return {
            "name": name,
            "script": str(script_path),
            "skill_path": str(skill_file)
        }

    def generate_launchd_plist(self, job_name: str, script_cmd: str, interval_seconds: int = 3600) -> str:
        """Generates a macOS LaunchAgent plist descriptor for background scheduling with XML escaping."""
        escaped_job = xml.sax.saxutils.escape(job_name, entities={'"': "&quot;", "'": "&apos;"})
        escaped_cmd = xml.sax.saxutils.escape(script_cmd, entities={'"': "&quot;", "'": "&apos;"})
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>io.dagmas.{escaped_job}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>{escaped_cmd}</string>
    </array>
    <key>StartInterval</key>
    <integer>{interval_seconds}</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        skills_dir = Path(td) / "skills"
        automator = AutonomousAutomator(skills_dir)
        # Create a dummy script
        test_script = Path(td) / "backup_sync.sh"
        test_script.write_text("#!/bin/bash\necho 'Syncing'")
        res = automator.scan_and_generate_skills(td)
        print("Generated Skills:", res)
