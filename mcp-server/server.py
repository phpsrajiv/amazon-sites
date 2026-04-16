"""
SellerBuddy AI Agents — MCP Server

Umbrella MCP server that exposes all SellerBuddy AI agents as Claude tools.
All current and future amazon-sites AI agents are registered here.

Agents:
  - SEO Agent          (http://localhost:8001)
  - Content Writer     (http://localhost:8002)
  - Video Script       (http://localhost:8003)
  - Video Generator    (http://localhost:8004)
  - Social Media       (http://localhost:8005)

Usage:
  # Install
  pip install -e .

  # Run locally (stdio transport — used by Claude Code / claude_desktop_config.json)
  python server.py

  # Run in Docker (SSE transport on port 8006)
  MCP_TRANSPORT=sse python server.py

  # Or via the installed script
  sellerbuddy-mcp
"""

import os

from mcp.server.fastmcp import FastMCP

from tools import seo, content, video_script, video_generator, social

mcp = FastMCP(
    "SellerBuddy AI Agents",
    host="0.0.0.0",
    port=int(os.getenv("MCP_PORT", "8006")),
)

# Register all agent tool groups
seo.register(mcp)
content.register(mcp)
video_script.register(mcp)
video_generator.register(mcp)
social.register(mcp)


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
