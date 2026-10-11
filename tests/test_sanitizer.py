#!/usr/bin/env python3
"""
Unit tests for PrivacySanitizer (src/sanitizer.py).
Asserts that real credentials trigger detection, get scrubbed, and pass verify_clean.
"""

import unittest
from src.sanitizer import PrivacySanitizer

class TestPrivacySanitizer(unittest.TestCase):

    def setUp(self):
        self.sanitizer = PrivacySanitizer()

    def test_all_14_credential_classes_detected_and_scrubbed(self):
        # Realistic sample secrets across all 14 credential classes
        samples = [
            ("AWS Access Key", "AKIAIOSFODNN7EXAMPLE"),
            ("AWS Secret Access Key", "aws_secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'"),
            ("Stripe Live Key", "sk_live_51M0abcdefghijklmnopqrstuvwxyzA"),
            ("Stripe Restricted Key", "rk_live_51M0abcdefghijklmnopqrstuvwxyzA"),
            ("Slack Bot Token", "xoxb-123456789012-1234567890123-456789abcdefghijklmnopqrst"),
            ("Database DSN with Password", "postgres://admin:SuperSecretPass123!@db.internal.net:5432/production"),
            ("OpenAI API Key", "sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx"),
            ("Anthropic API Key", "sk-ant-api03-abcdef1234567890abcdef1234567890abcdef1234567890-AAAAAA"),
            ("GCP Cloud API Key (39 chars)", "AIzaSyDa-abcdefghijklmnopqrstuvwxyz1234"),
            ("GitHub Personal Token", "ghp_1234567890abcdefghijklmnopqrstuvwxyzAB"),
            ("Private Key Block", "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----"),
            ("Ethereum Address", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"),
            ("Generic Password Assignment", "api_key = 'ultra_secret_production_token_1234'"),
            ("Home Directory Path", "/Users/developer/.ssh/id_rsa")
        ]


        for label, raw_secret in samples:
            with self.subTest(label=label):
                # 1. verify_clean must FAIL on raw unscrubbed secret
                is_clean_pre, leaks_pre = self.sanitizer.verify_clean(raw_secret)
                self.assertFalse(
                    is_clean_pre,
                    f"Expected verify_clean to detect {label}, but returned clean=True. Input: {raw_secret}"
                )
                self.assertGreater(
                    len(leaks_pre), 0,
                    f"Expected leak descriptions for {label}"
                )

                # 2. scrub() must redact the secret
                scrubbed = self.sanitizer.scrub(raw_secret)
                self.assertTrue(
                    "<REDACTED" in scrubbed or "~" in scrubbed,
                    f"Expected redaction tag or tilde in scrubbed output for {label}. Scrubbed: {scrubbed}"
                )

                # 3. verify_clean must PASS on scrubbed text
                is_clean_post, leaks_post = self.sanitizer.verify_clean(scrubbed)
                self.assertTrue(
                    is_clean_post,
                    f"Expected verify_clean to pass after scrubbing {label}, but got leaks: {leaks_post}"
                )

    def test_benign_text_remains_clean(self):
        clean_text = "def calculate_score(points: int) -> float:\n    return points * 1.5\n"
        is_clean, leaks = self.sanitizer.verify_clean(clean_text)
        self.assertTrue(is_clean)
        self.assertEqual(leaks, [])

if __name__ == "__main__":
    unittest.main()
