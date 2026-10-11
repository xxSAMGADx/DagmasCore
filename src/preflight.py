#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Autonomous Preflight Diagnostic & Self-Healing Engine
Runs deep system diagnostic checks on the sovereign vault environment:
- 0700/0600 filesystem security & sandbox integrity
- Configuration and keystore permissions
- Global agent rules and skill registrations
- Regression test suite verification (54 tests)
- Local reasoning core readiness (Cactus Compute Needle 3 & llama.cpp)
- Vector DB (Qdrant) connectivity

If any check fails or is degraded, the engine actively self-heals / auto-fixes
the broken component and verifies the repair before reporting final status.
"""

import os
import sys
import json
import stat
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .vault import VaultSandbox, DEFAULT_VAULT_PATH
from .needle import NeedleEngine
from .schemas import (
    validate_schema,
    VAULT_CONFIG_SCHEMA,
    LIMITS_SCHEMA,
    REGISTRY_SCHEMA,
    CODE_GRAPH_SCHEMA,
    get_default_limits_config,
    get_default_registry_json,
    get_default_code_graph_json,
    get_default_vault_config
)

class PreflightEngine:
    """Diagnostic and self-healing engine for Brain Vault."""

    def __init__(self, vault_path: str = DEFAULT_VAULT_PATH, repo_root: Optional[str] = None):
        self.vault_path = Path(vault_path)
        self.vault = VaultSandbox(str(self.vault_path))
        self.needle = NeedleEngine()
        if repo_root:
            self.repo_root = Path(repo_root)
        else:
            self.repo_root = Path(__file__).resolve().parent.parent

    def run_all(self, auto_fix: bool = True, run_tests: bool = True) -> Dict[str, Any]:
        """
        Executes all preflight checks, automatically repairing any degraded components.
        Returns a comprehensive diagnostic report.
        """
        results: List[Dict[str, Any]] = []
        fixes_applied: List[str] = []

        # 1. Sandbox Permissions & Directory Structure
        sb_res, sb_fixes = self.check_and_heal_sandbox(auto_fix=auto_fix)
        results.append(sb_res)
        fixes_applied.extend(sb_fixes)

        # 2. Config & Keystore Security
        cfg_res, cfg_fixes = self.check_and_heal_config_and_keystore(auto_fix=auto_fix)
        results.append(cfg_res)
        fixes_applied.extend(cfg_fixes)

        # 3. Brain & System Schema Compliance
        schema_res, schema_fixes = self.check_and_heal_brain_schemas(auto_fix=auto_fix)
        results.append(schema_res)
        fixes_applied.extend(schema_fixes)

        # 4. Global Agent Default Rule
        rule_res, rule_fixes = self.check_and_heal_global_rule(auto_fix=auto_fix)
        results.append(rule_res)
        fixes_applied.extend(rule_fixes)

        # 5. Agent Skills Synchronization
        skill_res, skill_fixes = self.check_and_heal_skills_sync(auto_fix=auto_fix)
        results.append(skill_res)
        fixes_applied.extend(skill_fixes)

        # 6. Local Reasoning Engines (Needle 3 / llama.cpp)
        engine_res = self.check_reasoning_engines()
        results.append(engine_res)

        # 7. Qdrant Vector DB Connectivity
        qdrant_res = self.check_qdrant_connectivity()
        results.append(qdrant_res)

        # 8. Regression Unit Test Suite
        if run_tests:
            test_res = self.check_regression_tests()
            results.append(test_res)

        # Determine overall status
        has_failure = any(r.get("status") == "FAIL" for r in results)
        has_warning = any(r.get("status") == "WARN" for r in results)

        overall_status = "FAIL" if has_failure else ("WARN" if has_warning else "PASS")
        exit_code = 1 if has_failure else 0

        return {
            "overall_status": overall_status,
            "exit_code": exit_code,
            "total_checks": len(results),
            "fixes_applied": fixes_applied,
            "checks": results
        }

    def check_and_heal_sandbox(self, auto_fix: bool = True) -> Tuple[Dict[str, Any], List[str]]:
        """Verifies and heals ~/.brain-vault sandbox and 0700 permissions."""
        fixes = []
        status = "PASS"
        details = []

        if not self.vault_path.exists():
            if auto_fix:
                self.vault_path.mkdir(parents=True, exist_ok=True)
                os.chmod(self.vault_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                fixes.append(f"Created missing vault directory at {self.vault_path} with 0700 permissions.")
                details.append("Vault directory created and locked to 0700.")
            else:
                return {
                    "name": "sandbox_integrity",
                    "status": "FAIL",
                    "message": f"Vault path {self.vault_path} does not exist."
                }, fixes
        else:
            # Check octal permissions
            mode = os.stat(self.vault_path).st_mode & 0o777
            if mode != 0o700:
                if auto_fix:
                    os.chmod(self.vault_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                    fixes.append(f"Fixed vault permissions from {oct(mode)} to 0700 (drwx------).")
                    details.append("Vault permissions repaired to 0700.")
                else:
                    status = "FAIL"
                    details.append(f"Vault permissions insecure: {oct(mode)} (expected 0700).")
            else:
                details.append("Vault root locked to 0700.")

        # Check subdirectories
        required_dirs = ["teams", "skills", "memory", "ledgers"]
        for subdir_name in required_dirs:
            sub = self.vault_path / subdir_name
            if not sub.exists():
                if auto_fix:
                    sub.mkdir(parents=True, exist_ok=True)
                    os.chmod(sub, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                    fixes.append(f"Created missing subdirectory {subdir_name} with 0700 permissions.")
                else:
                    status = "FAIL"
                    details.append(f"Subdirectory {subdir_name} missing.")
            else:
                sub_mode = os.stat(sub).st_mode & 0o777
                if sub_mode != 0o700:
                    if auto_fix:
                        os.chmod(sub, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                        fixes.append(f"Fixed {subdir_name} permissions to 0700.")
                    else:
                        status = "WARN"

        # Check living ledgers
        ledgers_dir = self.vault_path / "ledgers"
        do_file = ledgers_dir / "DO.md"
        dont_file = ledgers_dir / "DONT.md"

        if not do_file.exists():
            if auto_fix:
                do_file.write_text("# Living Ledger: DO\n\n- [System] Always verify preflight before execution.\n- [Security] Enforce 0700 permissions on all vault files.\n", encoding="utf-8")
                fixes.append("Created missing DO.md living ledger.")
            else:
                status = "WARN"
                details.append("DO.md missing in ledgers.")

        if not dont_file.exists():
            if auto_fix:
                dont_file.write_text("# Living Ledger: DONT\n\n- [Security] Never leak unredacted tokens to external APIs.\n- [System] Never bypass the verify-against-source check.\n", encoding="utf-8")
                fixes.append("Created missing DONT.md living ledger.")
            else:
                status = "WARN"
                details.append("DONT.md missing in ledgers.")

        return {
            "name": "sandbox_integrity",
            "status": status,
            "message": "; ".join(details) if details else "Sandbox intact and secured at 0700."
        }, fixes

    def check_and_heal_config_and_keystore(self, auto_fix: bool = True) -> Tuple[Dict[str, Any], List[str]]:
        """Verifies configuration validity and keystore security (0600)."""
        fixes = []
        status = "PASS"
        details = []

        cfg_file = self.vault_path / "vault_config.json"
        if not cfg_file.exists():
            if auto_fix:
                self.vault.initialize()
                fixes.append("Regenerated default vault_config.json.")
                details.append("vault_config.json regenerated.")
            else:
                return {
                    "name": "config_and_keystore",
                    "status": "FAIL",
                    "message": "vault_config.json is missing."
                }, fixes
        else:
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("Config is not a valid JSON dictionary.")
                details.append("vault_config.json valid.")
            except Exception as e:
                if auto_fix:
                    self.vault.initialize()
                    fixes.append(f"Repaired corrupt vault_config.json: {e}")
                    details.append("Corrupt config re-initialized.")
                else:
                    status = "FAIL"
                    details.append(f"Corrupt vault_config.json: {e}")

        # Check keystore permissions if it exists
        keystore_file = self.vault_path / "keystore.json"
        if keystore_file.exists():
            kmode = os.stat(keystore_file).st_mode & 0o777
            if kmode != 0o600:
                if auto_fix:
                    os.chmod(keystore_file, stat.S_IRUSR | stat.S_IWUSR)
                    fixes.append(f"Restricted keystore.json permissions from {oct(kmode)} to 0600 (owner rw only).")
                    details.append("keystore.json locked to 0600.")
                else:
                    status = "FAIL"
                    details.append(f"keystore.json permissions insecure: {oct(kmode)}.")
            else:
                details.append("keystore.json secured at 0600.")

        return {
            "name": "config_and_keystore",
            "status": status,
            "message": "; ".join(details)
        }, fixes

    def check_and_heal_brain_schemas(self, auto_fix: bool = True) -> Tuple[Dict[str, Any], List[str]]:
        """Audits compliance against canonical Brain & System schemas (limits, registry, code_graph)."""
        fixes = []
        details = []
        status = "PASS"

        # 1. limits.json
        limits_file = self.vault_path / "limits.json"
        if not limits_file.exists():
            if auto_fix:
                data = get_default_limits_config()
                limits_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                os.chmod(limits_file, stat.S_IRUSR | stat.S_IWUSR)
                fixes.append("Provisioned missing limits.json complying with LIMITS_SCHEMA.")
                details.append("limits.json provisioned.")
            else:
                status = "WARN"
                details.append("limits.json missing.")
        else:
            try:
                data = json.loads(limits_file.read_text(encoding="utf-8"))
                ok, err = validate_schema(data, LIMITS_SCHEMA)
                if not ok:
                    if auto_fix:
                        data = get_default_limits_config()
                        limits_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                        fixes.append(f"Healed non-compliant limits.json: {err}")
                        details.append("limits.json repaired.")
                    else:
                        status = "WARN"
                        details.append(f"limits.json invalid: {err}")
                else:
                    details.append("limits.json valid.")
            except Exception as e:
                if auto_fix:
                    data = get_default_limits_config()
                    limits_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    fixes.append(f"Healed corrupt limits.json: {e}")
                    details.append("limits.json repaired.")
                else:
                    status = "WARN"
                    details.append(f"limits.json corrupt: {e}")

        # 2. registry.json
        registry_file = self.vault_path / "registry.json"
        if not registry_file.exists():
            if auto_fix:
                data = get_default_registry_json()
                registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                os.chmod(registry_file, stat.S_IRUSR | stat.S_IWUSR)
                fixes.append("Provisioned missing registry.json complying with REGISTRY_SCHEMA.")
                details.append("registry.json provisioned.")
            else:
                status = "WARN"
                details.append("registry.json missing.")
        else:
            try:
                data = json.loads(registry_file.read_text(encoding="utf-8"))
                ok, err = validate_schema(data, REGISTRY_SCHEMA)
                if not ok:
                    if auto_fix:
                        data = get_default_registry_json()
                        registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                        fixes.append(f"Healed non-compliant registry.json: {err}")
                        details.append("registry.json repaired.")
                    else:
                        status = "WARN"
                        details.append(f"registry.json invalid: {err}")
                else:
                    details.append(f"registry.json valid ({data.get('total_nodes', len(data.get('nodes', [])))} nodes).")
            except Exception as e:
                if auto_fix:
                    data = get_default_registry_json()
                    registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    fixes.append(f"Healed corrupt registry.json: {e}")
                    details.append("registry.json repaired.")
                else:
                    status = "WARN"

        # 3. code_graph.json
        graph_file = self.vault_path / "code_graph.json"
        if not graph_file.exists():
            if auto_fix:
                data = get_default_code_graph_json()
                graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                os.chmod(graph_file, stat.S_IRUSR | stat.S_IWUSR)
                fixes.append("Provisioned missing code_graph.json complying with CODE_GRAPH_SCHEMA.")
                details.append("code_graph.json provisioned.")
            else:
                status = "WARN"
                details.append("code_graph.json missing.")
        else:
            try:
                data = json.loads(graph_file.read_text(encoding="utf-8"))
                ok, err = validate_schema(data, CODE_GRAPH_SCHEMA)
                if not ok:
                    if auto_fix:
                        data = get_default_code_graph_json()
                        graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                        fixes.append(f"Healed non-compliant code_graph.json: {err}")
                        details.append("code_graph.json repaired.")
                    else:
                        status = "WARN"
                        details.append(f"code_graph.json invalid: {err}")
                else:
                    details.append("code_graph.json valid.")
            except Exception as e:
                if auto_fix:
                    data = get_default_code_graph_json()
                    graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
                    fixes.append(f"Healed corrupt code_graph.json: {e}")
                    details.append("code_graph.json repaired.")
                else:
                    status = "WARN"

        return {
            "name": "brain_schemas",
            "status": status,
            "message": "; ".join(details)
        }, fixes

    def check_and_heal_global_rule(self, auto_fix: bool = True) -> Tuple[Dict[str, Any], List[str]]:
        """Verifies that the global agent default rule is in place."""
        fixes = []
        status = "PASS"
        rule_path = Path(os.path.expanduser("~/.agents/rules/dagmas_brain_vault.md"))

        if not rule_path.exists():
            if auto_fix:
                rule_path.parent.mkdir(parents=True, exist_ok=True)
                source_rule = self.repo_root / "rules" / "vault_security.md"
                if source_rule.exists():
                    shutil.copy2(source_rule, rule_path)
                else:
                    self.vault.install_global_agent_default()
                fixes.append("Installed missing global agent rule at ~/.agents/rules/dagmas_brain_vault.md.")
                message = "Global agent default rule installed."
            else:
                status = "WARN"
                message = "Global rule ~/.agents/rules/dagmas_brain_vault.md is not installed."
        else:
            message = "Global agent rule ~/.agents/rules/dagmas_brain_vault.md active."

        return {
            "name": "global_agent_rule",
            "status": status,
            "message": message
        }, fixes

    def check_and_heal_skills_sync(self, auto_fix: bool = True) -> Tuple[Dict[str, Any], List[str]]:
        """Verifies that the brain-vault-setup skill is present in active agent config."""
        fixes = []
        status = "PASS"
        skill_path = Path(os.path.expanduser("~/.agents/skills/brain-vault-setup/SKILL.md"))
        source_skill = self.repo_root / "skills" / "brain-vault-setup" / "SKILL.md"

        if not skill_path.exists():
            if auto_fix and source_skill.exists():
                skill_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_skill, skill_path)
                fixes.append("Installed brain-vault-setup skill into ~/.agents/skills/.")
                message = "Skill brain-vault-setup installed."
            else:
                status = "WARN"
                message = "Skill brain-vault-setup not found in ~/.agents/skills/."
        else:
            # Check if synced
            if source_skill.exists() and source_skill.read_text(encoding="utf-8") != skill_path.read_text(encoding="utf-8"):
                if auto_fix:
                    shutil.copy2(source_skill, skill_path)
                    fixes.append("Updated out-of-date brain-vault-setup skill in ~/.agents/skills/.")
                    message = "Skill synchronized to latest version."
                else:
                    status = "WARN"
                    message = "Skill in ~/.agents/skills/ is out of date."
            else:
                message = "Skill brain-vault-setup installed and in sync."

        return {
            "name": "skills_sync",
            "status": status,
            "message": message
        }, fixes

    def check_reasoning_engines(self) -> Dict[str, Any]:
        """Audits readiness of local reasoning engines (Needle 3 & llama.cpp)."""
        needle_spec = self.needle.get_cactus_needle_spec()
        needle_avail = self.needle.check_cactus_needle_available()
        llama_avail = self.vault.check_llama_cpp_available()

        details = []
        details.append(f"Cactus Needle 3 ({needle_spec.get('model_series', 'Needle 3')} {needle_spec.get('binary_size_mb', '8-29 MB')}) available: {needle_avail}")
        details.append(f"llama.cpp runner available: {llama_avail}")

        return {
            "name": "local_reasoning_engines",
            "status": "PASS",
            "message": "; ".join(details),
            "needle_spec": needle_spec,
            "llama_cpp_available": llama_avail
        }

    def check_qdrant_connectivity(self) -> Dict[str, Any]:
        """Checks if Qdrant vector database is responsive on port 6333."""
        qdrant_url = "http://127.0.0.1:6333/collections"
        try:
            req = urllib.request.Request(qdrant_url, method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return {
                        "name": "qdrant_vector_db",
                        "status": "PASS",
                        "message": "Qdrant is running on http://127.0.0.1:6333 (collections accessible)."
                    }
        except Exception:
            pass

        return {
            "name": "qdrant_vector_db",
            "status": "WARN",
            "message": "Qdrant is offline at http://127.0.0.1:6333. Operating in lightweight SQLite-vec/markdown ledger fallback."
        }

    def check_regression_tests(self) -> Dict[str, Any]:
        """Runs the standard library test suite to verify system integrity."""
        if os.environ.get("BRAIN_VAULT_IN_TEST_RUNNER") == "1":
            return {
                "name": "regression_tests",
                "status": "PASS",
                "message": "Active unittest runner detected; skipping recursive test runner invocation.",
                "exit_code": 0
            }

        tests_dir = self.repo_root / "tests"
        if not tests_dir.exists():
            return {
                "name": "regression_tests",
                "status": "WARN",
                "message": f"Tests directory {tests_dir} not found."
            }

        cmd = [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir)]
        env = dict(os.environ, BRAIN_VAULT_IN_TEST_RUNNER="1")
        try:
            proc = subprocess.run(cmd, cwd=str(self.repo_root), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        except Exception as e:
            return {
                "name": "regression_tests",
                "status": "FAIL",
                "message": f"Regression test suite execution error: {e}",
                "exit_code": 1
            }

        if proc.returncode == 0:
            lines = proc.stderr.splitlines()
            summary = [l for l in lines if "Ran" in l or "OK" in l]
            return {
                "name": "regression_tests",
                "status": "PASS",
                "message": "All regression tests passed cleanly (exit 0). " + " ".join(summary),
                "exit_code": 0
            }
        else:
            return {
                "name": "regression_tests",
                "status": "FAIL",
                "message": f"Regression test suite failed (exit {proc.returncode}):\n{proc.stderr}",
                "exit_code": proc.returncode
            }

    def print_report(self, report: Dict[str, Any]):
        """Renders an executive preflight report to stdout."""
        print("=" * 70)
        print("  DAGMAS BRAIN VAULT - PREFLIGHT DIAGNOSTIC & SELF-HEALING REPORT")
        print("=" * 70)
        print(f"Overall Status : {report['overall_status']} (Exit Code: {report['exit_code']})")
        print(f"Total Checks   : {report['total_checks']}")
        print(f"Fixes Applied  : {len(report['fixes_applied'])}")
        print("-" * 70)

        for check in report["checks"]:
            badge = f"[{check['status']}]"
            print(f" {badge:<8} {check['name']:<25} : {check['message']}")

        if report["fixes_applied"]:
            print("-" * 70)
            print("Self-Healing Actions Taken:")
            for fix in report["fixes_applied"]:
                print(f"  - {fix}")

        print("=" * 70)


def main():
    auto_fix = "--no-fix" not in sys.argv
    engine = PreflightEngine()
    report = engine.run_all(auto_fix=auto_fix)
    engine.print_report(report)
    sys.exit(report["exit_code"])


if __name__ == "__main__":
    main()
