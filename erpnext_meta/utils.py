import frappe
import json
from frappe.utils import get_site_name
import requests
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
    try:
        doc = frappe.get_doc({
            "doctype": "Facebook Notification Log",
            "template": "Webhook",
            "metadata": frappe.local.form_dict
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        # Log the error or handle it appropriately
        frappe.log_error(f"Error processing webhook: {e}")

# Main function to handle incoming requests
@frappe.whitelist(allow_guest=True)
def facebook_webhook():
    if frappe.request.method == "GET":
        return verify_webhook()
    elif frappe.request.method == "POST":
        new_notification = frappe.get_doc({
            "doctype": "Facebook Notification Log",
            "template": "Webhook",
            "metadata": frappe.local.form_dict
        })
        new_notification.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return "Webhook processed successfully"
    else:
        return "Method not allowed", 405

#fetch comments of a page
def fetch_facebook_comments():
    settings = frappe.get_doc("Facebook Page Settings", "Facebook Page Settings")
    access_token = settings.get_password("access_token")
    page_id = settings.page_id
    feed = f"https://graph.facebook.com/v19.0/{page_id}/feed?access_token={access_token}"
    response = requests.request("GET", feed)
    # Process the response and extract comments
    if response.status_code == 200:
        for post in response.json().get("data"):
            post_url = f"https://graph.facebook.com/v19.0/{post.get('id')}/comments?access_token={access_token}"
            comments = requests.request("GET", post_url)
            for comment in comments.json().get("data"):
                message = comment.get("message")
                sender_id = comment.get("from")
                comment_id = comment.get("id")
                print(f'Inserting comment {comment_id}')
                if not frappe.db.exists("Meta Comments", comment_id):
                    new_comment = frappe.get_doc({
                        'doctype': 'Meta Comments',
                        'comment_id': comment_id,
                        'message': message,
                        'comment_source': 'Facebook',
                    })
                    new_comment.insert()
                    frappe.db.commit()

    
@frappe.whitelist(allow_guest=True)
def fetch_instagram_comments():
    settings = frappe.get_doc("Facebook Page Settings", "Facebook Page Settings")
    access_token = settings.get_password("access_token")
    page_id = settings.page_id
    instagram_media = f"https://graph.facebook.com/v19.0/17841464100616335?fields=media&access_token={access_token}"
    response = requests.request("GET", instagram_media)
    for media in response.json().get("media").get("data"):
        media_id = media.get("id")
        comments_url = f"https://graph.facebook.com/v19.0/{media_id}/comments?access_token={access_token}"
        comments = requests.request("GET", comments_url)
        for comment in comments.json().get("data"):
            message = comment.get("text")
            comment_id = comment.get("id")
            print(f'Inserting comment {comment_id}')
            if not frappe.db.exists("Meta Comments", comment_id):
                new_comment = frappe.get_doc({
                    'doctype': 'Meta Comments',
                    'comment_id': comment_id,                    'message': message,
                    'comment_source': 'Instagram',
                })
                new_comment.insert()
                frappe.db.commit()
    if response.status_code == 200:
        return "Comments fetched successfully"
    else:
        return "Error fetching comments"
    
def fetch_comments():
    fetch_facebook_comments()
    fetch_instagram_comments()
