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

import smtplib
import logging
from configparser import ConfigParser
from email.message import EmailMessage


class Emailer:
    """Class to send emails"""

    def __init__(self, config: ConfigParser):
        """Initialize emailer

        :param config: configuration settings
        """
        self.smtp_server = config.get("DEFAULT", "SMTP_SERVER")
        self.smtp_port = config.get("DEFAULT", "SMTP_PORT")
        self.smtp_email = config.get("DEFAULT", "SMTP_EMAIL")
        self.smtp_password = config.get("DEFAULT", "SMTP_PASSWORD")

    def send_email(self, message: EmailMessage) -> bool:
        """Send a given email message

        :param message: email message object to send
        :returns:       bool if email sent successfully
        """
        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                smtp.login(self.smtp_email, self.smtp_password)
                smtp.send_message(message)

            return True

        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            return False
