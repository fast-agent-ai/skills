# README.md Template for HF Spaces

This is the complete README.md template for deploying fast-agent to Hugging Face Spaces.

## Template

```markdown
---
title: fast-agent MCP Deployment
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Fast Agent on Hugging Face Spaces

This Space runs [fast-agent](https://fast-agent.ai/) as an MCP server.

## Configuration

This Space includes:
- Agent card(s) defining the agent's capabilities
- Python tool files for custom functionality
- Environment-based configuration for API keys

## Usage

Once running, the agent is accessible via HTTP API at the Space URL.

## YAML Frontmatter Fields

### Required Fields

- `title`: Display name for the Space (appears in Space listing).
- `sdk: docker` - Must be set to `docker` for Docker Spaces
- `app_port: 7860` - Port the application listens on (HF Spaces default)

### Optional Fields

- `emoji`: Emoji icon for the Space (e.g., 🤖, 🚀, 💬)
- `colorFrom`: Starting gradient color (blue, red, green, yellow, purple, etc.)
- `colorTo`: Ending gradient color
- `pinned`: Set to `true` to pin at top of your profile
- `license`: License identifier (e.g., `mit`, `apache-2.0`)
- `short_description`: Brief description shown in thumbnail

## Examples

### Minimal README

```markdown
---
title: My Agent
sdk: docker
app_port: 7860
---

# My Agent

Fast-agent MCP server.
```

### Full README

```markdown
---
title: Advanced AI Assistant
emoji: 🧠
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
license: mit
short_description: Advanced AI assistant with custom tools
---

# Advanced AI Assistant

This Space runs a custom fast-agent configuration with multiple specialized tools.

## Features

- Natural language processing
- API integration
- Custom workflows

## Environment Variables

Configure these in Space Settings:
- `OPENAI_API_KEY`: OpenAI API key
- `HF_TOKEN`: Hugging Face token
- `FAST_AGENT_SERVE_OAUTH`: Set to `hf` to enable OAuth token authentication
- `FAST_AGENT_OAUTH_SCOPES`: Required scopes (default: `access`)

## Usage

Send requests to the Space URL to interact with the agent.
```
