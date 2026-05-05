from __future__ import annotations

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class BrowserTool(Tool):
    name = "browser"
    description = "Navigate, read, click, and type in a browser when Playwright is installed."

    def __init__(self, headless: bool = False) -> None:
        self.headless = headless
        self._playwright = None
        self._browser = None
        self._page = None

    async def run(self, operation: str, **params) -> ActionResult:
        if operation == "checkpoint":
            return ActionResult(False, requires_human=True, checkpoint=params.get("name", "browser_checkpoint"))
        try:
            await self._ensure()
            if operation == "navigate":
                await self._page.goto(params["url"], wait_until="domcontentloaded", timeout=30000)
                return ActionResult(True, output={"url": self._page.url})
            if operation == "read":
                text = await self._page.inner_text("body", timeout=5000)
                return ActionResult(True, output={"url": self._page.url, "text": text[:8000]})
            if operation == "click_text":
                await self._page.get_by_text(params["text"], exact=False).first.click(timeout=8000)
                return ActionResult(True, output={"clicked": params["text"]})
            if operation == "type":
                loc = self._page.locator(params["selector"]).first
                await loc.fill(params.get("text", ""), timeout=8000)
                return ActionResult(True, output={"selector": params["selector"]})
            if operation == "submit":
                await self._page.keyboard.press("Enter")
                return ActionResult(True, output={"submitted": True})
            if operation == "close":
                await self.close()
                return ActionResult(True, output={"closed": True})
            return ActionResult(False, error=f"Unknown browser operation: {operation}")
        except ImportError:
            return ActionResult(
                False,
                requires_human=True,
                checkpoint="browser_dependency",
                error="Playwright is not installed. Install mini-daburu-os[browser] and run playwright install chromium.",
            )
        except Exception as exc:
            msg = str(exc)
            if any(token in msg.lower() for token in ("captcha", "recaptcha", "hcaptcha")):
                return ActionResult(False, requires_human=True, checkpoint="captcha", error=msg)
            return ActionResult(False, error=msg)

    async def _ensure(self) -> None:
        if self._page:
            return
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._page = await self._browser.new_page()

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._playwright = None
        self._page = None
