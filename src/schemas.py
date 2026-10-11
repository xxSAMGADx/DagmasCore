#!/usr/bin/env python3
"""
DAGMAS Brain Vault - The Brain & System Schema Specification
Defines the canonical JSON schemas, default structural templates, and pure standard-library
validation routines for all core Brain Vault subsystems:
1. vault_config.json (Sovereign sandbox configuration)
2. limits.json (Resource governance, memory ceilings, rate limits)
3. registry.json (718-node code registry with SHA-256 change detection)
4. code_graph.json (Static dependency and node routing graph)
5. team SOUL profiles (teams/*.json & SOUL.md squad definitions)
6. memory ledgers (DO.md, DONT.md, LESSONS.md, world_facts.jsonl)

Zero external dependencies - 100% Python Standard Library.
"""

import json
from typing import Dict, Any, List, Tuple, Optional

# ==============================================================================
# 1. CANONICAL JSON SCHEMAS
# ==============================================================================

VAULT_CONFIG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "BrainVaultConfig",
    "type": "object",
    "required": ["vault_path", "permissions", "local_model", "tool_engine", "max_ram_gb", "min_headroom_mb"],
    "properties": {
        "vault_path": {"type": "string"},
        "initialized": {"type": "boolean"},
        "version": {"type": "string"},
        "permissions": {"type": "string", "enum": ["0700", "0o700"]},
        "key_storage": {
            "type": "object",
            "required": ["backend"],
            "properties": {
                "backend": {"type": "string", "enum": ["local_encrypted", "bitwarden"]},
                "bitwarden_status": {"type": "boolean"}
            }
        },
        "local_model": {
            "type": "object",
            "required": ["runner", "model_id", "parameter_tier", "tool_engine"],
            "properties": {
                "runner": {"type": "string", "enum": ["llama.cpp", "cactus-needle", "ollama", "custom"]},
                "model_id": {"type": "string"},
                "parameter_tier": {"type": "string", "enum": ["sub-1b", "1b", "custom"]},
                "tool_engine": {"type": "string", "enum": ["gemma2-embedded", "needle-tool", "custom"]},
                "endpoint": {"type": "string"},
                "llama_cpp_installed": {"type": "boolean"}
            }
        },
        "runtime_engine": {"type": "string", "enum": ["python", "rust"]},
        "bun_enabled": {"type": "boolean"},
        "graphify_enabled": {"type": "boolean"},
        "tool_engine": {"type": "string"},
        "embedder_model": {"type": "string"},
        "qdrant_url": {"type": "string"},
        "qdrant_collections": {"type": "integer"},
        "max_ram_gb": {"type": "number", "maximum": 5.5},
        "min_headroom_mb": {"type": "number", "minimum": 500}
    }
}

LIMITS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "BrainLimitsConfig",
    "type": "object",
    "required": ["local_llm", "local_model", "decay_days", "rule_max_chars", "max_ram_gb", "min_headroom_mb"],
    "properties": {
        "local_llm": {"type": "string"},
        "local_model": {"type": "string"},
        "frontier_models": {"type": "array", "items": {"type": "string"}},
        "decay_days": {"type": "integer", "minimum": 1},
        "decay_max_per_tick": {"type": "integer", "minimum": 1},
        "rule_max_chars": {"type": "integer"},
        "plugin_dir": {"type": "string"},
        "qdrant_url": {"type": "string"},
        "embedder_model": {"type": "string"},
        "embed_cache": {"type": "string"},
        "max_ram_gb": {"type": "number", "maximum": 5.5},
        "min_headroom_mb": {"type": "number", "minimum": 500}
    }
}

REGISTRY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "BrainNodeRegistry",
    "type": "object",
    "required": ["version", "total_nodes", "nodes"],
    "properties": {
        "version": {"type": "string"},
        "total_nodes": {"type": "integer"},
        "last_scan_utc": {"type": "string"},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "kind", "name", "desc", "path", "content_hash"],
                "properties": {
                    "id": {"type": "string"},
                    "kind": {"type": "string", "enum": ["skill", "rule", "tool", "memory", "agent", "pipeline", "schema"]},
                    "name": {"type": "string"},
                    "desc": {"type": "string"},
                    "path": {"type": "string"},
                    "content_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
}

