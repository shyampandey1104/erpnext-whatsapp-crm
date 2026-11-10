"""Unit tests for Jinja2 template rendering."""

from app.services.template_engine import render_template


def test_render_invoice_template():
    context = {
        "customer_name": "Ramesh Kumar",
        "invoice_id": "SINV-00123",
        "amount": "12,450.00",
        "due_date": "2026-11-20",
        "company_name": "Acme Corp",
        "pdf_url": "https://erp.example.com/invoice.pdf",
    }
    rendered = render_template("sales_invoice_created", context)
    assert "Namaste Ramesh Kumar" in rendered
    assert "SINV-00123" in rendered
    assert "₹12,450.00" in rendered
    assert "Acme Corp" in rendered


def test_render_dispatch_template():
    context = {
        "customer_name": "Ananya Traders",
        "delivery_id": "DN-0099",
        "transporter": "Blue Dart Express",
        "tracking_no": "BD8899123",
        "item_count": 5,
        "tracking_url": "https://bluedart.com/track",
    }
    rendered = render_template("dispatch_notification", context)
    assert "DN-0099" in rendered
    assert "Blue Dart Express" in rendered
    assert "BD8899123" in rendered
