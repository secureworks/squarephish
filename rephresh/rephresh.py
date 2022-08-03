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
import json
import urllib3
import logging
import argparse
from pathlib import Path
from datetime import datetime
from datetime import timezone
from rephresh import __title__
from rephresh import __version__
from rephresh import utils
from rephresh import acquire
from rephresh.modules import Emails
from rephresh.modules import Groups
from rephresh.modules import OneDrive
from rephresh.modules import Organization
from rephresh.modules import SharePoint
from rephresh.modules import Users
from rephresh.modules.module import ModuleState


# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


if __name__ == "__main__":
    print(utils.BANNER)

    parser = argparse.ArgumentParser(description=f"{__title__} -- v{__version__}")

    parser.add_argument(
        "-t",
        "--tokenfile",
        type=str,
        help="SquarePhish generated token file containing JSON bearer token",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--domain",
        type=str,
        help=(
            "target domain to acquire tenant ID (if none provided, domain is extracted from "
            "token file name)"
        ),
    )
    parser.add_argument(
        "-m",
        "--module",
        type=str,
        default="all",
        help=(
            "specify module(s) to run (comma delimited) "
            "(all | emails,users,groups,organization,onedrive,sharepoint) "
            "[default: all]"
        ),
    )
    parser.add_argument(
        "-s",
        "--search",
        type=str,
        default=utils.SEARCH_KEYWORDS,
        help=(
            "specify keyword(s) to use when searching (comma delimited) "
            "[default: password,username]"
        ),
    )
    parser.add_argument("--debug", action="store_true", help="enable debugging")

    args = parser.parse_args()

    # Initialize logging level and format
    utils.init_logger(args.debug)

    # Read in the token file as a JSON object and extract the refresh token
    try:
        with open(args.tokenfile, "r") as f:
            token_info = json.loads(f.read())
        refresh_token = token_info["refresh_token"]

    # Catch invalid file exceptions
    except FileNotFoundError:
        logging.error("Invalid token file provided")
        sys.exit(1)

    # Catch JSON parsing exceptions
    except (KeyError, json.decoder.JSONDecodeError, TypeError) as e:
        logging.error(f"Error: {e}")
        sys.exit(1)

    # Parse modules to execute, remove invalid modules
    args.module = args.module.split(",")
    for m in args.module:
        if m not in utils.DATA_MODULES:
            logging.error(f"Skipping invalid module: '{m}'")

    args.module = [x for x in args.module if x in utils.DATA_MODULES]
    if len(args.module) < 1:
        logging.error("No modules provided")
        sys.exit(1)

    logging.debug(f"Modules:    {args.module}")

    # Parse token filename for domain and email
    # Remove path from full file name
    token_filename = args.tokenfile.split("/")[-1]
    logging.debug(f"Token file: {token_filename}")

    # Remove extension, extract email
    token_email = token_filename.replace(".tokeninfo.json", "")
    if not args.domain:
        try:
            args.domain = token_email.split("@")[1]  # Grab domain

        except IndexError:
            logging.error("Could not parse domain from token file name")
            logging.error("Please provide a domain via -d/--domain")
            sys.exit(1)

    logging.debug(f"Token UPN:  {token_email}")
    logging.debug(f"Domain:     {args.domain}")

    # Attempt to acquire the tenant ID from OpenID-Configuration
    tenant_id = acquire.acquire_tenant_id(domain=args.domain)
    if not tenant_id:
        logging.error("[!] Failed to retrieve tenant ID")
        sys.exit(1)

    logging.debug(f"Tenant ID:  {tenant_id}")

    # If needed, rebuild custom search keywords
    if type(args.search) == str:
        args.search = args.search.split(",")

    # Create output dir before moving on
    utc_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    output_dir = Path("output", f"{token_email}.{utc_now}")
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory: {output_dir}")

    # Create an instance of our module base
    module_state = ModuleState(
        output_dir=output_dir,
        domain=args.domain,
        tenant_id=tenant_id,
        token_email=token_email,
        refresh_token=refresh_token,
        search_keywords=args.search,
    )

    # Get emails
    scopes = [".default"]  # Default
    if any(x in args.module for x in ["emails", "all"]):
        Emails.fetch(module_state=module_state, scopes=scopes)

    if any(x in args.module for x in ["users", "all"]):
        Users.fetch(module_state=module_state, scopes=scopes)

    if any(x in args.module for x in ["groups", "all"]):
        Groups.fetch(module_state=module_state, scopes=scopes)

    if any(x in args.module for x in ["organization", "all"]):
        Organization.fetch(module_state=module_state, scopes=scopes)

    if any(x in args.module for x in ["onedrive", "all"]):
        OneDrive.fetch(module_state=module_state, scopes=scopes)

    if any(x in args.module for x in ["sharepoint", "all"]):
        SharePoint.fetch(module_state=module_state, scopes=scopes)
