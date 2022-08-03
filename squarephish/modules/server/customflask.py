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

from flask import Flask  # type: ignore
from typing import Any
from squarephish.utils import HTTP_OPSEC_HEADERS


class CustomFlask(Flask):
    """Custom Flask class to customize response headers in HTTP for better OPSEC."""

    def process_response(self, response: Any) -> Any:
        # Set the defined headers
        for header, value in HTTP_OPSEC_HEADERS.items():
            response.headers[header] = value
        super(CustomFlask, self).process_response(response)
        return response
