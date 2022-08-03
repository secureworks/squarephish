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

import msal  # type: ignore
import logging
import requests
from typing import List
from typing import Dict
from rephresh import utils


def acquire_token_by_refresh_token(
    *,
    refresh_token: str,
    client_id: str,
    scopes: List[str],
    tenant_id: str,
) -> Dict[str, str]:
    """Convenience function to instantiate a public client
    and attempt to acquire new tokens using a provided refresh token.

    :param refresh_token: initial refresh token for authentication
    :param client_id: target client ID to request refresh token for
    :param scopes: list of scopes to request with refresh token
    :param tenant_id: target tenant ID to request access to

    Via: https://github.com/secureworks/family-of-client-ids-research/blob/main/utils.py#L9
    """
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )
    return app.acquire_token_by_refresh_token(refresh_token, scopes=scopes)


def acquire_tenant_id(domain: str) -> str:
    """Retrieve the domain's tenant ID via Microsft's OpenID Configuration

    :param domain: domain name to retrieve tenant ID for
    """
    url = f"https://login.windows.net/{domain}/.well-known/openid-configuration"
    try:
        response = requests.get(url, headers=utils.HTTP_OPSEC_HEADERS, verify=False)
        json_response = response.json()
        tenant_id = json_response["token_endpoint"].split("/")[3]
        return tenant_id

    except requests.RequestException as e:
        logging.error(f"Error: {e}")
        return None
