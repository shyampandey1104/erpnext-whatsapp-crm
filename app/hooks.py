# Copyright (c) 2026, Shyamkumar Pandey and contributors
# For license information, please see license.txt

app_name = "app"
app_title = "Erpnext Whatsapp Crm"
app_publisher = "Shyamkumar Pandey"
app_description = "Erpnext Whatsapp Crm for Frappe and ERPNext"
app_email = "shyampandey1104@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_css = "/assets/app/css/app.bundle.css"
app_include_js = "/assets/app/js/app.bundle.js"

# Document Events
# ---------------
doc_events = {
    "DocType Event": {
        "on_submit": "app.engine.on_document_submit",
        "on_cancel": "app.engine.on_document_cancel"
    }
}

# Scheduled Tasks
# ---------------
scheduler_events = {
    "daily": [
        "app.engine.daily_scheduled_sync"
    ]
}
