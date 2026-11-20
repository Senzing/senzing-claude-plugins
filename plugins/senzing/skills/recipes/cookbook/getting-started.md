# Get Started

One-time setup: use an AI coding assistant, connect the **Senzing MCP** (the standard way AI assistants plug into outside tools), and grab a free Senzing license. Do it once, then every recipe is paste-and-cook.

## 1. Use an AI coding assistant

Any assistant that supports MCP works - **Claude Code**, **Claude Desktop**, **VS Code (GitHub Copilot)**, **Cursor**, **ChatGPT Desktop & Codex**, **Windsurf**, or **Amazon Kiro** - so if you already have one, you're set. New to this? The recipes were built and demoed with **Claude**, so the **Claude Desktop** app is the easiest start - or **Amazon Kiro** for the AWS recipes (Amazon's assistant, with Senzing built in).

> ⚠️ **A desktop or IDE assistant, not a browser tab.** Web assistants (**claude.ai**, **chatgpt.com**, and the like) can add the Senzing MCP, but they can't be set up to let their sandbox download from `senzing.com` - so recipes stall the moment they try to install Senzing. The apps and IDE tools above can.

- **Use a paid plan.** The free tiers won't run these assistants (e.g. Claude's free tier won't run Claude Code).
- **Use the most capable model.** Recipes do real, multi-step engineering, so pick your assistant's deepest "thinking" model, not a fast or cheap one. For **Claude** that's **Opus**; for **ChatGPT**, its top reasoning model; and the equivalent for the rest.

## 2. Connect the Senzing MCP

How you connect depends on your assistant.

**Claude Desktop app** - the paste prompt doesn't add it here, so use the app's settings (two things):
- **Tools:** Settings → Connectors → **Add custom connector**, URL `https://mcp.senzing.com/mcp` (no authentication).
- **Downloads** (for recipes that install or download): Settings → Capabilities → Code execution → **Domain allowlist**, add `mcp.senzing.com`.

More detail, caveats, and firewall help: **[Setup help & troubleshooting](mcp-setup-troubleshooting.md)**.

**Amazon Kiro** - it's built in: install the **Senzing Power** in one click from **[kiro.dev/launch/powers/senzing](https://kiro.dev/launch/powers/senzing)** (or pick **Senzing** from Kiro's *Add a Power* list).

**Any other assistant** (Claude Code, Cursor, VS Code, Windsurf, and most others) - just tell it (paste this):

```
Add the Senzing MCP server at https://mcp.senzing.com/mcp
```

Most add it right from that prompt. If yours doesn't, add it in its MCP / connector settings with the same URL (no authentication), or **ask it "how do I add an MCP server?"** - its UI changes faster than any guide.

## 3. Check it works

Two quick checks before you cook.

**1. Are the Senzing tools there?** *(the connector)* Ask your assistant:

```
List your Senzing MCP tools, then search the Senzing docs for "entity resolution".
```

Tools listed and a result back = connected. **No Senzing tools?** The connector didn't take - redo step 2 (add it in settings, or ask your assistant how).

**2. Can it download from Senzing?** *(the network)* Recipes pull the Senzing SDK and data from `mcp.senzing.com` - test it:

```
Use the Senzing MCP's download_resource tool to download the entity spec, and tell me if it was blocked.
```

It downloads = you're set. **Blocked?** That's a network or firewall block - see **[Setup help & troubleshooting](mcp-setup-troubleshooting.md)** to fix it.

## 4. Get a Senzing license

With the MCP connected, tell your assistant (paste this):

```
Email me a free Senzing license
```

It emails a free 10-day, 250K-record evaluation license to your **work email**. Download the license file from your inbox - keep it handy, and when a recipe asks for it, **attach it to the chat** (or drop it in your assistant's working folder).

## You're ready to cook

That's the one-time setup - you won't repeat it. From here, every recipe is just pick and paste. Your **first** run will be slower, though - expect a few approval prompts and some one-time installs, so give it extra time.

**[Browse the recipes →](cookbook.md)**
