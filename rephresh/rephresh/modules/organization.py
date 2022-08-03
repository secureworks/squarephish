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
from rephresh.modules.module import ModuleBase
from rephresh.modules.module import ModuleState


class Organization(ModuleBase):
    """Organization retrieval class"""

    def _fetch_organization(self, token: Dict[str, str]) -> Dict[str, str]:
        """Using the provided token, retrieve the given users Organization

        :param token: client specific refresh token
        """
        return self.msgraph_fetch(
            self,
            url_path="organization",
            token=token,
        )

    @classmethod
    def fetch(
        cls,
        module_state: ModuleState,
        scopes: List[str],
    ):
        """Acquire new refresh token and fetch users Oraganization

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
            logging.info("Fetching organizations")

            # Fetch all orgs
            orgs = cls._fetch_organization(cls, token=module_state.msoffice_refresh_token)  # fmt: skip
            total_orgs = len(orgs["value"])
            logging.info(f"  Organizations: {total_orgs}")

            # If orgs found, write to output file
            if total_orgs > 0:
                filename = f"{module_state.token_email}.organizations.json"
                logging.info(f"  Output: {filename}")

                cls.write_json(
                    cls,
                    filename=filename,
                    output_dir=module_state.output_dir,
                    data=orgs,
                )
