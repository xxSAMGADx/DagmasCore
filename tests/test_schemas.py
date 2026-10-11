import unittest
from src.schemas import (
    validate_schema,
    VAULT_CONFIG_SCHEMA,
    LIMITS_SCHEMA,
    REGISTRY_SCHEMA,
    CODE_GRAPH_SCHEMA,
    TEAM_SOUL_SCHEMA,
    get_default_vault_config,
    get_default_limits_config,
    get_default_registry_json,
    get_default_code_graph_json
)

class TestBrainSchemas(unittest.TestCase):
    def test_default_vault_config_valid(self):
        cfg = get_default_vault_config()
        ok, err = validate_schema(cfg, VAULT_CONFIG_SCHEMA)
        self.assertTrue(ok, f"Vault config failed validation: {err}")

    def test_default_limits_config_valid(self):
        limits = get_default_limits_config()
        ok, err = validate_schema(limits, LIMITS_SCHEMA)
        self.assertTrue(ok, f"Limits config failed validation: {err}")

    def test_default_registry_json_valid(self):
        registry = get_default_registry_json()
        ok, err = validate_schema(registry, REGISTRY_SCHEMA)
        self.assertTrue(ok, f"Registry failed validation: {err}")

    def test_default_code_graph_json_valid(self):
        graph = get_default_code_graph_json()
        ok, err = validate_schema(graph, CODE_GRAPH_SCHEMA)
        self.assertTrue(ok, f"Code graph failed validation: {err}")

    def test_team_soul_schema_valid(self):
        squad = {
            "id": "team-engineering",
            "name": "Engineering Squad",
            "lead": "Kaelen Drake",
            "specialization": "Software & Microservices",
            "dos": ["Enforce exit code 0", "Verify unit tests"],
            "donts": ["Never bypass security gates"],
            "memory_file": "engineering_memory.json"
        }
        ok, err = validate_schema(squad, TEAM_SOUL_SCHEMA)
        self.assertTrue(ok, f"Team soul profile failed validation: {err}")

    def test_schema_catches_missing_required_property(self):
        cfg = get_default_vault_config()
        del cfg["max_ram_gb"]
        ok, err = validate_schema(cfg, VAULT_CONFIG_SCHEMA)
        self.assertFalse(ok)
        self.assertIn("Missing required property: 'max_ram_gb'", err)

    def test_schema_catches_type_mismatch(self):
        cfg = get_default_vault_config()
        cfg["vault_path"] = 12345  # Must be string
        ok, err = validate_schema(cfg, VAULT_CONFIG_SCHEMA)
        self.assertFalse(ok)
        self.assertIn("must be string", err)

    def test_schema_catches_ram_bound_violation(self):
        cfg = get_default_vault_config()
        cfg["max_ram_gb"] = 16.0  # Hard ceiling is 5.5 GB
        ok, err = validate_schema(cfg, VAULT_CONFIG_SCHEMA)
        self.assertFalse(ok)
        self.assertIn("exceeds maximum allowed value 5.5", err)

if __name__ == "__main__":
    unittest.main()
