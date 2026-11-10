"""WhatsApp Webhook verification and incoming message handler."""

import logging
from fastapi import APIRouter, Request, Response, Query, BackgroundTasks
from app.config import settings
from app.services.erpnext_service import ERPNextService
from app.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])

erpnext_service = ERPNextService()
whatsapp_service = WhatsAppService()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Meta webhook verification endpoint."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)


async def process_incoming_message(body: dict):
    """Background task to parse and respond to customer WhatsApp inquiries."""
    try:
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    sender = msg.get("from")
                    msg_type = msg.get("type")
                    text_content = ""

                    if msg_type == "text":
                        text_content = msg.get("text", {}).get("body", "").strip()
                    elif msg_type == "interactive":
                        text_content = msg.get("interactive", {}).get("button_reply", {}).get("id", "")

                    if not sender:
                        continue

                    logger.info(f"Received WhatsApp from {sender}: {text_content}")

                    # 1. Log communication in ERPNext
                    await erpnext_service.log_communication(phone=sender, message=text_content, direction="Received")

                    # 2. Look up customer in ERPNext
                    customer = await erpnext_service.get_customer_by_phone(sender)
                    customer_name = customer.get("customer_name") if customer else "Valued Customer"

                    # 3. Intelligent Quick Responses
                    lower_msg = text_content.lower()
                    if lower_msg in ("hi", "hello", "namaste", "start"):
                        buttons = [
                            {"id": "btn_balance", "title": "Check Balance"},
                            {"id": "btn_invoice", "title": "Latest Invoice"},
                            {"id": "btn_support", "title": "Speak to Support"},
                        ]
                        await whatsapp_service.send_interactive_buttons(
                            recipient_phone=sender,
                            body_text=f"Namaste {customer_name}! 🙏\nWelcome to our self-service portal. What would you like to check today?",
                            buttons=buttons,
                        )

                    elif lower_msg == "btn_balance" or "balance" in lower_msg:
                        if customer:
                            balance = customer.get("outstanding_amount", 0.0)
                            await whatsapp_service.send_text_message(
                                recipient_phone=sender,
                                text=f"📊 *Outstanding Balance Summary*\nAccount: {customer_name}\nPending Amount: ₹{balance:,.2f}",
                            )
                        else:
                            await whatsapp_service.send_text_message(
                                recipient_phone=sender,
                                text="Sorry, your mobile number is not registered with any customer profile. Please contact accounts.",
                            )

                    elif lower_msg == "btn_invoice" or "invoice" in lower_msg:
                        invoice = await erpnext_service.get_latest_sales_invoice(customer_name) if customer else None
                        if invoice:
                            await whatsapp_service.send_text_message(
                                recipient_phone=sender,
                                text=f"🧾 *Latest Sales Invoice*\nInvoice No: #{invoice['name']}\nDate: {invoice['posting_date']}\nAmount: ₹{invoice['grand_total']:,.2f}\nStatus: {invoice['status']}",
                            )
                        else:
                            await whatsapp_service.send_text_message(
                                recipient_phone=sender,
                                text="No recent invoices found for your account.",
                            )

                    elif lower_msg == "btn_support" or "support" in lower_msg:
                        await whatsapp_service.send_text_message(
                            recipient_phone=sender,
                            text="👩‍💼 An executive has been notified and will assist you shortly. You may also reply with your inquiry.",
                        )

    except Exception as e:
        logger.error(f"Error handling WhatsApp message: {e}", exc_info=True)


@router.post("")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """Receive incoming WhatsApp messages."""
    payload = await request.json()
    background_tasks.add_task(process_incoming_message, payload)
    return {"status": "received"}
