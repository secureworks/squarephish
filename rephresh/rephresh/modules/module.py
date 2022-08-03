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
import logging
import requests
from typing import List
from typing import Dict
from pathlib import Path
from rephresh import utils
from rephresh import acquire


class ModuleState:
    """Module state class to store global data"""

    def __init__(
        self,
        output_dir: str,
        domain: str,
        tenant_id: str,
        token_email: str,
        refresh_token: str,
        search_keywords: List[str],
    ):
        """Module state initialization

        :param output_dir: data output location
        :param domain: target domain name
        :param tenant_id: target tenant ID
        :param token_email: email address of primary refresh token
        :param refresh_token: refresh token string
        """
        self.output_dir = output_dir
        self.domain = domain
        self.tenant_id = tenant_id
        self.token_email = token_email
        self.refresh_token = refresh_token
        self.search_keywords = search_keywords or utils.SEARCH_KEYWORDS

        # FOCI Refresh Tokens
        self.msoffice_refresh_token = None
        self.sharepoint_refresh_token = None


class ModuleBase:
    """Module base class for shared functions"""

    def write_json(self, filename: str, output_dir: str, data: Dict[str, str]):
        """Write a data structure as JSON to a file on the system

        :param filename: name of output file
        :param output_dir: output directory name
        :param data: data structure to write to system
        """
        full_path = Path(output_dir, filename)
        try:
            with open(full_path, "w") as f:
                json.dump(data, f)

        except Exception as e:
            logging.error(f"Error: {e}")
            print(json.dumps(data, indent=4))

    def fetch_refresh_token(
        self,
        module_state: ModuleState,
        client_name: str,
        scopes: List[str],
    ) -> Dict[str, str]:
        """Retrieve a new refresh token for the specified client

        :param module_state: ModuleState instance
        :param client_name: name of target client to fetch refresh token for
        :param scopes: list of scopes to request with refresh token
        """
        client_id = utils.TARGET_CLIENT_IDS[client_name]

        new_refresh_token = acquire.acquire_token_by_refresh_token(
            refresh_token=module_state.refresh_token,
            client_id=client_id,
            scopes=scopes,
            tenant_id=module_state.tenant_id,
        )

        if "error" in new_refresh_token.keys():
            logging.error(f'Invalid response for refresh token: {new_refresh_token["error_description"]}')  # fmt: skip
            return None

        return new_refresh_token

    def msgraph_fetch(
        self,
        url_path: str,
        token=Dict[str, str],
        limit: int = 10,
    ) -> Dict[str, str]:
        """Fetch data from Microsoft Graph

        :param url_path: API path
        :param token: client specific refresh token
        :param limit: max number of page fetches
        """
        headers = utils.HTTP_OPSEC_HEADERS
        headers["Authorization"] = f'Bearer {token["access_token"]}'  # type: ignore

        # Define our initial URL
        url = f"https://graph.microsoft.com/v1.0/{url_path}"

        # Rebuild the search response JSON scheme
        # Exclude @odata.nextLink - only use this to get the next page
        results = {"@odata.context": None, "value": []}

        count = 0
        try:
            # Continue to loop while there is more data/until we hit our request limit
            while url and count <= limit:
                count += 1
                response = requests.get(
                    url=url,
                    headers=headers,
                    verify=False,
                )

                # Get JSON response
                json_response = response.json()

                # Check for errors
                if "error" in json_response:
                    logging.error(f'Error: {json_response["error"]["message"]}')
                    break

                # Get the context (only on first request)
                if not results["@odata.context"]:
                    results["@odata.context"] = json_response.get("@odata.context", None)  # fmt: skip

                # Get the values returned and append to results
                value = json_response.get("value", None)
                if value:
                    results["value"] += value

                # Get the next URL if more results
                url = json_response.get("@odata.nextLink", None)
                if url:
                    logging.debug(f"Requesting next page...")

            return results

        except requests.RequestException as e:
            logging.error(f"Error: {e}")
            return results

    def msgraph_search(
        self,
        entity: List[str],
        search: str,
        token=Dict[str, str],
    ) -> Dict[str, str]:
        """Search data via Microsoft Graph Search

        :param entity: entity to search
        :param search: search term
        :param token: client specific refresh token
        """
        headers = utils.HTTP_OPSEC_HEADERS
        headers["Authorization"] = f'Bearer {token["access_token"]}'  # type: ignore
        headers["content-type"] = "application/json"

        json = {
            "requests": [
                {
                    "entityTypes": entity,
                    "query": {
                        "queryString": search,
                    },
                }
            ]
        }

        try:
            response = requests.post(
                url=f"https://graph.microsoft.com/v1.0/search/query",
                json=json,
                headers=headers,
                verify=False,
            )

            json_response = response.json()
            if "error" in json_response:
                logging.error(f'Error: {json_response["error"]["message"]}')
                return None

            return json_response

        except requests.RequestException as e:
            logging.error(f"Error: {e}")
            return None
