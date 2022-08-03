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

import urllib3
import unittest
import requests
from squarephish.utils import HTTP_OPSEC_HEADERS

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RemoteServerTestCase(unittest.TestCase):
    """SquarePhish Server Test Cases - Remote

    This is a unittest for testing a running SquarePhish server remotely to
    validate OPSEC prior to execution against a victim.
    """

    SQUAREPHISH_PORT = 8443  # Populate this with the correct value when testing
    SQUAREPHISH_SERVER = ""  # Populate this with the correct value when testing

    def test_server_headers_1(self):
        """Server Headers 1: Valid request"""
        if not self.SQUAREPHISH_SERVER:
            raise ValueError("Invalid SquarePhish server")

        url = f"https://{self.SQUAREPHISH_SERVER}:{self.SQUAREPHISH_PORT}"
        endpoint = "/mfa?email=test@test.com"  # Default config endpoint
        response = requests.get(f"{url}{endpoint}", allow_redirects=False, verify=False)

        for header, value in response.headers.items():
            # Skip non-customized headers
            if header.lower() in ["content-length", "location", "date"]:
                continue
            self.assertTrue(header in HTTP_OPSEC_HEADERS.keys())
            self.assertEqual(HTTP_OPSEC_HEADERS[header], value)

    def test_server_headers_2(self):
        """Server Headers 2: Invalid request"""
        if not self.SQUAREPHISH_SERVER:
            raise ValueError("Invalid SquarePhish server")

        url = f"https://{self.SQUAREPHISH_SERVER}:{self.SQUAREPHISH_PORT}"
        endpoint = "/invalid"
        response = requests.get(f"{url}{endpoint}", allow_redirects=False, verify=False)

        for header, value in response.headers.items():
            # Skip non-customized headers
            if header.lower() in ["content-length", "location", "date"]:
                continue
            self.assertTrue(header in HTTP_OPSEC_HEADERS.keys())
            self.assertEqual(HTTP_OPSEC_HEADERS[header], value)

    def test_endpoint_valid(self):
        """Valid Request"""
        if not self.SQUAREPHISH_SERVER:
            raise ValueError("Invalid SquarePhish server")

        url = f"https://{self.SQUAREPHISH_SERVER}:{self.SQUAREPHISH_PORT}"
        endpoint = "/mfa?email=test@test.com"  # Default config endpoint
        response = requests.get(f"{url}{endpoint}", allow_redirects=False, verify=False)

        # There is 3 scenarios that can happen if a valid endpoint is provided:
        #   1. The server can not reach microsoft.com
        #   2. The server gets an invalid response from microsoft.com
        #   3. The server succeeds and continues
        # All three scenarios will result in a redirect to the Device Code endpoint
        # of microsoft.com
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"] == "https://microsoft.com/devicelogin")  # fmt: skip

    def test_endpoint_invalid_1(self):
        """Invalid Request 1: Incorrect URL path"""
        if not self.SQUAREPHISH_SERVER:
            raise ValueError("Invalid SquarePhish server")

        url = f"https://{self.SQUAREPHISH_SERVER}:{self.SQUAREPHISH_PORT}"
        endpoint = "/invalid"
        response = requests.get(f"{url}{endpoint}", allow_redirects=False, verify=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "https://microsoft.com/")

    def test_endpoint_invalid_2(self):
        """Invalid Request 2: Missing GET parameter"""
        if not self.SQUAREPHISH_SERVER:
            raise ValueError("Invalid SquarePhish server")

        url = f"https://{self.SQUAREPHISH_SERVER}:{self.SQUAREPHISH_PORT}"
        endpoint = "/mfa"
        response = requests.get(f"{url}{endpoint}", allow_redirects=False, verify=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "https://microsoft.com/")

    def test_endpoint_invalid_3(self):
        """Invalid Request 3: Incorrect GET parameter"""
        if not self.SQUAREPHISH_SERVER:
            raise ValueError("Invalid SquarePhish server")

        url = f"https://{self.SQUAREPHISH_SERVER}:{self.SQUAREPHISH_PORT}"
        endpoint = "/mfa?username=test@test.com"
        response = requests.get(f"{url}{endpoint}", allow_redirects=False, verify=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "https://microsoft.com/")


if __name__ == "__main__":
    unittest.main()
