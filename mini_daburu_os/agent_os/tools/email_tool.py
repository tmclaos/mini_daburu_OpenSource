from __future__ import annotations

import asyncio
import email
import imaplib
import re
import smtplib
from email.header import decode_header
from email.message import EmailMessage

from agent_os.schemas import ActionResult
from agent_os.tools.base import Tool
from agent_os.tools.vault import VaultTool


class EmailTool(Tool):
    name = "email"
    description = "Draft/send email and poll IMAP for verification codes."

    def __init__(self, vault: VaultTool | None = None) -> None:
        self.vault = vault
        self.drafts: list[dict] = []

    async def run(self, operation: str, **params) -> ActionResult:
        if operation == "draft":
            draft = {"to": params.get("to", ""), "subject": params.get("subject", ""), "body": params.get("body", "")}
            self.drafts.append(draft)
            return ActionResult(True, output=draft)
        if operation == "send":
            return await asyncio.to_thread(self._send, params)
        if operation == "wait_for_code":
            return await asyncio.to_thread(self._wait_for_code, params)
        return ActionResult(False, error=f"Unknown email operation: {operation}")

    def _send(self, params: dict) -> ActionResult:
        return ActionResult(False, requires_human=True, checkpoint="smtp_setup", error="SMTP sending is not configured in the minimal OS yet.")

    def _wait_for_code(self, params: dict) -> ActionResult:
        if not self.vault:
            return ActionResult(False, error="EmailTool needs VaultTool for IMAP credentials.")
        # Expected vault keys: imap_username, imap_password
        return ActionResult(
            False,
            requires_human=True,
            checkpoint="email_verification",
            error="Automatic IMAP polling is scaffolded. Use HumanTool for the verification code unless you extend this method.",
        )


def extract_code_from_text(text: str) -> str:
    match = re.search(r"\b(\d{4,8})\b", text)
    return match.group(1) if match else ""
