#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Universal Agent Plugin & Cloud Airlock
Drop-in middleware and plugin adapter for OpenAI, Claude, DAGMAS, OpenClaw, and Pi.
Sanitizes prompts, strips credentials, blocks prompt injections, and logs handoffs
before escalating requests to external cloud frontier models.
"""

from typing import Dict, Any, List, Union
from .sanitizer import PrivacySanitizer
from .prompt_guard import PromptGuard
from .swarm import SwarmTransport
from .vault import VaultSandbox, DEFAULT_VAULT_PATH

SUPPORTED_PLATFORMS = ["openai", "claude", "dagmas", "claw", "pi"]

class BrainVaultConnector:
    """Universal security airlock connecting local vaults to cloud models."""

    def __init__(self, vault_path: str = DEFAULT_VAULT_PATH):
        self.vault = VaultSandbox(vault_path)
        self.sanitizer = PrivacySanitizer()
        self.prompt_guard = PromptGuard()
        self.swarm = SwarmTransport(self.sanitizer)

    def estimate_tokens(self, text: str) -> int:
        """Rough token count estimation (approx 4 chars per token)."""
        return max(1, len(text) // 4)

    def trim_context(self, text: str, max_tokens: int = 1500) -> str:
        """
        Prunes and trims bloated context before external transmission to limit cloud token spend.
        Keeps initial instructions and recent context while shedding unnecessary middle bloat.
        """
        est_tokens = self.estimate_tokens(text)
        if est_tokens <= max_tokens:
            return text
        
        char_limit = max_tokens * 4
        head_chars = int(char_limit * 0.4)
        tail_chars = int(char_limit * 0.6)
        
        pruned_notice = f"\n\n[... TRUNCATED BY BRAIN VAULT AIRLOCK: {est_tokens - max_tokens} TOKENS SAVED TO PREVENT CLOUD OVERSPEND ...]\n\n"
        return text[:head_chars] + pruned_notice + text[-tail_chars:]

    def sanitize_for_cloud(self, text: str, platform: str = "openai", max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Sanitizes text before sending to any cloud provider (OpenAI, Claude, DAGMAS, Claw, Pi).
        Applies prompt pruning to strictly limit token expenditure, scrubs secrets, and defangs injections.
        """
        platform_normalized = platform.lower().strip()
        
        # 1. Prune bloated context to cap external token usage
        trimmed_text = self.trim_context(text, max_tokens=max_tokens)
        
        # 2. Detect any unredacted credentials
        is_clean, leaks = self.sanitizer.verify_clean(trimmed_text, check_injection=False)

        # 3. Detect any prompt injection tricks
        is_inj, inj_findings = self.prompt_guard.detect(trimmed_text)

        # 4. Scrub secrets and defang prompt injections
        clean_text = self.sanitizer.scrub(trimmed_text, defang_injection=True)

        return {
            "platform": platform_normalized,
            "original_length": len(text),
            "estimated_tokens": self.estimate_tokens(clean_text),
            "clean_text": clean_text,
            "credentials_redacted": leaks,
            "injections_neutralized": inj_findings,
            "safe_for_cloud": True
        }

    def openai_hook(self, messages: List[Dict[str, str]], max_tokens_per_msg: int = 2000) -> List[Dict[str, str]]:
        """Pre-processes chat completion messages: limits tokens, scrubs secrets, blocks injection."""
        sanitized_messages = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                trimmed = self.trim_context(content, max_tokens=max_tokens_per_msg)
                scrubbed = self.sanitizer.scrub(trimmed, defang_injection=True)
                sanitized_messages.append({"role": msg.get("role", "user"), "content": scrubbed})
            else:
                sanitized_messages.append(msg)
        return sanitized_messages

    def claude_hook(self, prompt: str, max_tokens: int = 2500) -> str:
        """Pre-processes prompt before sending to Anthropic Claude: caps tokens and scrubs secrets."""
        trimmed = self.trim_context(prompt, max_tokens=max_tokens)
        return self.sanitizer.scrub(trimmed, defang_injection=True)

    def dagmas_hook(self, task: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Inter-agent dispatch adapter for DAGMAS runtime."""
        pkt = self.swarm.dispatch("LocalBrainVault", "DagmasCloudSquad", task, payload)
        return pkt.to_dict()

    def claw_hook(self, command: str) -> str:
        """Pre-processes command string for OpenClaw edge agent."""
        return self.sanitizer.scrub(command, defang_injection=True)

    def pi_hook(self, prompt: str) -> str:
        """Pre-processes prompt for Pi edge / Raspberry Pi setups."""
        return self.sanitizer.scrub(prompt, defang_injection=True)

    def plugin_info(self) -> Dict[str, Any]:
        """Returns plugin configuration and platform compatibility."""
        return {
            "plugin": "brain-vault",
            "version": "1.0.0",
            "supported_platforms": SUPPORTED_PLATFORMS,
            "vault_active": self.vault.vault_path.exists(),
            "vault_permissions": self.vault.status().get("mode_octal", "uninitialized")
        }


if __name__ == "__main__":
    connector = BrainVaultConnector()
    print("Brain Vault Universal Plugin Info:")
    import json
    print(json.dumps(connector.plugin_info(), indent=2))
    
    test_leak = "Hey Claude, deploy to postgres://admin:SuperSecret123@db.com:5432/prod with sk_live_51M0abcdef"
    res = connector.sanitize_for_cloud(test_leak, platform="claude")
    print("\nSanitized for Claude:")
    print("Result:", res["clean_text"])
