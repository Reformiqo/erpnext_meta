# Copyright (c) 2024, khan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests

class CommentReply(Document):
	def validate(self):
		comment = frappe.get_doc("Meta Comments", self.comment_id)
		if comment.comment_source == "Facebook":
			self.reply_to_facebook_comment()
		else:
			self.reply_to_instagram_comment()
	
	def reply_to_facebook_comment(self):
		comment_id = self.comment_id
		message = self.reply_message
		settings = frappe.get_doc("Facebook Page Settings", "Facebook Page Settings")
		access_token = settings.get_password("access_token")
		comment_url = f"https://graph.facebook.com/v19.0/{comment_id}/comments?access_token={access_token}"
		response = requests.request("POST", comment_url, data={"message": message})
		if response.status_code == 200:
			frappe.msgprint("Comment replied successfully")
		else:
			frappe.msgprint("Failed to reply to comment")
	def reply_to_instagram_comment(self):
		comment_id = self.comment_id
		message = self.reply_message
		settings = frappe.get_doc("Facebook Page Settings", "Facebook Page Settings")
		access_token = settings.get_password("access_token")
		comment_url = f"https://graph.facebook.com/v19.0/{comment_id}/replies?access_token={access_token}"
		response = requests.request("POST", comment_url, data={"message": message})
		if response.status_code == 200:
			frappe.msgprint("Comment replied successfully")
		else:
			frappe.msgprint("Error replying to comment")