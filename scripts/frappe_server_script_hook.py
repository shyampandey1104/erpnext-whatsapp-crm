"""Frappe Server Script Hook.

Paste this into ERPNext:
Settings -> Server Script -> New Server Script
- Reference DocType: Sales Invoice
- Script Type: DocType Event
- DocType Event: on_submit
"""

# Fetch customer details
customer_doc = frappe.get_doc("Customer", doc.customer)
mobile_no = customer_doc.mobile_no or doc.contact_mobile

if mobile_no:
    import json
    import requests

    gateway_url = "http://your-whatsapp-gateway:8080/erp-events/on-invoice-submitted"
    payload = {
        "invoice_id": doc.name,
        "customer_name": doc.customer_name,
        "mobile_no": str(mobile_no).replace(" ", "").replace("-", ""),
        "grand_total": float(doc.grand_total),
        "due_date": str(doc.due_date),
        "company_name": doc.company,
        "pdf_url": f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={doc.name}&format=Standard"
    }

    try:
        # Asynchronously send webhook event to WhatsApp CRM Gateway
        frappe.enqueue(
            method="requests.post",
            url=gateway_url,
            json=payload,
            timeout=10,
            now=False
        )
    except Exception as e:
        frappe.log_error(f"WhatsApp notification trigger failed: {e}", "WhatsApp Gateway")
