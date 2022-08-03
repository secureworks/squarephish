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

from configparser import RawConfigParser


class CustomConfigParser(RawConfigParser):
    """Custom config parser"""

    def get(self, section: str, option: str) -> str:
        """Overrride the 'get' function to strip any single/double quotes from values
        extracted from the configuration file"""
        val = RawConfigParser.get(self, section, option)
        return val.strip('"').strip("'")
