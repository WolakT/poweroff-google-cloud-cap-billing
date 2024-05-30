""" Module for getting the project ids linked to a billing account"""
import json
import sys
import os
func_dir = os.path.join(os.getcwd(), "function-source")
sys.path.append(func_dir)
from typing import List

from main import list_projects

BILLING_ACCOUNT_ID = "01A7A9-41C342-AAC8BD"

def escape_quotes_string_list(string_list: List[str]) -> str:
    """escapes each doubleqoute of the string inside the list"""
    json_str = json.dumps(string_list)
    escaped_json_string = json_str.replace('"', '\"')
    return escaped_json_string

billing_account_name = f"billingAccounts/{BILLING_ACCOUNT_ID}"
project_ids = list_projects(billing_account_name)
escaped_project_ids = escape_quotes_string_list(project_ids)
json_string = json.dumps({"project_ids": escaped_project_ids})
print(json_string)
#print("""{\n"project_ids": "[\\"limitless-learn\\",
#\\"trade-tide-engine\\", \\"writing-practice-app\\"]"\n}""")