CODE_GRAPH_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "BrainCodeGraph",
    "type": "object",
    "required": ["version", "nodes", "edges"],
    "properties": {
        "version": {"type": "string"},
        "nodes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "type", "label"],
                "properties": {
                    "id": {"type": "string"},
                    "type": {"type": "string"},
                    "label": {"type": "string"},
                    "metadata": {"type": "object"}
                }
            }
        },
        "edges": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source", "target", "relation"],
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relation": {"type": "string"}
                }
            }
        }
    }
}

TEAM_SOUL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SquadSoulProfile",
    "type": "object",
    "required": ["id", "name", "lead", "specialization", "dos", "donts", "memory_file"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "lead": {"type": "string"},
        "specialization": {"type": "string"},
        "dos": {"type": "array", "items": {"type": "string"}},
        "donts": {"type": "array", "items": {"type": "string"}},
        "memory_file": {"type": "string"},
        "capabilities": {"type": "array", "items": {"type": "string"}},
        "assigned_tools": {"type": "array", "items": {"type": "string"}}
    }
}


# ==============================================================================
# 2. DEFAULT TEMPLATE FACTORIES
# ==============================================================================

def get_default_vault_config(vault_path: str = "~/.brain-vault") -> Dict[str, Any]:
    """Returns the default vault_config.json conforming to VAULT_CONFIG_SCHEMA."""
    return {
        "vault_path": vault_path,
        "initialized": True,
        "version": "1.0.0",
        "permissions": "0700",
        "runtime_engine": "python",
        "bun_enabled": True,
        "graphify_enabled": True,
        "key_storage": {
            "backend": "local_encrypted",
            "bitwarden_status": False
        },
        "local_model": {
            "runner": "llama.cpp",
            "model_id": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
            "parameter_tier": "sub-1b",
            "tool_engine": "gemma2-embedded",
            "endpoint": "http://127.0.0.1:8080/v1",
            "llama_cpp_installed": True
        },
        "tool_engine": "gemma2-embedded",
        "embedder_model": "gemma2-embedded",
        "qdrant_url": "http://localhost:6333",
        "qdrant_collections": 16,
        "max_ram_gb": 5.5,
        "min_headroom_mb": 500
    }

def get_default_limits_config() -> Dict[str, Any]:
    """Returns the canonical limits.json resource configuration."""
    return {
        "local_llm": "http://127.0.0.1:8080/v1/chat/completions",
        "local_model": "Qwen/Qwen2.5-0.5B-Instruct-GGUF",
        "frontier_models": [
            "claude-3-7-sonnet",
            "deepseek-r1",
            "gpt-4o"
        ],
        "decay_days": 60,
        "decay_max_per_tick": 10,
        "rule_max_chars": 1800,
        "plugin_dir": "~/.brain-vault/skills",
        "qdrant_url": "http://localhost:6333",
        "embedder_model": "gemma2-embedded",
        "embed_cache": "~/.brain-vault/memory/embed_cache",
        "max_ram_gb": 5.5,
        "min_headroom_mb": 500
    }

def get_default_registry_json() -> Dict[str, Any]:
    """Returns baseline registry.json tracking foundational system nodes."""
    return {
        "version": "1.0.0",
        "total_nodes": 6,
        "last_scan_utc": "2026-10-10T00:00:00Z",
        "nodes": [
            {
                "id": "node-core-vault",
                "kind": "tool",
                "name": "VaultSandbox",
                "desc": "Local POSIX 0700 sovereign sandbox file store and permissions guard.",
                "path": "src/vault.py",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "dependencies": [],
                "tags": ["core", "security", "sandbox"]
            },
            {
                "id": "node-sanitizer",
                "kind": "tool",
                "name": "PrivacySanitizer",
                "desc": "Air-gap scrubber for 14 credential classes before cloud transmission.",
                "path": "src/sanitizer.py",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "dependencies": [],
                "tags": ["privacy", "credentials", "redactor"]
            },
            {
                "id": "node-prompt-guard",
                "kind": "tool",
                "name": "PromptGuard",
                "desc": "Neutralizer for jailbreaks, role spoofing, and delimiter escape attacks.",
                "path": "src/prompt_guard.py",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "dependencies": [],
                "tags": ["security", "injection", "defanger"]
            },
            {
                "id": "node-needle-engine",
                "kind": "pipeline",
                "name": "NeedleEngine",
                "desc": "Cactus Compute Needle 3 local function caller and sub-1B router.",
                "path": "src/needle.py",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "dependencies": ["node-sanitizer"],
                "tags": ["inference", "needle", "sub-1b"]
            },
            {
                "id": "node-preflight-engine",
                "kind": "tool",
                "name": "PreflightEngine",
                "desc": "Autonomous 7-system diagnostic and self-healing engine.",
                "path": "src/preflight.py",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "dependencies": ["node-core-vault", "node-needle-engine"],
                "tags": ["diagnostics", "self-healing", "preflight"]
            },
            {
                "id": "node-schemas",
                "kind": "schema",
                "name": "BrainSchemas",
                "desc": "System and brain schema specifications for validation and provisioning.",
                "path": "src/schemas.py",
                "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "dependencies": [],
                "tags": ["schemas", "validation", "architecture"]
            }
        ]
    }

