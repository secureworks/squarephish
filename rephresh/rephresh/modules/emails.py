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

import logging
from typing import Dict
from typing import List
from rephresh import utils
from rephresh.modules.module import ModuleBase
from rephresh.modules.module import ModuleState


class Emails(ModuleBase):
    """Email retrieval class"""

    def _search_emails(
        self,
        token: Dict[str, str],
        keywords: List[str] = utils.SEARCH_KEYWORDS,
    ) -> Dict[str, str]:
        """Using the provided token, retrieve all emails for the given user

        :param token: client specific refresh token
        :param keywords: keywords for searching
        """
        keywords = " OR ".join(keywords)  # KQL logical or
        return self.msgraph_search(
            self,
            entity=["message"],
            search=keywords,
            token=token,
        )

    def _fetch_emails(self, token: Dict[str, str]) -> Dict[str, str]:
        """Using the provided token, retrieve all emails for the given user

        :param token: client specific refresh token
        """
        return self.msgraph_fetch(
            self,
            url_path="me/messages",
            token=token,
        )

    @classmethod
    def fetch(
        cls,
        module_state: ModuleState,
        scopes: List[str],
    ):
        """Acquire new refresh token and fetch all emails

        :param module_state: Module State instance
        :param scopes: list of scopes to request with refresh token
        """
        if not module_state.msoffice_refresh_token:
            logging.info("Acquiring refresh token for 'Microsoft Office'")
            new_refresh_token = cls.fetch_refresh_token(
                cls,
                module_state=module_state,
                client_name="Microsoft Office",
                scopes=scopes,
            )

            # Update module base
            module_state.msoffice_refresh_token = new_refresh_token

        if module_state.msoffice_refresh_token:
            logging.info("Fetching emails")

            # Fetch emails
            emails = cls._fetch_emails(cls, token=module_state.msoffice_refresh_token)
            total_emails = len(emails["value"])
            logging.info(f"  Emails: {total_emails}")

            # If emails found, write to output file
            if total_emails > 0:
                filename = f"{module_state.token_email}.emails.json"
                logging.info(f"  Output: {filename}")

                cls.write_json(
                    cls,
                    filename=filename,
                    output_dir=module_state.output_dir,
                    data=emails,
                )

            logging.info(f"Searching emails: {module_state.search_keywords}")

            # Search emails for keywords
            results = cls._search_emails(
                cls,
                token=module_state.msoffice_refresh_token,
                keywords=module_state.search_keywords,
            )

            # The response JSON scheme is broke into nested lists, so we need to traverse
            # all lists to find the 'total' results found
            total_results = sum(
                h["total"] for v in results["value"] for h in v["hitsContainers"]
            )
            logging.info(f"  Results: {total_results}")

            # If search results found, write to output file
            if total_results > 0:
                filename = f"{module_state.token_email}.searchemails.json"
                logging.info(f"  Output: {filename}")

                cls.write_json(
                    cls,
                    filename=filename,
                    output_dir=module_state.output_dir,
                    data=results,
                )
