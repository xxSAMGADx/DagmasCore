#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Privacy Sanitizers & Scrubbers
Defense-in-depth pattern scrubbing for credentials, tokens, private keys, database DSNs,
and local system paths before external transmission.
"""

import re
from typing import Dict, List, Tuple, Any

# Canonical pattern definitions.
# Each entry is a dict: {"name": str, "regex": Pattern, "replacement": str}
SECRET_PATTERNS: List[Dict[str, Any]] = [
    # 1. AWS Access Key ID
    {
        "name": "aws_access_key",
        "regex": re.compile(r'\b(AKIA[0-9A-Z]{16})\b'),
        "replacement": "<REDACTED_AWS_ACCESS_KEY>"
    },
    # 2. AWS Secret Access Key (with assignment key or known label)
    {
        "name": "aws_secret_key",
        "regex": re.compile(r'(?i)\b(aws_secret_access_key|aws_secret_key|aws_secret)\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?'),
        "replacement": r'\1: <REDACTED_AWS_SECRET_KEY>'
    },
    # 3. Stripe Live & Restricted Keys
    {
        "name": "stripe_api_key",
        "regex": re.compile(r'\b(?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,}\b'),
        "replacement": "<REDACTED_STRIPE_KEY>"
    },
    # 4. Slack Bot, User & App Tokens
    {
        "name": "slack_token",
        "regex": re.compile(r'\bxox[baprs]-[0-9a-zA-Z-]{10,72}\b'),
        "replacement": "<REDACTED_SLACK_TOKEN>"
    },
    # 5. Database Connection DSNs (Postgres, MySQL, Mongo, Redis, AMQP)
    {
        "name": "database_dsn",
        "regex": re.compile(r'(?i)\b((?:postgres|postgresql|mysql|mongodb(?:\+srv)?|redis|amqp):\/\/[^:\s\/]+:)([^@\s\/]+)(@[^\s\/]+)'),
        "replacement": r'\1<REDACTED_DB_PASSWORD>\3'
    },
    # 6. GCP Cloud API Key (39 chars total, typically starts with AIzaSy)
    {
        "name": "gcp_api_key",
        "regex": re.compile(r'\b(AIza[0-9A-Za-z-_]{35})\b'),
        "replacement": "<REDACTED_GCP_API_KEY>"
    },
    # 7. OpenAI API Key (classic sk-... and project sk-proj-...)
    {
        "name": "openai_api_key",
        "regex": re.compile(r'\b(sk-(?:proj-)?[a-zA-Z0-9_\-]{32,})\b'),
        "replacement": "<REDACTED_OPENAI_KEY>"
    },
    # 8. Anthropic API Key
    {
        "name": "anthropic_api_key",
        "regex": re.compile(r'\b(sk-ant-[a-zA-Z0-9_\-]{32,})\b'),
        "replacement": "<REDACTED_ANTHROPIC_KEY>"
    },
    # 9. GitHub Personal Access & Fine-Grained Tokens
    {
        "name": "github_token",
        "regex": re.compile(r'\b((?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,}|github_pat_[a-zA-Z0-9_]{82})\b'),
        "replacement": "<REDACTED_GITHUB_TOKEN>"
    },
    # 10. Private Keys & Certificates Block
    {
        "name": "private_key_block",
        "regex": re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
        "replacement": "<REDACTED_PRIVATE_KEY>"
    },
    # 11. Ethereum Addresses
    {
        "name": "eth_address",
        "regex": re.compile(r'\b(0x[a-fA-F0-9]{40})\b'),
        "replacement": "<REDACTED_ETH_ADDRESS>"
    },
    # 12. Bearer Authentication Tokens
    {
        "name": "bearer_token",
        "regex": re.compile(r'(?i)\bBearer\s+([a-zA-Z0-9_\-\.]{16,})\b'),
        "replacement": "Bearer <REDACTED_BEARER_TOKEN>"
    },
    # 13. Generic Secret Assignments (password, secret, token, api_key, auth)
    {
        "name": "generic_secret_assignment",
        "regex": re.compile(r'(?i)\b(api[_-]?key|token|secret|password|passwd|auth)\s*[:=]\s*["\']?([^"\'\s,;]{8,})["\']?'),
        "replacement": r'\1: <REDACTED_SECRET>'
    },
    # 14. Local System User Directories
    {
        "name": "system_home_path",
        "regex": re.compile(r'/(?:Users|home)/[a-zA-Z0-9_\-]+'),
        "replacement": "~"
    }
]

from .prompt_guard import PromptGuard

class PrivacySanitizer:
    """Sanitizes text and payload data before external transmission, with prompt injection defense."""
    
    def __init__(self, custom_redactions: List[str] = None):
        self.custom_redactions = custom_redactions or []
        self.prompt_guard = PromptGuard()

    def scrub(self, text: str, defang_injection: bool = True) -> str:
        """Applies all scrubber rules and prompt injection defense to text, returning sanitized output."""
        if not text:
            return ""

        scrubbed = text
        for entry in SECRET_PATTERNS:
            pattern = entry["regex"]
            replacement = entry["replacement"]
            scrubbed = pattern.sub(replacement, scrubbed)

        for custom in self.custom_redactions:
            if custom:
                scrubbed = scrubbed.replace(custom, "<REDACTED>")

        if defang_injection:
            scrubbed = self.prompt_guard.scrub(scrubbed)

        return scrubbed

    def verify_clean(self, text: str, check_injection: bool = True) -> Tuple[bool, List[str]]:
        """
        Derives checks directly from SECRET_PATTERNS as the single source of truth,
        and optionally verifies absence of prompt injection vectors.
        Returns (True, []) if clean.
        """
        if not text:
            return True, []

        leaks: List[str] = []

        # Check for unredacted private key block
        if "PRIVATE KEY-----" in text and "<REDACTED_PRIVATE_KEY>" not in text:
            leaks.append("private_key_block: Unredacted private key header detected")

        # Check against each pattern
        for entry in SECRET_PATTERNS:
            name = entry["name"]
            pattern = entry["regex"]

            # Search text for pattern
            for match in pattern.finditer(text):
                matched_str = match.group(0)
                # Ignore if the matched portion is already fully redacted
                if "<REDACTED" in matched_str or matched_str == "~":
                    continue
                # For generic assignment, if the value part is already redacted, ignore
                if name == "generic_secret_assignment" and "<REDACTED" in matched_str:
                    continue
                if name == "database_dsn" and "<REDACTED" in matched_str:
                    continue
                leaks.append(f"{name}: Unredacted pattern matched '{matched_str[:25]}...'")

        # Custom redactions check
        for custom in self.custom_redactions:
            if custom and custom in text:
                leaks.append(f"custom_secret: Custom secret found in text")

        # Check prompt injection vectors
        if check_injection:
            is_inj, inj_findings = self.prompt_guard.detect(text)
            if is_inj:
                leaks.extend(inj_findings)

        return len(leaks) == 0, leaks


if __name__ == "__main__":
    sanitizer = PrivacySanitizer()
    samples = [
        "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "sk_live_51Abcdefghijklmnopqrstuvwx",
        "xoxb-123456789012-1234567890123-456789abcdef",
        "postgres://app_user:SuperSecretPassword123@db.internal:5432/production"
    ]
    for s in samples:
        scrubbed = sanitizer.scrub(s)
        clean, leaks = sanitizer.verify_clean(scrubbed)
        print("Sample:", s[:45])
        print("Scrubbed:", scrubbed)
        print("Clean:", clean, leaks)
        print("-" * 50)
