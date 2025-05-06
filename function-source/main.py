import base64
import json
import os

import google.auth
from google.cloud import billing

PROJECT_ID = google.auth.default()[1]
cloud_billing_client = billing.CloudBillingClient()


def list_projects(billing_account_name: str):
    """Lists projects linked to a given billing account name"""
    projects = cloud_billing_client.list_project_billing_info(name=billing_account_name)
    return [project.project_id for project in projects]


def stop_billing(request):
    """HTTP-triggered Cloud Function entry point handling Pub/Sub push payload"""
    try:
        envelope = request.get_json()
        if not envelope or "message" not in envelope:
            print("Invalid Pub/Sub message format")
            return "Bad Request: Invalid Pub/Sub message", 400

        pubsub_message = envelope.get("message", {})
        encoded_data = pubsub_message.get("data")
        print(f"This is Pub/Sub message: {pubsub_message}")

        if not encoded_data:
            print(f"Missing 'data' in Pub/Sub message: {pubsub_message}")
            return "Bad Request: Missing data", 400

        try:
            pubsub_data = base64.b64decode(encoded_data).decode("utf-8")
        except Exception as decode_err:
            print(f"Failed to decode message data: {decode_err}")
            return "Bad Request: Cannot decode data", 400
        print(f"Decoded Pub/Sub data: {pubsub_data}")

        pubsub_json = json.loads(pubsub_data)
        cost_amount = pubsub_json["costAmount"]
        budget_amount = pubsub_json["budgetAmount"]

        if cost_amount <= budget_amount:
            print(f"No action necessary. (Current cost: {cost_amount})")
            return "No action needed", 200

        budget_id = os.environ.get("MY_BUDGET_ALERT_ID")
        billing_account_id = budget_id.split("/")[1]
        billing_account_name = f"billingAccounts/{billing_account_id}"
        projects = list_projects(billing_account_name)

        for project in projects:
            project_name = cloud_billing_client.common_project_path(project)
            unlink_billing(project_name)

        return "Billing stopped", 200

    except Exception as e:
        print(f"Error: {e}")
        return f"Internal Server Error: {e}", 200


def unlink_billing(project_name: str):
    request = billing.UpdateProjectBillingInfoRequest(
        name=project_name,
        project_billing_info=billing.ProjectBillingInfo(
            billing_account_name=""  # Disable billing
        ),
    )
    project_billing_info = cloud_billing_client.update_project_billing_info(request)
    print(f"Billing disabled: {project_billing_info}")
