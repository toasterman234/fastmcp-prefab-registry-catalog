from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP("Federation Fixture")


@mcp.tool
def echo(value: str) -> str:
    """Echo a value through the proxied fixture server."""
    return f"echo:{value}"


@mcp.resource("fixture://info")
def fixture_info() -> str:
    """Return fixture resource content."""
    return "federation-fixture-resource"


@mcp.prompt
def review(topic: str) -> str:
    """Return a tiny prompt so prompt discovery is exercised."""
    return f"Review {topic} through the federation fixture."


if __name__ == "__main__":
    mcp.run()
