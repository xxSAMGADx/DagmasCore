#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Local Model Context Protocol (MCP) Server & Airlock App
Standard JSON-RPC 2.0 stdio MCP Server.
Allows any MCP-compatible client (Claude Desktop, Cursor, Open WebUI, DAGMAS, OpenAI wrappers)
to communicate directly with the local Brain Vault as native tools and resources.

Zero external dependencies - 100% Python Standard Library.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
from .vault import VaultSandbox, DEFAULT_VAULT_PATH
from .sanitizer import PrivacySanitizer
from .prompt_guard import PromptGuard
from .connectors import BrainVaultConnector
from .needle import NeedleEngine
from .boss_report import BossReportEngine
from .preflight import PreflightEngine

# Configure minimal stderr logger so stdin/stdout remain strictly pure JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("brain_vault_mcp")

SERVER_INFO = {
    "name": "brain-vault-mcp",
    "version": "1.0.0"
}

# Declarations of all tools exposed by the Brain Vault Local MCP App
MCP_TOOLS = [
    {
        "name": "vault_status",
        "description": "Checks the physical security status and 0700 permissions of the local ~/.brain-vault safe.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "sanitize_cloud_prompt",
        "description": "Airlock tool: redacts 14 classes of credentials (AWS, Stripe, DSNs, keys), defangs prompt injections, and trims context before sending to cloud models (Claude, OpenAI, Pi, Claw).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The prompt or message text to inspect and sanitize."
                },
                "platform": {
                    "type": "string",
                    "description": "Target cloud platform (claude, openai, dagmas, claw, pi). Default is claude.",
                    "default": "claude"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Max tokens to allow before pruning context to prevent cloud token overspend.",
                    "default": 1500
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "defang_prompt_injection",
        "description": "Detects and neutralizes prompt injections, jailbreaks (DAN mode), and instruction overrides.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze for prompt injection attacks."
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "local_route_task",
        "description": "Routes a task locally first using Needle Engine, checking if it can be fulfilled by free local automations ($0.00 cost) before escalating to paid cloud models.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Task description to plan and route."
                }
            },
            "required": ["task"]
        }
    },
    {
        "name": "daily_boss_report",
        "description": "Runs daily performance audit across subsidiary agent teams and updates memory DOs and DONTs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Lookback days for audit. Default is 1.",
                    "default": 1
                }
            },
            "required": []
        }
    },
    {
        "name": "run_preflight",
        "description": "Runs comprehensive system preflight diagnostic and autonomous self-healing across the vault sandbox (0700 permissions, config files, keystore, global rules, skills, and regression tests). If anything is broken or degraded, actively heals it and verifies recovery.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "auto_fix": {
                    "type": "boolean",
                    "description": "Whether to automatically heal and repair broken components on the fly. Defaults to true.",
                    "default": True
                }
            },
            "required": []
        }
    },
    {
        "name": "vault_hybrid_retrieve",
        "description": "Hybrid graph-augmented retrieval tool: fuses BM25 sparse keyword matching, dense vector cosine similarity, Reciprocal Rank Fusion (RRF), and code_graph.json directed edge traversal to recall past artifacts, schemas, and memory ledgers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Semantic search query or keywords."
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default: 5).",
                    "default": 5
                },
                "alpha": {
                    "type": "number",
                    "description": "Weight between dense vector (1.0) and sparse lexical (0.0). Default is 0.5.",
                    "default": 0.5
                }
            },
            "required": ["query"]
        }
    }
]



class BrainVaultMCPServer:
    """Standard Model Context Protocol Server over stdio."""

    def __init__(self, vault_path: str = DEFAULT_VAULT_PATH):
        self.vault = VaultSandbox(vault_path)
        self.sanitizer = PrivacySanitizer()
        self.prompt_guard = PromptGuard()
        self.connector = BrainVaultConnector(vault_path)
        self.needle = NeedleEngine()
        self.boss = BossReportEngine(vault_path)
        self.preflight = PreflightEngine(vault_path)


    def handle_request(self, req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processes a single JSON-RPC 2.0 request."""
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": SERVER_INFO
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": MCP_TOOLS
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            try:
                result_content = self.execute_tool(tool_name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_content, indent=2)
                            }
                        ],
                        "isError": False
                    }
                }
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error executing {tool_name}: {str(e)}"
                            }
                        ],
                        "isError": True
                    }
                }

        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            }

        else:
            if req_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            return None

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Dispatches tool execution to Brain Vault local components."""
        if name == "vault_status":
            return self.vault.status()

        elif name == "sanitize_cloud_prompt":
            text = args.get("text", "")
            platform = args.get("platform", "claude")
            max_tokens = int(args.get("max_tokens", 1500))
            return self.connector.sanitize_for_cloud(text, platform=platform, max_tokens=max_tokens)

        elif name == "defang_prompt_injection":
            text = args.get("text", "")
            is_inj, findings = self.prompt_guard.detect(text)
            scrubbed = self.prompt_guard.scrub(text)
            return {
                "is_injection": is_inj,
                "findings": findings,
                "defanged_text": scrubbed
            }

        elif name == "local_route_task":
            task = args.get("task", "")
            return self.needle.plan(task)

        elif name == "daily_boss_report":
            days = int(args.get("days", 1))
            report = self.boss.generate_report(days=days)
            return report

        elif name == "run_preflight":
            auto_fix = bool(args.get("auto_fix", True))
            return self.preflight.run_all(auto_fix=auto_fix)

        elif name == "vault_hybrid_retrieve":
            query = args.get("query", "")
            limit = int(args.get("limit", 5))
            alpha = float(args.get("alpha", 0.5))
            include_neighbors = bool(args.get("include_graph_neighbors", True))
            return self.vault.hybrid_retrieve(
                query=query,
                limit=limit,
                alpha=alpha,
                include_graph_neighbors=include_neighbors
            )

        else:
            raise ValueError(f"Unknown tool: {name}")


    def run_stdio(self):
        """Standard IO loop for JSON-RPC MCP clients."""
        logger.info("Brain Vault MCP Server listening on stdio...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                res = self.handle_request(req)
                if res is not None:
                    sys.stdout.write(json.dumps(res) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"Invalid JSON received: {e}")


if __name__ == "__main__":
    server = BrainVaultMCPServer()
    server.run_stdio()
