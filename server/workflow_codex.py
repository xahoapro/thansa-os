"""Run restricted workflow steps on ChatGPT with file writes delegated to the gated hub."""
from __future__ import annotations

import json
import re

from claude_cli import CodexCLI, codex_sandbox_cho_mode

HEADER = "X-Thansa-Tool-Allowlist"
_FILE_TOOLS = {
    "Read": ("thansa_read_file",),
    "LS": ("thansa_list_dir",),
    "Glob": ("thansa_list_dir", "thansa_search_files"),
    "Grep": ("thansa_search_files",),
    "Write": ("thansa_write_file",),
    "Edit": ("thansa_edit_file",),
    "WebFetch": ("thansa_web_fetch",),
    "WebSearch": ("thansa_web_search",),
}


def hub_allowlist(allowed):
    """Translate the existing Claude allowlist without granting an unrestricted dispatcher."""
    names = set()
    for item in allowed:
        name = str(item)
        if name in _FILE_TOOLS:
            names.update(_FILE_TOOLS[name])
        elif name.startswith(("mcp__thansa__", "mcp__thansa-plugins__")):
            names.add(name.split("__", 2)[2])
        elif name.startswith("mcp__") and len(name.split("__", 2)) == 3:
            names.add(name[5:])
        else:
            raise ValueError("Restricted ChatGPT workflow cannot grant tool: " + name)
    return sorted(names)


def build(*, cwd, model, instructions, allowed, mode, apply_hub, extra_servers):
    """No Claude fallback and no native write/network escape from an explicit tool list."""
    if codex_sandbox_cho_mode("suggest") != "read-only":
        raise ValueError("Restricted ChatGPT workflow requires the read-only Codex sandbox")
    if any(not re.fullmatch(r"[A-Za-z0-9_-]+", name) for name in extra_servers):
        raise ValueError("Restricted ChatGPT workflow cannot safely disable an external MCP server name")
    names = hub_allowlist(allowed)
    cli = CodexCLI(cwd=cwd, tag="workflow", model=model, instructions=instructions)
    if not cli.is_available():
        raise ValueError("ChatGPT workflow requires the Codex CLI")
    apply_hub(cli, cwd)
    if not cli.profile or not cli.hub_turn:
        raise ValueError("Restricted ChatGPT workflow requires the Thansa MCP Hub")
    import mcp_hub
    cli.sandbox = "read-only"
    mcp_hub.dat_codex_mode(cli.extra_config, mode)
    mcp_hub.dat_codex_hub_bat_buoc(cli.extra_config)
    mcp_hub.dat_codex_tat_app(cli.extra_config)
    cli.extra_config += [
        "features.shell_tool=false", "features.multi_agent=false", "features.plugins=false",
        "features.browser_use=false", "features.browser_use_external=false",
        "features.computer_use=false", "features.image_generation=false", "features.goals=false",
        "features.skill_mcp_dependency_install=false", 'web_search="disabled"',
        "sandbox_workspace_write.network_access=false",
        'service_tier="default"',
        "mcp_servers.thansa.http_headers." + HEADER + "=" + json.dumps(json.dumps(names)),
    ]
    # Keep the owner's persistent MCP configuration intact. Servers outside the permissioned
    # hub are disabled only for this restricted workflow process.
    cli.extra_config += ["mcp_servers." + name + ".enabled=false" for name in extra_servers]
    if not any("*" in name for name in names):
        cli.extra_config.append("mcp_servers.thansa.enabled_tools=" + json.dumps(names))
    return cli
