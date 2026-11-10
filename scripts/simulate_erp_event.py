#!/usr/bin/env python3
"""CLI test script to simulate ERPNext invoice event to WhatsApp gateway."""

import httpx
import sys

GATEWAY_URL = "http://localhost:8080/erp-events/on-invoice-submitted"

payload = {
    "invoice_id": "ACC-SINV-2026-00042",
    "customer_name": "Sharma Textiles & Garments",
    "mobile_no": "919876543210",
    "grand_total": 84500.0,
    "due_date": "2026-11-25",
    "company_name": "Samwadini Enterprise Solutions",
    "pdf_url": "https://erp.example.com/api/v1/invoice/ACC-SINV-2026-00042.pdf"
}

print(f"Sending mock invoice event to {GATEWAY_URL}...")
try:
    with httpx.Client() as client:
        res = client.post(GATEWAY_URL, json=payload, timeout=5.0)
        print(f"Status Code: {res.status_code}")
        print("Response:", res.json())
except Exception as e:
    print(f"Connection error: {e}")
    sys.exit(1)
