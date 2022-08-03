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


class OneDrive(ModuleBase):
    """OneDrive drive search/retrieval class"""

    def _search_drives(
        self,
        token: Dict[str, str],
        keywords: List[str] = utils.SEARCH_KEYWORDS,
    ) -> Dict[str, str]:
        """Using the provided token, search OneDrive drives by name accessible
        by the given user

        For the time being, we are using the `search` path for /drive/ instead of the
        /search/query API

        :param token: client specific refresh token
        :param keywords: keywords for searching
        """
        keywords = " OR ".join(keywords)  # KQL logical or
        return self.msgraph_fetch(
            self,
            url_path=f"me/drive/search(q='{keywords}')",
            token=token,
        )

    def _fetch_drives(self, token: Dict[str, str]) -> Dict[str, str]:
        """Using the provided token, list OneDrive drives accessible by the given user

        :param token: client specific refresh token
        """
        return self.msgraph_fetch(
            self,
            url_path="me/drives",
            token=token,
        )

    @classmethod
    def fetch(
        cls,
        module_state: ModuleState,
        scopes: List[str],
    ):
        """Acquire new refresh token and access OneDrive

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
            logging.info("Fetching OneDrive drives")

            # Fetch drives
            drives = cls._fetch_drives(cls, token=module_state.msoffice_refresh_token)
            total_drives = len(drives["value"])
            logging.info(f'  Drives: {total_drives}')

            # If drives found, write to output file
            if total_drives > 0:
                filename = f"{module_state.token_email}.drives.json"
                logging.info(f"  Output: {filename}")

                cls.write_json(
                    cls,
                    filename=filename,
                    output_dir=module_state.output_dir,
                    data=drives,
                )

            # Specifically search file names across drives (different from the /search/query
            # API)
            logging.info(f"Searching OneDrive files (by name): {module_state.search_keywords}")  # fmt: skip

            # Search drive files for keywords
            results = cls._search_drives(
                cls,
                token=module_state.msoffice_refresh_token,
                keywords=module_state.search_keywords,
            )
            total_results = len(results["value"])
            logging.info(f'  Files: {total_results}')

            # If search results found, write to output file
            if total_results > 0:
                filename = f"{module_state.token_email}.searchdrives.json"
                logging.info(f"  Output: {filename}")

                cls.write_json(
                    cls,
                    filename=filename,
                    output_dir=module_state.output_dir,
                    data=results,
                )
