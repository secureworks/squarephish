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
from squarephish import __version__


# Configuration values
CONFIG_DEFAULT = ["SMTP_PORT", "SMTP_SERVER", "SMTP_PROTO", "SMTP_EMAIL", "SMTP_PASSWORD"]
CONFIG_EMAIL   = ["SQUAREPHISH_SERVER", "SQUAREPHISH_PORT", "SQUAREPHISH_ENDPOINT", "FROM_EMAIL", "SUBJECT", "EMAIL_TEMPLATE"]
CONFIG_SERVER  = ["PORT", "FROM_EMAIL", "SUBJECT", "CLIENT_ID", "ENDPOINT", "EMAIL_TEMPLATE", "PERMISSION_SCOPE"]

# Default HTTP values
HTTP_HEADERS         = { "Content-Type": "application/x-www-form-urlencoded" }
HTTP_OPSEC_HEADERS   = {
    "vary": "Accept-Encoding",
    "server": "Microsoft-IIS/10.0",
    "tls_version": "tls1.3",
    "content-type": "text/html; charset=utf-8",
    "x-appversion": "1.0.8125.42964",
    "x-frame-options": "SAMEORIGIN",
    "x-ua-compatible": "IE=Edge;chrome=1",
    "x-xss-protection": "1; mode=block",
    "x-content-type-options": "nosniff",
    "strict-transport-security": "max-age=31536000",
}

BANNER = f"""
   _____                            _____  _     _     _     
  / ____|                          |  __ \| |   (_)   | |    
 | (___   __ _ _   _  __ _ _ __ ___| |__) | |__  _ ___| |__  
  \___ \ / _` | | | |/ _` | '__/ _ \  ___/| '_ \| / __| '_ \ 
  ____) | (_| | |_| | (_| | | |  __/ |    | | | | \__ \ | | |
 |_____/ \__, |\__,_|\__,_|_|  \___|_|    |_| |_|_|___/_| |_|
            | |                                              
            |_|                                            
                     _________
                    |         | /(
                    | O       |/ (
                    |>        |\ (  v{__version__}
                    |_________| \(
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
