"""ERPNext Document Event Webhook Listeners."""

import logging
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.whatsapp_service import WhatsAppService
from app.services.template_engine import render_template
from app.services.erpnext_service import ERPNextService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/erp-events", tags=["ERPNext Events"])

whatsapp_service = WhatsAppService()
erpnext_service = ERPNextService()


class InvoiceEventPayload(BaseModel):
    invoice_id: str
    customer_name: str
    mobile_no: str
    grand_total: float
    due_date: str
    company_name: str
    pdf_url: Optional[str] = None


class DispatchEventPayload(BaseModel):
    delivery_id: str
    customer_name: str
    mobile_no: str
    transporter: str
    tracking_no: str
    item_count: int
    tracking_url: Optional[str] = "https://track.example.com"


@router.post("/on-invoice-submitted")
async def on_invoice_submitted(payload: InvoiceEventPayload, background_tasks: BackgroundTasks):
    """Triggered by ERPNext Server Script when a Sales Invoice is submitted."""
    logger.info(f"Triggered invoice alert for {payload.customer_name} ({payload.mobile_no})")

    context = {
        "customer_name": payload.customer_name,
        "invoice_id": payload.invoice_id,
        "amount": f"{payload.grand_total:,.2f}",
        "due_date": payload.due_date,
        "company_name": payload.company_name,
        "pdf_url": payload.pdf_url or "https://erp.example.com",
    }
    msg_body = render_template("sales_invoice_created", context)

    # Dispatch WhatsApp in background
    background_tasks.add_task(
        whatsapp_service.send_text_message,
        recipient_phone=payload.mobile_no,
        text=msg_body,
    )
    background_tasks.add_task(
        erpnext_service.log_communication,
        phone=payload.mobile_no,
        message=msg_body,
        direction="Sent",
        reference_doctype="Sales Invoice",
        reference_name=payload.invoice_id,
    )
    return {"status": "dispatched", "invoice": payload.invoice_id}


@router.post("/on-delivery-dispatched")
async def on_delivery_dispatched(payload: DispatchEventPayload, background_tasks: BackgroundTasks):
    """Triggered by ERPNext Server Script on Delivery Note dispatch."""
    context = {
        "customer_name": payload.customer_name,
        "delivery_id": payload.delivery_id,
        "transporter": payload.transporter,
        "tracking_no": payload.tracking_no,
        "item_count": payload.item_count,
        "tracking_url": payload.tracking_url,
    }
    msg_body = render_template("dispatch_notification", context)

    background_tasks.add_task(
        whatsapp_service.send_text_message,
        recipient_phone=payload.mobile_no,
        text=msg_body,
    )
    return {"status": "dispatched", "delivery": payload.delivery_id}
