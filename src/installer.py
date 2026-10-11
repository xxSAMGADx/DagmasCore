#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Autonomous CLI Skill & MCP Installer
Automates setup of the brain-vault-setup skill, global agent rules,
and Model Context Protocol (MCP) server across Claude Desktop, Cursor, and agent runtimes.
Zero external dependencies (pure Python Standard Library).
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

BANNER = """
======================================================================
  DAGMAS BRAIN VAULT // AUTONOMOUS SKILL & MCP INSTALLER
  Sovereign Intelligence Engine - Pure Python Standard Library
======================================================================
"""

class SkillInstaller:
    """Installs and configures DAGMAS Brain Vault skills, rules, and MCP servers."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = Path(repo_root or Path(__file__).resolve().parent.parent)
        self.skill_source_dir = self.repo_root / "skills" / "brain-vault-setup"
        self.rule_source_file = self.repo_root / "rules" / "vault_security.md"
        self.mcp_server_script = self.repo_root / "src" / "mcp_server.py"

    def detect_environment(self) -> Dict[str, Any]:
        """Detects available agent platforms, configuration paths, and OS details."""
        home = Path.home()
        env_info: Dict[str, Any] = {
            "platform": sys.platform,
            "python_executable": sys.executable,
            "has_agents_dir": (home / ".agents").exists(),
            "has_claude_desktop": False,
            "has_cursor": (home / ".cursor").exists(),
            "claude_config_path": None,
            "default_skill_dest": home / ".agents" / "skills" / "brain-vault-setup",
            "default_rule_dest": home / ".agents" / "rules" / "dagmas_brain_vault.md"
        }

        # Detect Claude Desktop configuration path
        if sys.platform == "darwin":
            claude_cfg = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
            if claude_cfg.parent.exists():
                env_info["has_claude_desktop"] = True
                env_info["claude_config_path"] = claude_cfg
        elif sys.platform == "win32":
            appdata = os.getenv("APPDATA")
            if appdata:
                claude_cfg = Path(appdata) / "Claude" / "claude_desktop_config.json"
                if claude_cfg.parent.exists():
                    env_info["has_claude_desktop"] = True
                    env_info["claude_config_path"] = claude_cfg
        else:
            claude_cfg = home / ".config" / "claude" / "claude_desktop_config.json"
            if claude_cfg.parent.exists():
                env_info["has_claude_desktop"] = True
                env_info["claude_config_path"] = claude_cfg

        return env_info

    def install_skill(self, dest_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Copies brain-vault-setup skill files to target skills directory."""
        dest = Path(dest_dir or (Path.home() / ".agents" / "skills" / "brain-vault-setup")).expanduser()
        if not self.skill_source_dir.exists():
            return {"success": False, "error": f"Skill source not found at {self.skill_source_dir}"}

        dest.mkdir(parents=True, exist_ok=True)
        copied_files: List[str] = []

        for item in self.skill_source_dir.iterdir():
            target_item = dest / item.name
            if item.is_file():
                shutil.copy2(item, target_item)
                os.chmod(target_item, 0o644)
                copied_files.append(item.name)
            elif item.is_dir():
                if target_item.exists():
                    shutil.rmtree(target_item)
                shutil.copytree(item, target_item)
                copied_files.append(f"{item.name}/")

        return {
            "success": True,
            "dest": str(dest),
            "files_copied": copied_files
        }

    def install_global_rule(self, dest_file: Optional[Path] = None) -> Dict[str, Any]:
        """Installs dagmas_brain_vault.md into the agent's global rules directory."""
        target = Path(dest_file or (Path.home() / ".agents" / "rules" / "dagmas_brain_vault.md")).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)

        content = (
            "# DAGMAS Brain Vault Global Agent Standards\n\n"
            "## 1. Sovereign Vault Sandbox\n"
            "- All memory ledgers (`DO.md`, `DONT.md`), squad rosters, and token stores MUST reside inside `~/.brain-vault` with strict `0700` (`drwx------`) filesystem permissions.\n\n"
            "## 2. Mandatory Privacy Sanitization\n"
            "- Prior to transmitting any text, prompt, stack trace, or environment payload to external cloud models, scrub all 14 credential classes (AWS, Stripe, Slack, database DSNs, private keys, system home paths) using `PrivacySanitizer`.\n\n"
            "## 3. Local-First Small Model Inference (llama.cpp)\n"
            "- Route routine planning, intent classification, and tool dispatching locally through `llama-server` on `http://127.0.0.1:8080/v1` (Qwen 2.5 1.5B, Llama 3.2 1B, IBM Granite 3B) with Apple Silicon Metal acceleration ($0.00 fees, <2 GB RAM).\n"
            "- Reserve cloud models strictly for complex multi-repo synthesis or external APIs.\n\n"
            "## 4. Architectural Verification Gate & ADHD Skill Skeptor\n"
            "- Require deterministic, reproducible `prove-it-done` commands with `exit 0` verification for every software change.\n"
            "- Enforce the **ADHD Skill Skeptor**: single-task hyperfocus lock preventing distraction drift, coupled with Spector.js 60 FPS WebGL/WebGPU graphics profiling (<= 150 draw calls, zero shader thrashing).\n\n"
            "## 5. Quantum Vector DB & Automated Output Graphification\n"
            "- Every task output, artifact, or generated asset MUST be automatically graphified into `~/.brain-vault/code_graph.json` as connected nodes/edges and vector-indexed into the local Quantum Vector DB (Qdrant on port 6333 / SQLite-vec).\n\n"
            "## 6. Bilingual Token Optimization Protocol\n"
            "- All inter-agent communications, swarm packets, subagent prompts, and task reports MUST be strictly formulated in **Simplified Chinese (简体中文)** to maximize information density and cut context token usage by ~70%.\n"
            "- All direct user interactions, explanations, and artifacts MUST be formulated in **English**.\n\n"
            "## 7. Asymmetric Nostr Ed25519 Cryptographic Mesh\n"
            "- Inter-agent messaging between squads MUST use peer-to-peer asymmetric public/private key encryption with signed envelopes (Nostr NIP-44 style) to guarantee zero plaintext leakage on local buses or sockets.\n"
        )

        target.write_text(content, encoding="utf-8")
        os.chmod(target, 0o644)
        return {"success": True, "dest": str(target)}

    def configure_claude_desktop(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Injects brain-vault MCP server entry into Claude Desktop configuration."""
        env = self.detect_environment()
        cfg_file = Path(config_path or env.get("claude_config_path") or (Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"))

        cfg_data: Dict[str, Any] = {"mcpServers": {}}
        if cfg_file.exists():
            try:
                cfg_data = json.loads(cfg_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        cfg_data.setdefault("mcpServers", {})
        cfg_data["mcpServers"]["brain-vault"] = {
            "command": sys.executable,
            "args": ["-m", "src.mcp_server"],
            "cwd": str(self.repo_root)
        }

        cfg_file.parent.mkdir(parents=True, exist_ok=True)
        cfg_file.write_text(json.dumps(cfg_data, indent=2), encoding="utf-8")
        return {"success": True, "config_file": str(cfg_file)}

    def uninstall(self, skill_dir: Optional[Path] = None, rule_file: Optional[Path] = None) -> Dict[str, Any]:
        """Safely removes installed skill directory and global agent rule."""
        s_dir = Path(skill_dir or (Path.home() / ".agents" / "skills" / "brain-vault-setup")).expanduser()
        r_file = Path(rule_file or (Path.home() / ".agents" / "rules" / "dagmas_brain_vault.md")).expanduser()

        removed = []
        if s_dir.exists():
            shutil.rmtree(s_dir)
            removed.append(str(s_dir))
        if r_file.exists():
            r_file.unlink()
            removed.append(str(r_file))

        return {"success": True, "removed": removed}

    def run_all(self, install_rule: bool = True, configure_mcp: bool = True, verify: bool = True) -> Dict[str, Any]:
        """Executes full autonomous installation sequence with verification."""
        results: Dict[str, Any] = {}

        # 1. Install Skill
        results["skill"] = self.install_skill()

        # 2. Install Rule
        if install_rule:
            results["rule"] = self.install_global_rule()

        # 3. Configure MCP
        if configure_mcp:
            env = self.detect_environment()
            if env.get("has_claude_desktop") and env.get("claude_config_path"):
                results["claude_mcp"] = self.configure_claude_desktop(env["claude_config_path"])

        # 4. Verification
        if verify:
            from .preflight import PreflightEngine
            engine = PreflightEngine()
            results["preflight"] = engine.run_all(auto_fix=True)

        return results


def main() -> int:
    """CLI Entrypoint for the installer."""
    parser = argparse.ArgumentParser(
        description="DAGMAS Brain Vault - Autonomous CLI Skill & MCP Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 install.py                  # Standard full installation\n"
            "  python3 install.py --verify-only    # Run preflight diagnostics\n"
            "  python3 install.py --uninstall      # Remove installed skill and rules\n"
        )
    )
    parser.add_argument("--skill-dir", type=str, help="Custom skills destination directory")
    parser.add_argument("--no-rule", action="store_true", help="Do not install global agent rule")
    parser.add_argument("--configure-claude", action="store_true", help="Force configure Claude Desktop MCP")
    parser.add_argument("--verify-only", action="store_true", help="Run preflight diagnostic verification without installing")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall brain-vault-setup skill and global rules")

    args = parser.parse_args()

    print(BANNER)
    installer = SkillInstaller()

    if args.verify_only:
        print("[*] Running preflight diagnostic engine...")
        from src.preflight import PreflightEngine
        engine = PreflightEngine()
        res = engine.run_all(auto_fix=True)
        return res.get("exit_code", 0)

    if args.uninstall:
        print("[*] Uninstalling DAGMAS Brain Vault skill and rules...")
        res = installer.uninstall()
        for r in res.get("removed", []):
            print(f" [OK] Removed: {r}")
        print("\n[OK] Uninstallation complete.")
        return 0

    print("[*] Detecting agent environment...")
    env = installer.detect_environment()
    print(f" - Platform           : {env['platform']}")
    print(f" - Agent Skills       : {'Available' if env['has_agents_dir'] else 'Default created'}")
    print(f" - Claude Desktop     : {'Found' if env['has_claude_desktop'] else 'Not detected'}")

    print("\n[*] Installing 'brain-vault-setup' skill...")
    dest = Path(args.skill_dir) if args.skill_dir else None
    res_skill = installer.install_skill(dest)
    if res_skill["success"]:
        print(f" [OK] Skill installed to: {res_skill['dest']}")
        for f in res_skill["files_copied"]:
            print(f"     + {f}")
    else:
        print(f" [FAIL] Skill installation failed: {res_skill.get('error')}")
        return 1

    if not args.no_rule:
        print("\n[*] Installing global agent rule (dagmas_brain_vault.md)...")
        res_rule = installer.install_global_rule()
        if res_rule["success"]:
            print(f" [OK] Global rule active at: {res_rule['dest']}")

    if args.configure_claude or env.get("has_claude_desktop"):
        print("\n[*] Configuring Claude Desktop Model Context Protocol (MCP)...")
        res_mcp = installer.configure_claude_desktop()
        if res_mcp["success"]:
            print(f" [OK] MCP server registered in: {res_mcp['config_file']}")

    print("\n[*] Running autonomous preflight self-verification...")
    from src.preflight import PreflightEngine
    preflight = PreflightEngine()
    rep = preflight.run_all(auto_fix=True)

    if rep.get("exit_code") == 0:
        print("\n" + "=" * 70)
        print("  DAGMAS BRAIN VAULT IS INSTALLED & READY!")
        print("=" * 70)
        print("\nTo trigger your sovereign architecture setup, simply prompt your agent:")
        print("  > \"Set up Brain Vault and grill me on my architecture choices.\"")
        print("\nOr connect the MCP server to Cursor or Claude Desktop:\n")
        print("  command : python3 -m src.mcp_server")
        print(f"  cwd     : {installer.repo_root}\n")
        return 0
    else:
        print("\n[!] Preflight warning: Some checks did not return PASS.")
        return rep.get("exit_code", 1)


if __name__ == "__main__":
    sys.exit(main())
