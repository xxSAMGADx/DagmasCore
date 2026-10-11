#!/usr/bin/env python3
"""
Unit tests for SwarmTransport (src/swarm.py).
Tests recursive sanitization of payloads, lists, and nested dictionaries.
"""

import unittest
from src.swarm import SwarmTransport
from src.sanitizer import PrivacySanitizer

class TestSwarmTransport(unittest.TestCase):

    def setUp(self):
        self.swarm = SwarmTransport()

    def test_recursive_payload_sanitization(self):
        # Deep nested structure with multiple secret types
        nested_payload = {
            "top_level": "Safe top level",
            "aws_config": {
                "access_key": "AKIAIOSFODNN7EXAMPLE",
                "secret": "aws_secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'"
            },
            "stripe_list": [
                "sk_live_51M0abcdefghijklmnopqrstuvwxyzA",
                {"nested_slack": "xoxb-123456789012-1234567890123-456789abcdefghijklmnopqrst"}
            ],
            "database_tuple": (
                "postgres://admin:SuperSecretPass123!@db.internal.net:5432/production",
                "clean_value"
            )
        }

        packet = self.swarm.dispatch(
            sender="SecurityBot",
            recipient="WorkerSquad",
            task="Process sk_live_51M0abcdefghijklmnopqrstuvwxyzA integration",
            payload=nested_payload
        )

        p = packet.payload
        # Check task was scrubbed
        self.assertNotIn("sk_live_51M0", packet.task)
        self.assertIn("<REDACTED_STRIPE_KEY>", packet.task)

        # Check deep nested fields scrubbed
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", p["aws_config"]["access_key"])
        self.assertIn("<REDACTED_AWS_ACCESS_KEY>", p["aws_config"]["access_key"])

        self.assertNotIn("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", p["aws_config"]["secret"])

        # Check list element scrubbed
        self.assertNotIn("sk_live_51M0", p["stripe_list"][0])
        self.assertIn("<REDACTED_STRIPE_KEY>", p["stripe_list"][0])

        # Check nested dict within list scrubbed
        self.assertNotIn("xoxb-123456789012", p["stripe_list"][1]["nested_slack"])
        self.assertIn("<REDACTED_SLACK_TOKEN>", p["stripe_list"][1]["nested_slack"])

        # Check tuple scrubbed
        self.assertNotIn("SuperSecretPass123!", p["database_tuple"][0])
        self.assertIn("<REDACTED_DB_PASSWORD>", p["database_tuple"][0])
        self.assertEqual(p["database_tuple"][1], "clean_value")


class TestAgentKeyMesh(unittest.TestCase):

    def setUp(self):
        from src.swarm import AgentKeyMesh, SwarmTransport
        self.mesh = AgentKeyMesh()
        self.swarm = SwarmTransport()

    def test_keypair_registration_and_derivation(self):
        keys = self.mesh.register_agent("AlphaSquad")
        self.assertIn("private_key", keys)
        self.assertIn("public_key", keys)
        # Consistent retrieval
        keys2 = self.mesh.register_agent("AlphaSquad")
        self.assertEqual(keys["public_key"], keys2["public_key"])

    def test_nostr_encrypted_envelope_exchange(self):
        payload = {"instruction": "Refactor core WebGPU buffer geometry", "secret_nonce": "987654"}
        envelope = self.mesh.encrypt_envelope("SenderAgent", "ReceiverAgent", payload)
        self.assertIn("ciphertext", envelope)
        self.assertIn("signature", envelope)
        self.assertIn("sender_pubkey", envelope)
        self.assertIn("recipient_pubkey", envelope)

        # Decrypt
        decrypted = self.mesh.decrypt_envelope("ReceiverAgent", "SenderAgent", envelope)
        self.assertEqual(decrypted["instruction"], "Refactor core WebGPU buffer geometry")
        self.assertEqual(decrypted["secret_nonce"], "987654")

    def test_signature_tampering_rejection(self):
        payload = {"data": "critical payload"}
        envelope = self.mesh.encrypt_envelope("Agent1", "Agent2", payload)
        # Tamper signature
        envelope["signature"] = "tampered_bad_signature_00000000"
        with self.assertRaises(ValueError):
            self.mesh.decrypt_envelope("Agent2", "Agent1", envelope)

    def test_swarm_dispatch_encrypted(self):
        pkt = self.swarm.dispatch(
            sender="Orchestrator",
            recipient="Worker",
            task="Private deployment",
            payload={"token": "clean_deploy_token"},
            encrypt=True,
            key_mesh=self.mesh
        )
        self.assertEqual(pkt.task, "[ENCRYPTED_NOSTR_PAYLOAD]")
        self.assertIn("ciphertext", pkt.payload)
        decrypted = self.mesh.decrypt_envelope("Worker", "Orchestrator", pkt.payload)
        self.assertEqual(decrypted["task"], "Private deployment")


class TestBilingualProtocol(unittest.TestCase):

    def setUp(self):
        from src.swarm import BilingualProtocol
        self.proto = BilingualProtocol()

    def test_chinese_detection(self):
        self.assertTrue(self.proto.contains_chinese("分析并重构代码图谱"))
        self.assertFalse(self.proto.contains_chinese("Analyze and refactor the code graph"))

    def test_user_facing_english_enforcement(self):
        self.assertTrue(self.proto.is_primarily_english("Here is the completed architecture diagram."))
        self.assertFalse(self.proto.is_primarily_english("这是给用户的架构图解释"))

    def test_token_compression_ratio(self):
        eng = "Analyze the authentication flow in src/auth.py and identify any token leakage vulnerabilities."
        cn = "分析 src/auth.py 中的身份验证流程，找出可能存在的令牌泄漏漏洞。"
        ratio = self.proto.calculate_token_compression_ratio(eng, cn)
        self.assertGreater(ratio, 0.0)


if __name__ == "__main__":
    unittest.main()

