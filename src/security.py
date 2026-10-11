#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Security Squad & Automated Gates
Enforces AST-based static security analysis, deterministic prove-it-done verification
without shell injection, architectural linting, and host preflight checks.
"""

import os
import ast
import shlex
import shutil
import subprocess
from typing import Dict, Any, List, Tuple
from .sanitizer import PrivacySanitizer

# Forbidden shell chaining operators in prove_it_done
FORBIDDEN_SHELL_OPERATORS = [";", "&&", "||", "|", "`", "$(", "${", ">", "<", "\n", "\r"]

class SecurityTeam:
    """Automated security gatekeeper enforcing system integrity, AST safety, and 'The Bar'."""

    def __init__(self, max_ram_gb: float = 5.5, min_headroom_mb: int = 500):
        self.max_ram_gb = max_ram_gb
        self.min_headroom_mb = min_headroom_mb
        self.sanitizer = PrivacySanitizer()

    def preflight(self) -> Tuple[bool, List[str]]:
        """Preflight check verifying environment, disk headroom, and Python binary."""
        checks = []
        
        # 1. Disk Space Check (Require at least 5GB free)
        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free // (2**30)
            if free_gb < 5:
                checks.append(f"Low disk space: {free_gb}GB free (minimum 5GB required)")
        except Exception as e:
            checks.append(f"Disk check failed: {e}")

        # 2. Python environment sanity
        if not shutil.which("python3"):
            checks.append("python3 is not in PATH")

        return len(checks) == 0, checks

    def run_gates(self, content_sample: str, is_ui: bool = False, filename: str = "") -> Tuple[bool, Dict[str, str]]:
        """
        Runs the three mandatory gates: Security, UI/UX, and Architecture.
        Uses AST analysis and pattern verification rather than superficial substring matches.
        """
        results: Dict[str, str] = {}
        sec_errors: List[str] = []
        arch_errors: List[str] = []

        # -------------------------------------------------------------
        # Gate 1: Security Gate (AST + Secret Verification)
        # -------------------------------------------------------------
        # 1. Check for unredacted secrets in code
        clean, leaks = self.sanitizer.verify_clean(content_sample, check_injection=False)
        if not clean:
            sec_errors.append(f"Credentials detected: {', '.join(leaks[:2])}")

        # 2. Check for prompt injection & jailbreak exploits
        is_inj, inj_findings = self.sanitizer.prompt_guard.detect(content_sample)
        if is_inj:
            sec_errors.append(f"Prompt injection detected: {', '.join(inj_findings[:2])}")

        # 3. Check for dangerous shell execution patterns in raw text
        if "curl " in content_sample and ("| bash" in content_sample or "| sh" in content_sample):
            sec_errors.append("Dangerous remote script piping: 'curl ... | bash'")

        # 3. AST Inspection for Python code
        try:
            tree = ast.parse(content_sample)
            for node in ast.walk(tree):
                # Check dangerous calls
                if isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr

                    if func_name in ("eval", "exec", "compile"):
                        sec_errors.append(f"Arbitrary code execution primitive: '{func_name}()'")
                    elif func_name in ("system", "popen"):
                        sec_errors.append(f"Dangerous OS execution primitive: 'os.{func_name}()'")
                    elif func_name in ("loads", "load"):
                        # Check if module is pickle
                        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                            if node.func.value.id in ("pickle", "_pickle", "marshal", "shelve"):
                                sec_errors.append(f"Unsafe deserialization: '{node.func.value.id}.{func_name}()'")

                # Check dangerous imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ("telnetlib", "ftplib"):
                            sec_errors.append(f"Insecure network library import: '{alias.name}'")
        except SyntaxError as e:
            if filename.endswith(".py"):
                arch_errors.append(f"Python syntax error at line {e.lineno}: {e.msg}")

        if sec_errors:
            results["security"] = f"FAIL: {'; '.join(sec_errors)}"
        else:
            results["security"] = "PASS: Zero high-risk primitives or unredacted credentials detected"

        # -------------------------------------------------------------
        # Gate 2: UI/UX Gate
        # -------------------------------------------------------------
        if is_ui:
            emoji_chars = ["🔥", "🚀", "✨", "🎉", "💯", "👏"]
            found_emojis = [e for e in emoji_chars if e in content_sample]
            if found_emojis:
                results["uiux"] = f"FAIL: Decorative emoji detected on UI surface ({', '.join(found_emojis)})"
            else:
                results["uiux"] = "PASS: Clean typography, zero decorative emoji"
        else:
            results["uiux"] = "PASS: Non-UI step"

        # -------------------------------------------------------------
        # Gate 3: Architecture Gate (Structural Analysis)
        # -------------------------------------------------------------
        # Check for hardcoded local user directories
        if "/Users/" in content_sample or "/home/" in content_sample:
            arch_errors.append("Hardcoded host absolute path (/Users/ or /home/); use relative paths or os.path.expanduser")

        # Check for duplicate function definitions in the same scope
        try:
            tree = ast.parse(content_sample)
            top_level_defs: Dict[str, int] = {}
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    top_level_defs[node.name] = top_level_defs.get(node.name, 0) + 1
                    if top_level_defs[node.name] > 1:
                        arch_errors.append(f"Duplicate top-level definition: '{node.name}'")
        except Exception:
            pass

        if arch_errors:
            results["architecture"] = f"FAIL: {'; '.join(arch_errors)}"
        else:
            results["architecture"] = "PASS: Clean syntax, no host paths or duplicate definitions"

        passed = not sec_errors and not ("FAIL" in results["uiux"]) and not arch_errors
        return passed, results

    def prove_it_done(self, test_cmd: str) -> Tuple[bool, str]:
        """
        Runs deterministic verification command.
        Uses shlex.split() with shell=False and rejects shell metacharacters to eliminate RCE.
        """
        if not test_cmd or not test_cmd.strip():
            return False, "EMPTY COMMAND: prove_it_done requires a valid executable command"

        # 1. Defend against command chaining & shell injection
        for op in FORBIDDEN_SHELL_OPERATORS:
            if op in test_cmd:
                return False, f"SECURITY REJECTION: Shell metacharacter or chaining '{op}' is forbidden in prove_it_done"

        # 2. Split safely into argv list
        try:
            argv = shlex.split(test_cmd)
        except Exception as e:
            return False, f"PARSER ERROR: Invalid command string: {e}"

        if not argv:
            return False, "EMPTY ARGV: No command to execute"

        # 3. Execute with shell=False
        try:
            res = subprocess.run(argv, shell=False, capture_output=True, text=True, timeout=15)
            if res.returncode == 0:
                output_snip = res.stdout.strip()[:100] if res.stdout else "Success"
                return True, f"EXIT 0: {output_snip}"
            else:
                err_snip = res.stderr.strip()[:100] if res.stderr else f"Exit code {res.returncode}"
                return False, f"EXIT {res.returncode}: {err_snip}"
        except FileNotFoundError:
            return False, f"COMMAND NOT FOUND: Executable '{argv[0]}' does not exist"
        except subprocess.TimeoutExpired:
            return False, "TIMEOUT: Command execution exceeded 15 seconds"
        except Exception as e:
            return False, f"EXECUTION ERROR: {str(e)}"


if __name__ == "__main__":
    sec = SecurityTeam()
    ok, issues = sec.preflight()
    print("Preflight:", ok, issues)

    # Test dangerous eval
    p1, g1 = sec.run_gates("eval('2+2')", is_ui=False)
    print("Gate on eval():", p1, g1["security"])

    # Test pickle.loads
    p2, g2 = sec.run_gates("import pickle\npickle.loads(b'foo')", is_ui=False)
    print("Gate on pickle:", p2, g2["security"])

    # Test prove_it_done injection defense
    success, msg = sec.prove_it_done("true; echo SECOND-COMMAND-RAN")
    print("Prove-it-done injection test:", success, msg)

    # Test valid prove_it_done
    s2, m2 = sec.prove_it_done("python3 -c 'print(\"Verified\")'")
    print("Valid prove-it-done test:", s2, m2)
