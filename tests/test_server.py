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

import unittest
from squarephish.utils import HTTP_OPSEC_HEADERS
from squarephish.cfgparser import CustomConfigParser
from squarephish.modules.server import app
from squarephish.modules.server import init_app


class ServerTestCase(unittest.TestCase):
    """SquarePhish Server Test Cases

    These test cases are specifically designed to validate the OPSEC handling
    of the Flask server. No matter what, valid or valid request, the server
    should only include the custom response headers defined in utils.py and
    redirect away from our Flask instance to a Microsoft owned endpoint.
    """

    @classmethod
    def setUpClass(cls):
        """Initialize Flask app"""
        # Parse the default config settings
        config = CustomConfigParser(comment_prefixes="#", inline_comment_prefixes="#")
        config.read("../settings.config")

        # Initialize app
        init_app(config=config, emailer=None)

    def setUp(self):
        self.app = app.app_context()
        self.app.push()
        self.client = app.test_client()

    def tearDown(self):
        self.app.pop()

    def test_server_headers_1(self):
        """Server Headers 1: Valid request"""
        endpoint = "/mfa?email=test@test.com"  # Default config endpoint
        response = self.client.get(endpoint, follow_redirects=False)
        for header, value in response.headers.items():
            # Skip non-customized headers
            if header.lower() in ["content-length", "location", "date"]:
                continue
            self.assertTrue(header in HTTP_OPSEC_HEADERS.keys())
            self.assertEqual(HTTP_OPSEC_HEADERS[header], value)

    def test_server_headers_2(self):
        """Server Headers 2: Invalid request"""
        endpoint = "/invalid"
        response = self.client.get(endpoint, follow_redirects=False)
        for header, value in response.headers.items():
            # Skip non-customized headers
            if header.lower() in ["content-length", "location", "date"]:
                continue
            self.assertTrue(header in HTTP_OPSEC_HEADERS.keys())
            self.assertEqual(HTTP_OPSEC_HEADERS[header], value)

    def test_endpoint_valid(self):
        """Valid Request"""
        endpoint = "/mfa?email=test@test.com"  # Default config endpoint
        response = self.client.get(endpoint, follow_redirects=False)

        # There is 3 scenarios that can happen if a valid endpoint is provided:
        #   1. The server can not reach microsoft.com
        #   2. The server gets an invalid response from microsoft.com
        #   3. The server succeeds and continues
        # All three scenarios will result in a redirect to the Device Code endpoint
        # of microsoft.com
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location == "https://microsoft.com/devicelogin")

    def test_endpoint_invalid_1(self):
        """Invalid Request 1: Incorrect URL path"""
        endpoint = "/invlaid"
        response = self.client.get(endpoint, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "https://microsoft.com/")

    def test_endpoint_invalid_2(self):
        """Invalid Request 2: Missing GET parameter"""
        endpoint = "/mfa"
        response = self.client.get(endpoint, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "https://microsoft.com/")

    def test_endpoint_invalid_3(self):
        """Invalid Request 3: Incorrect GET parameter"""
        endpoint = "/mfa?username=test@test.com"
        response = self.client.get(endpoint, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "https://microsoft.com/")


if __name__ == "__main__":
    unittest.main()
