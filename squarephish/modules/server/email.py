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

from email.message import EmailMessage
from squarephish.modules.emailer import Emailer


def email_usercode(
    email_template: str,
    subject: str,
    from_email: str,
    to_email: str,
    user_code: str,
    emailer: Emailer,
) -> bool:
    """Send the phishing email to a target user

    :param email_template: email body template
    :param subject:        email subject to send to victim
    :param from_email:     FROM email address to display to victim
    :param to_email:       TO email address of victim
    :param user_code:      OAuth user code
    :param emailer:        emailer object to send emails
    :returns:              bool if the email was successfully sent
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    msg.set_content(email_template % user_code, subtype="html")
    return emailer.send_email(msg)
