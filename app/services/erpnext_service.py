"""Service for communicating with ERPNext / Frappe REST API."""

import logging
from typing import Any, Dict, Optional, List
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class ERPNextService:
    def __init__(self):
        self.base_url = settings.ERPNEXT_URL.rstrip("/")
        self.headers = {
            "Authorization": f"token {settings.ERPNEXT_API_KEY}:{settings.ERPNEXT_API_SECRET}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_customer_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Look up customer in ERPNext by mobile number."""
        clean_phone = phone.replace("+", "").strip()[-10:]
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Query ERPNext Customer
                url = f"{self.base_url}/api/resource/Customer"
                params = {
                    "filters": f'[["mobile_no", "like", "%{clean_phone}%"]]',
                    "fields": '["name", "customer_name", "customer_group", "territory", "outstanding_amount"]',
                    "limit_page_length": "1",
                }
                res = await client.get(url, headers=self.headers, params=params)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    return data[0] if data else None
            except Exception as e:
                logger.error(f"Error fetching customer from ERPNext: {e}")
        return None

    async def get_latest_sales_invoice(self, customer_name: str) -> Optional[Dict[str, Any]]:
        """Fetch the most recent submitted Sales Invoice for a customer."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                url = f"{self.base_url}/api/resource/Sales Invoice"
                params = {
                    "filters": f'[["customer", "=", "{customer_name}"], ["docstatus", "=", 1]]',
                    "fields": '["name", "posting_date", "grand_total", "outstanding_amount", "status"]',
                    "order_by": "posting_date desc",
                    "limit_page_length": "1",
                }
                res = await client.get(url, headers=self.headers, params=params)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    return data[0] if data else None
            except Exception as e:
                logger.error(f"Error fetching invoice from ERPNext: {e}")
        return None

    async def log_communication(self, phone: str, message: str, direction: str = "Received", reference_doctype: Optional[str] = None, reference_name: Optional[str] = None) -> bool:
        """Create a Frappe 'Communication' record so chats appear on the timeline."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                payload = {
                    "communication_type": "Communication",
                    "communication_medium": "WhatsApp",
                    "sent_or_received": direction,
                    "sender": phone if direction == "Received" else "System",
                    "recipients": phone if direction == "Sent" else "System",
                    "content": message,
                    "subject": f"WhatsApp {direction}: {phone}",
                    "reference_doctype": reference_doctype,
                    "reference_name": reference_name,
                }
                url = f"{self.base_url}/api/resource/Communication"
                res = await client.post(url, headers=self.headers, json=payload)
                return res.status_code in (200, 201)
            except Exception as e:
                logger.error(f"Failed to log communication in ERPNext: {e}")
                return False
