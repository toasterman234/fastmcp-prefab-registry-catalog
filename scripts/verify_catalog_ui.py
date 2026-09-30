from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

from playwright.sync_api import Frame, Page, sync_playwright

DEV_PORT = int(os.environ.get("CATALOG_DEV_PORT", "9090"))
BASE_URL = f"http://127.0.0.1:{DEV_PORT}"
SCREENSHOT = Path(os.environ.get("CATALOG_SCREENSHOT", "/tmp/catalog-stage5.png"))


def find_app_frame(page: Page, timeout_seconds: float = 30.0) -> Frame:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        for frame in page.frames:
            try:
                if frame.get_by_text("Environment Catalog", exact=True).count():
                    return frame
            except Exception:
                pass
        time.sleep(0.25)
    raise AssertionError("Prefab app frame did not render Environment Catalog")


def assert_visible(frame: Frame, text: str) -> None:
    locator = frame.get_by_text(text, exact=True)
    if locator.count() == 0 or not locator.first.is_visible():
        raise AssertionError(f"Expected visible text: {text!r}")


def assert_not_visible(frame: Frame, text: str) -> None:
    locator = frame.get_by_text(text, exact=True)
    if locator.count() and locator.first.is_visible():
        raise AssertionError(f"Expected text to be filtered out: {text!r}")


def main() -> int:
    launch_url = BASE_URL + "/launch?" + urlencode({"tool": "catalog", "args": "{}"})

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.goto(launch_url, wait_until="domcontentloaded", timeout=30_000)

        app = find_app_frame(page)
        assert_visible(app, "Environment Catalog")
        assert_visible(app, "Everything (17)")

        skills_tab = app.get_by_role("tab", name="Skills (3)")
        skills_tab.click()
        assert_visible(app, "Browser Verification")
        assert_visible(app, "Root Cause Analysis")
        assert_visible(app, "Discovered Test")

        search = app.locator("input:visible").first
        if search.count() == 0:
            raise AssertionError("Expected a visible DataTable search input")

        search.fill("skill://discovered-test/SKILL.md")
        assert_visible(app, "Discovered Test")
        assert_not_visible(app, "Root Cause Analysis")

        search.fill("fastmcp-skills")
        assert_visible(app, "Discovered Test")
        assert_visible(app, "Browser Verification")

        SCREENSHOT.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SCREENSHOT), full_page=True)
        print(
            "BROWSER_VERIFY succeeded: real SKILL.md discovery, stable skill IDs, "
            f"available MCP resource interfaces, and catalog projection rendered; screenshot={SCREENSHOT}"
        )
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
