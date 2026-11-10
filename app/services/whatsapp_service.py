"""Service for sending messages via Meta WhatsApp Cloud API."""

import logging
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.token = settings.WHATSAPP_TOKEN
        self.api_version = settings.META_GRAPH_VERSION
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        """Send a standard text message to recipient."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "text",
            "text": {"preview_url": True, "body": text},
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(self.base_url, headers=self.headers, json=payload)
            return res.json()

    async def send_interactive_buttons(self, recipient_phone: str, body_text: str, buttons: List[Dict[str, str]]) -> Dict[str, Any]:
        """Send interactive quick-reply buttons (e.g. Check Balance, View Invoice, Talk to Agent)."""
        button_components = [
            {
                "type": "reply",
                "reply": {"id": btn["id"], "title": btn["title"][:20]},
            }
            for btn in buttons[:3]
        ]

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": button_components},
            },
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(self.base_url, headers=self.headers, json=payload)
            return res.json()

    async def send_document(self, recipient_phone: str, doc_url: str, filename: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Send PDF document (e.g. Sales Invoice or Quotation PDF)."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "document",
            "document": {
                "link": doc_url,
                "filename": filename,
                "caption": caption or filename,
            },
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(self.base_url, headers=self.headers, json=payload)
            return res.json()
