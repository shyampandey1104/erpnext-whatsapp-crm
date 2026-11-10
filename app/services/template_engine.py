"""Dynamic Jinja2 notification template engine for ERPNext business events."""

from jinja2 import Template
from typing import Dict, Any

TEMPLATES = {
    "sales_invoice_created": """*Namaste {{ customer_name }},* 🙏

Your invoice *#{{ invoice_id }}* has been generated for amount *₹{{ amount }}*.
Due Date: {{ due_date }}

You can download your official tax invoice using the link below:
📄 {{ pdf_url }}

For any queries, reply directly to this message.
Thank you for choosing {{ company_name }}!""",

    "payment_reminder": """*Friendly Payment Reminder* ⏰

Dear {{ customer_name }},
An outstanding balance of *₹{{ balance }}* is pending for Invoice *#{{ invoice_id }}*.
Kindly process payment to ensure uninterrupted service.

Quick UPI / Payment Link:
💳 {{ payment_link }}

Thank you!""",

    "dispatch_notification": """*Good News! Your Order is Dispatched 🚚*

Hi {{ customer_name }},
Your Delivery Note *#{{ delivery_id }}* containing {{ item_count }} item(s) has been dispatched via {{ transporter }}.
LR / Tracking Number: *{{ tracking_no }}*

Track status: {{ tracking_url }}""",

    "crm_welcome": """*Welcome to {{ company_name }}!* 👋

Hello {{ customer_name }}, how can we help you today?
Select an option below or type your inquiry directly."""
}


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render a notification template with contextual data."""
    raw_template = TEMPLATES.get(template_name)
    if not raw_template:
        raise ValueError(f"Template '{template_name}' not found.")
    template = Template(raw_template)
    return template.render(**context)
