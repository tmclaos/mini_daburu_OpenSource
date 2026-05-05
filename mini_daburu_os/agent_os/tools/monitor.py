from __future__ import annotations

import time
import urllib.request

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool


class MonitorTool(Tool):
    name = "monitor"
    description = "Check uptime and record simple business metrics."

    def __init__(self) -> None:
        self.metrics: list[dict] = []

    async def run(self, operation: str, **params) -> ActionResult:
        if operation == "uptime":
            url = params["url"]
            started = time.monotonic()
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    status = response.status
                ok = 200 <= status < 400
                latency_ms = int((time.monotonic() - started) * 1000)
                return ActionResult(ok, output={"url": url, "status": status, "latency_ms": latency_ms})
            except Exception as exc:
                return ActionResult(False, error=str(exc))
        if operation == "record":
            item = {
                "metric": params["metric"],
                "value": float(params.get("value", 0)),
                "label": params.get("label", ""),
            }
            self.metrics.append(item)
            return ActionResult(True, output=item)
        if operation == "summary":
            totals: dict[str, float] = {}
            for item in self.metrics:
                totals[item["metric"]] = totals.get(item["metric"], 0.0) + item["value"]
            return ActionResult(True, output={"totals": totals, "events": len(self.metrics)})
        return ActionResult(False, error=f"Unknown monitor operation: {operation}")
