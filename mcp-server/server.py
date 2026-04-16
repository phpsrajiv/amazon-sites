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

  # Run (stdio transport — used by Claude Code / claude_desktop_config.json)
  python server.py

  # Or via the installed script
  sellerbuddy-mcp
"""

from mcp.server.fastmcp import FastMCP

from tools import seo, content, video_script, video_generator, social

mcp = FastMCP("SellerBuddy AI Agents")

# Register all agent tool groups
seo.register(mcp)
content.register(mcp)
video_script.register(mcp)
video_generator.register(mcp)
social.register(mcp)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