def get_default_code_graph_json() -> Dict[str, Any]:
    """Returns baseline code_graph.json for structural routing."""
    return {
        "version": "1.0.0",
        "nodes": [
            {"id": "vault", "type": "module", "label": "Vault Sandbox", "metadata": {"permissions": "0700"}},
            {"id": "sanitizer", "type": "module", "label": "Privacy Sanitizer", "metadata": {"classes": 14}},
            {"id": "prompt_guard", "type": "module", "label": "Prompt Guard", "metadata": {"injection": "defang"}},
            {"id": "needle", "type": "engine", "label": "Cactus Needle 3 / Sub-1B", "metadata": {"tier": "sub-1b"}},
            {"id": "gemma2_tools", "type": "engine", "label": "Gemma 2 Embedded Tools", "metadata": {"role": "tools"}},
            {"id": "preflight", "type": "engine", "label": "Autonomous Preflight", "metadata": {"self_healing": True}}
        ],
        "edges": [
            {"source": "preflight", "target": "vault", "relation": "heals_permissions"},
            {"source": "preflight", "target": "needle", "relation": "verifies_readiness"},
            {"source": "needle", "target": "gemma2_tools", "relation": "dispatches_embedded_tools"},
            {"source": "vault", "target": "sanitizer", "relation": "scrubs_outbound_tokens"},
            {"source": "sanitizer", "target": "prompt_guard", "relation": "neutralizes_injections"}
        ]
    }


# ==============================================================================
# 3. PURE PYTHON VALIDATOR (ZERO EXTERNAL DEPENDENCY)
# ==============================================================================

def validate_schema(data: Any, schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates a Python data object against a canonical JSON Schema structure.
    Implements type checking, required properties, and bounds using Python stdlib.
    """
    if not isinstance(data, dict):
        return False, "Root payload must be a JSON object (dict)."

    # Check required fields
    required = schema.get("required", [])
    for req in required:
        if req not in data:
            return False, f"Missing required property: '{req}'."

    properties = schema.get("properties", {})
    for key, val in data.items():
        if key in properties:
            prop_def = properties[key]
            expected_type = prop_def.get("type")

            if expected_type == "string" and not isinstance(val, str):
                return False, f"Property '{key}' must be string, got {type(val).__name__}."
            elif expected_type == "integer" and not (isinstance(val, int) and not isinstance(val, bool)):
                return False, f"Property '{key}' must be integer, got {type(val).__name__}."
            elif expected_type == "number" and not (isinstance(val, (int, float)) and not isinstance(val, bool)):
                return False, f"Property '{key}' must be number, got {type(val).__name__}."
            elif expected_type == "boolean" and not isinstance(val, bool):
                return False, f"Property '{key}' must be boolean, got {type(val).__name__}."
            elif expected_type == "array" and not isinstance(val, list):
                return False, f"Property '{key}' must be array (list), got {type(val).__name__}."
            elif expected_type == "object" and not isinstance(val, dict):
                return False, f"Property '{key}' must be object (dict), got {type(val).__name__}."

            # Check enum
            if "enum" in prop_def and val not in prop_def["enum"]:
                return False, f"Property '{key}' has value '{val}' not in allowed enum: {prop_def['enum']}."

            # Check maximum / minimum for numbers
            if "maximum" in prop_def and isinstance(val, (int, float)) and val > prop_def["maximum"]:
                return False, f"Property '{key}' exceeds maximum allowed value {prop_def['maximum']}."
            if "minimum" in prop_def and isinstance(val, (int, float)) and val < prop_def["minimum"]:
                return False, f"Property '{key}' below minimum allowed value {prop_def['minimum']}."

            # Recursive validation for nested objects with required fields
            if expected_type == "object" and "required" in prop_def:
                sub_ok, sub_err = validate_schema(val, prop_def)
                if not sub_ok:
                    return False, f"Nested object '{key}' invalid: {sub_err}"

    return True, None
