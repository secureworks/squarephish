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

# fmt: off

import logging
from rephresh import __version__

SEARCH_KEYWORDS = [
    "password",
    "username",
]

DATA_MODULES = [
    "all",
    "users",
    "groups",
    "emails",
    "onedrive",
    "sharepoint",
    "organization",
]

TARGET_CLIENT_IDS = {
    "Intune":                "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
    "OneDrive":              "b26aadf8-566f-4478-926f-589f601d9c74",
    "SharePoint":            "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0",
    "Microsoft Office":      "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "Office 365 Management": "00b41c95-dab0-4487-9791-b9d2c32c80f2",
}

HTTP_OPSEC_HEADERS   = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",  # Chrome 99
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "upgrade-insecure-requests":  "1",
}

BANNER = f"""
    ____       ____  __                   __  
   / __ \___  / __ \/ /_  ________  _____/ /_ 
  / /_/ / _ \/ /_/ / __ \/ ___/ _ \/ ___/ __ \\
 / _, _/  __/ ____/ / / / /  /  __(__  ) / / /
/_/ |_|\___/_/   /_/ /_/_/   \___/____/_/ /_/ 

                o O             v{__version__}
                 o   _/_
                  . /o  \//
                    =___/\\\\
                     ''
"""

class bcolors:
    """Color codes for colorized terminal output"""

    HEADER    = "\033[95m"
    OKBLUE    = "\033[94m"
    OKCYAN    = "\033[96m"
    OKGREEN   = "\033[92m"
    WARNING   = "\033[93m"
    FAIL      = "\033[91m"
    ENDC      = "\033[0m"
    BOLD      = "\033[1m"
    UNDERLINE = "\033[4m"


class LoggingLevels:
    CRITICAL = f"{bcolors.FAIL}%s{bcolors.ENDC}" % "crit"
    WARNING  = f"{bcolors.WARNING}%s{bcolors.ENDC}" % "warn"
    DEBUG    = f"{bcolors.OKBLUE}%s{bcolors.ENDC}" % "debug"
    ERROR    = f"{bcolors.FAIL}%s{bcolors.ENDC}" % "fail"
    INFO     = f"{bcolors.OKGREEN}%s{bcolors.ENDC}" % "info"


def init_logger(debug: bool):
    """Initialize program logging

    :param debug: debug enabled/disabled
    """
    if debug:
        logging_level = logging.DEBUG
        logging_format = ("[%(asctime)s] [%(levelname)-5s] %(filename)17s:%(lineno)-4s - %(message)s")
    else:
        logging_level = logging.INFO
        logging_format = "[%(asctime)s] [%(levelname)-5s] %(message)s"

    logging.basicConfig(format=logging_format, level=logging_level)

    # Handle color output
    logging.addLevelName(logging.CRITICAL, LoggingLevels.CRITICAL)
    logging.addLevelName(logging.WARNING, LoggingLevels.WARNING)
    logging.addLevelName(logging.DEBUG, LoggingLevels.DEBUG)
    logging.addLevelName(logging.ERROR, LoggingLevels.ERROR)
    logging.addLevelName(logging.INFO, LoggingLevels.INFO)
