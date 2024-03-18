import frappe
import json
from frappe.utils import get_site_name
from werkzeug.wrappers import Response

# Fetch settings from Frappe
settings = frappe.get_doc("Facebook Page Settings", "Facebook Page Settings")
access_token = settings.get_password("access_token")
app_secret = settings.get_password("app_secret")
page_id = settings.page_id
verify_token = settings.verify_token
url = f"https://graph.facebook.com/v19.0/{page_id}/subscribed_apps"

# Function to handle webhook verification
@frappe.whitelist(allow_guest=True)
def verify_webhook():
    verify = frappe.db.get_single_value("Facebook Page Settings", "verify_token")
    hub_challenge = frappe.request.args.get("hub.challenge")
    if frappe.request.args.get("hub.verify_token") == verify_token:
        return Response(hub_challenge, status=200)
    else:
        return "Invalid verify token"

# Function to handle incoming webhook data
def process_webhook():
    data = json.loads(frappe.request.data)
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "comments":
                handle_comment(change.get("value"))

# Function to handle incoming comment data
def handle_comment(comment_data):
    # Extract necessary data from comment_data
    comment_id = comment_data.get("comment_id")
    comment_message = comment_data.get("message")
    sender_id = comment_data.get("sender_id")

    # Create lead in ERPNext
    create_lead_in_erpnext(comment_message, sender_id)

# Function to create lead in ERPNext
def create_lead_in_erpnext(comment_message, sender_id):
    # Perform necessary actions to create a lead in ERPNext using the data provided
    frappe.get_doc({
        "doctype": "Lead",
        "first_name": sender_id,
        'status': 'Open',
        "description": comment_message,
        "company_name": "Facebook Lead",
        # Add more fields as needed
    }).insert(ignore_permissions=True)

# Main function to handle incoming requests
@frappe.whitelist(allow_guest=True)
def webhook():
    if frappe.request.method == "GET":
        return verify_webhook()
    elif frappe.request.method == "POST":
        process_webhook()
        return "Webhook processed successfully"
    else:
        return "Method not allowed", 405
