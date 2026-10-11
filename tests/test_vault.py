#!/usr/bin/env python3
"""
Unit tests for DAGMASBrainVault (src/vault.py).
Pins 0700 sandbox permission checks and directory structure validation.
"""

import os
import unittest
import tempfile
from pathlib import Path
from src.vault import VaultSandbox

class TestDAGMASBrainVault(unittest.TestCase):

    def test_vault_permissions_0700_enforced(self):
        with tempfile.TemporaryDirectory() as td:
            vault_dir = Path(td) / "test_vault"
            vault = VaultSandbox(vault_path=str(vault_dir))
            init_res = vault.initialize()

            self.assertTrue(vault_dir.exists())
            mode = os.stat(vault_dir).st_mode & 0o777
            self.assertEqual(
                mode, 0o700,
                f"Vault directory permissions must be strictly 0700 (drwx------), got {oct(mode)}"
            )

            status = vault.status()
            self.assertTrue(status["exists"])
            self.assertTrue(status["permissions_secure_0700"])
            self.assertEqual(status["mode_octal"], "0o700")

    def test_vault_subdirectories_created(self):
        with tempfile.TemporaryDirectory() as td:
            vault_dir = Path(td) / "test_vault"
            vault = VaultSandbox(vault_path=str(vault_dir))
            vault.initialize()

            self.assertTrue(vault.skills_dir.exists())
            self.assertTrue(vault.teams_dir.exists())
            self.assertTrue(vault.memory_dir.exists())
            self.assertTrue(vault.ledgers_dir.exists())

    def test_key_storage_options(self):
        with tempfile.TemporaryDirectory() as td:
            vault_dir = Path(td) / "test_vault"
            vault = VaultSandbox(vault_path=str(vault_dir))
            vault.initialize()

            # 1. Local Encrypted 0600 storage test
            res = vault.store_secret("OPENAI_API_KEY", "sk-proj-test123456789", backend="local_encrypted")
            self.assertTrue(res["success"])
            self.assertEqual(res["backend"], "local_encrypted")
            
            retrieved = vault.get_secret("OPENAI_API_KEY", backend="local_encrypted")
            self.assertTrue(retrieved["found"])
            self.assertEqual(retrieved["value"], "sk-proj-test123456789")

            # 2. Bitwarden backend handling test
            bw_res = vault.store_secret("STRIPE_KEY", "sk_live_12345", backend="bitwarden")
            # If Bitwarden CLI is installed or not, ensure response handles gracefully
            self.assertIn("backend", bw_res)
            self.assertEqual(bw_res["backend"], "bitwarden")

    def test_llama_cpp_runner_configuration(self):
        with tempfile.TemporaryDirectory() as td:
            vault_dir = Path(td) / "test_vault"
            vault = VaultSandbox(vault_path=str(vault_dir))
            config = vault.initialize(
                local_model_id="qwen2.5-1.5b-instruct",
                runner="llama.cpp",
                local_endpoint="http://127.0.0.1:8080/v1"
            )

            self.assertIn("local_model", config)
            self.assertEqual(config["local_model"]["runner"], "llama.cpp")
            self.assertEqual(config["local_model"]["model_id"], "qwen2.5-1.5b-instruct")
            self.assertEqual(config["local_model"]["endpoint"], "http://127.0.0.1:8080/v1")
            self.assertIn("llama_cpp_installed", config["local_model"])
            self.assertIsInstance(config["local_model"]["llama_cpp_installed"], bool)

    def test_check_llama_cpp_available(self):
        vault = VaultSandbox()
        is_avail = vault.check_llama_cpp_available()
        self.assertIsInstance(is_avail, bool)

    def test_install_global_agent_default(self):
        with tempfile.TemporaryDirectory() as td:
            rules_dir = Path(td) / "test_rules"
            vault = VaultSandbox()
            res = vault.install_global_agent_default(rules_dir=str(rules_dir))
            self.assertTrue(res["installed"])
            rule_file = rules_dir / "dagmas_brain_vault.md"
            self.assertTrue(rule_file.exists())
            content = rule_file.read_text(encoding="utf-8")
            self.assertIn("DAGMAS Brain Vault Global Agent Standards", content)
            self.assertIn("llama.cpp", content)
            self.assertIn("0700", content)
            self.assertIn("Privacy Sanitization", content)
    def test_graphify_and_index_quantum_db(self):
        with tempfile.TemporaryDirectory() as td:
            vault_dir = Path(td) / "test_vault"
            vault = VaultSandbox(vault_path=str(vault_dir))
            vault.initialize()

            res = vault.graphify_and_index_quantum_db(
                node_id="artifact:feature_plan",
                label="Feature Implementation Plan",
                content="# Feature Plan\nDetails on Nostr key mesh.",
                node_type="artifact",
                metadata={"author": "Sam"},
                relations=[{"source": "artifact:feature_plan", "target": "core:the_brain", "relation": "documents"}]
            )

            self.assertTrue(res["success"])
            self.assertEqual(res["node_id"], "artifact:feature_plan")
            self.assertGreaterEqual(res["total_nodes"], 1)
            self.assertEqual(res["quantum_vector_db"]["status"], "INDEXED")
            self.assertEqual(res["quantum_vector_db"]["collection"], "quantum_agent_outputs")

            # Check code_graph.json
            graph_file = vault_dir / "code_graph.json"
            self.assertTrue(graph_file.exists())
            import json
            graph = json.loads(graph_file.read_text(encoding="utf-8"))
            node_ids = [n["id"] for n in graph["nodes"]]
            self.assertIn("artifact:feature_plan", node_ids)


if __name__ == "__main__":
    unittest.main()

