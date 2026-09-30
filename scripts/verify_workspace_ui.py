from __future__ import annotations

import os

from playwright.sync_api import sync_playwright


def main() -> None:
    port = os.environ.get("WORKSPACE_PORT", "3000")
    url = f"http://127.0.0.1:{port}/"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(url, wait_until="networkidle")
        page.get_by_text("MCP: 1/1 available", exact=False).wait_for(state="visible")

        page.get_by_test_id("nav-apps").click()
        page.get_by_test_id("app-surface-catalog").wait_for(state="visible")
        gen = page.get_by_test_id("app-surface-generative")
        gen.click()

        frame = page.locator('iframe[title="FastMCP Generative UI"]')
        frame.wait_for()
        src = frame.get_attribute("src") or ""
        assert "tool=generate_prefab_ui" in src, src

        context = page.locator(".app-context").inner_text()
        assert "generate_prefab_ui" in context
        assert "search_prefab_components" in context

        screenshot = "/tmp/workspace-stage7.png"
        page.screenshot(path=screenshot, full_page=True)
        browser.close()

    print(
        "WORKSPACE_VERIFY succeeded: live MCP federation status plus Catalog/Generative UI Apps rendered; "
        f"generated UI iframe={src}; screenshot={screenshot}"
    )


if __name__ == "__main__":
    main()
