# Connecting the Senzing MCP: setup help & troubleshooting

> **Heads-up:** assistant UIs change fast, so any exact clicks below (dated **August 2026**) may look different in your version. The always-current move is to **ask your assistant** - "how do I add an MCP server?" or "how do I allow a domain for code execution?" - it knows its own current setup.

## Ask your assistant first

For almost anything here, the quickest fix is to ask the assistant itself:

- **Add the MCP:** paste `Add the Senzing MCP server at https://mcp.senzing.com/mcp` - or ask "how do I add an MCP server?"
- **Allow downloads:** ask "how do I allow the domain `mcp.senzing.com` for your code execution?"

## Something not working? Check these two things

Almost every setup problem is one of two failure modes:

**1. The assistant can't see any Senzing tools** → the **connector** isn't added.
Fix: add it in the assistant's MCP / connector settings using `https://mcp.senzing.com/mcp` (no authentication), or ask the assistant how. Claude Desktop specifics are below.

**2. The tools work, but a recipe stalls when it installs Senzing or downloads data** → the assistant's **code sandbox can't reach `mcp.senzing.com`**.
You'll see a `403`, a DNS error, or a timeout. Fix: allow `mcp.senzing.com` in the assistant's network / code-execution settings (Claude Desktop specifics below), or ask the assistant how. If it still fails after that, the block is your **network** (a corporate firewall or proxy) - see the next section.

These are independent: the connector is routed from the assistant's servers, so it can work even while the sandbox's downloads are blocked.

## Behind a corporate firewall or proxy?

In a managed / corporate environment, downloads can be blocked at **two layers** - and both have to allow the traffic:

1. **Your assistant's own egress setting** (for example, Claude Desktop's domain allowlist - see below).
2. **Your corporate network** - a firewall or proxy can block the domain even after the assistant is set up correctly.

So if downloads still fail once you've allowed it in the assistant, it's the network. Ask IT / your network admin to allow outbound HTTPS (port 443) to:

- **`mcp.senzing.com`** - the MCP server, plus the Senzing SDK / package downloads and workflow resources.
- **`senzing.com`** - some dataset (CORD) downloads are served from here.

**Using an HTTPS proxy?** Make sure the assistant's code-execution environment is pointed at it (e.g. via the `HTTPS_PROXY` variable) so its downloads route through the proxy rather than getting refused.

**Reading the error:** a `403` (blocked-by-allowlist) usually means the assistant's own setting; a **timeout, connection refused, or DNS failure** usually means the corporate network or proxy.

## Browser tools won't work

Web assistants (**claude.ai**, **chatgpt.com**, and similar) can add the connector, but they **can't be configured to let their sandbox download from `senzing.com`** - so recipes stall on install with no fix. Use a **desktop app or IDE tool** instead (Claude Code, Claude Desktop, Cursor, VS Code, Windsurf, and so on).

---

## Claude Desktop app

Two settings matter, both under Claude Desktop's **Settings**:
- the **connector** - adds the Senzing tools (URL `https://mcp.senzing.com/mcp`, no authentication);
- the **code-execution domain allowlist** - lets Claude's sandbox reach `mcp.senzing.com`; needed only for recipes that install or download.

The exact place for each moves around as the app updates, so for where they live right now, ask Claude ("how do I add an MCP server?" / "how do I allow a domain for code execution?") or check Anthropic's docs below.

**Good to know** (two non-obvious ones):
- **Domain-allowlist changes apply to new conversations only** - start a fresh chat after saving.
- **Known bug:** an allowed domain sometimes still returns `403` even when set correctly. If it fails after a fresh session, that's a reported issue, not your mistake.

**Authoritative, up-to-date docs (Anthropic):**
- [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [Create and edit files with Claude](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) (covers code execution and network egress)
