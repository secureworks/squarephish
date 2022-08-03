# RePhresh

This is a support tool that is meant to be used with the output from `SquarePhish`.

RePhresh will take in the SquarePhish generated JSON file containing the target bearer token information, parse the token and request new refresh token(s) for given client IDs. Once the refresh tokens are acquired, RePhresh will fetch associated data (e.g. requesting a token for Microsoft Office will retrieve all emails for the given user).

This approach is based on the research: [Family of Client IDs](https://github.com/secureworks/family-of-client-ids-research)

## Usage

```
    ____       ____  __                   __  
   / __ \___  / __ \/ /_  ________  _____/ /_ 
  / /_/ / _ \/ /_/ / __ \/ ___/ _ \/ ___/ __ \
 / _, _/  __/ ____/ / / / /  /  __(__  ) / / /
/_/ |_|\___/_/   /_/ /_/_/   \___/____/_/ /_/ 

                o O             v0.1.0
                 o   _/_
                  . /o  \//
                    =___/\\
                     ''

usage: rephresh.py [-h] -t TOKENFILE [-d DOMAIN] [-m MODULE] [--debug]

RePhresh -- v0.1.0

optional arguments:
  -h, --help            show this help message and exit

  -t TOKENFILE, --tokenfile TOKENFILE
                        SquarePhish generated token file containing JSON bearer token

  -d DOMAIN, --domain DOMAIN
                        target domain to acquire tenant ID (if none provided, domain is
                        extracted from token file name)

  -m MODULE, --module MODULE
                        specify module(s) to run (comma delimited)
                        (all | emails,users,groups,organization,onedrive,sharepoint)
                        [default: all]

  -s SEARCH, --search SEARCH
                        specify keyword(s) to use when searching (comma delimited)
                        [default: password,username]

  --debug               enable debugging
```

## Modules

```
[2022-04-22 01:25:58,337] [info] Output directory: output/minnow@square.phish.20220422052558
[2022-04-22 01:25:58,338] [info] Acquiring refresh token for 'Microsoft Office'
[2022-04-22 01:25:58,733] [info] Fetching emails
[2022-04-22 01:26:01,367] [info]   Emails: 48
[2022-04-22 01:26:01,367] [info]   Output: minnow@square.phish.emails.json
[2022-04-22 01:26:01,374] [info] Searching emails: ['password', 'username']
[2022-04-22 01:26:01,686] [info]   Results: 1
[2022-04-22 01:26:01,686] [info]   Output: minnow@square.phish.searchemails.json
[2022-04-22 01:26:01,687] [info] Fetching users
[2022-04-22 01:26:02,300] [info]   Users: 75
[2022-04-22 01:26:02,300] [info]   Output: minnow@square.phish.users.json
[2022-04-22 01:26:02,302] [info] Fetching groups
[2022-04-22 01:26:02,650] [info]   Groups: 39
[2022-04-22 01:26:02,650] [info]   Output: minnow@square.phish.groups.json
[2022-04-22 01:26:02,653] [info] Fetching organizations
[2022-04-22 01:26:02,980] [info]   Organizations: 1
[2022-04-22 01:26:02,980] [info]   Output: minnow@square.phish.organizations.json
[2022-04-22 01:26:02,982] [info] Fetching OneDrive drives
[2022-04-22 01:26:03,370] [info]   Drives: 1
[2022-04-22 01:26:03,371] [info]   Output: minnow@square.phish.drives.json
[2022-04-22 01:26:03,371] [info] Searching OneDrive files (by name): ['password', 'username']
[2022-04-22 01:26:04,534] [info]   Files: 1
[2022-04-22 01:26:04,534] [info]   Output: minnow@square.phish.searchdrives.json
[2022-04-22 01:26:04,534] [info] Acquiring refresh token for 'SharePoint'
[2022-04-22 01:26:04,899] [info] Searching SharePoint and OneDrive contents: ['password', 'username']
[2022-04-22 01:26:05,375] [info]   Results: 3
[2022-04-22 01:26:05,375] [info]   Output: minnow@square.phish.search.json
```

### Emails

Acquire a refresh token for `Microsoft Office` and perform two actions:
1. Fetch and save all emails associated to the authenticating account.
2. Search all emails for given keywords.

### Users

Acquire a refresh token for `Microsoft Office` and then fetch and save all users accessible to the authenticating account.

### Groups

Acquire a refresh token for `Microsoft Office` and then fetch and save all groups accessible to the authenticating account.

### Organization

Acquire a refresh token for `Microsoft Office` and then fetch and save all organization data accessible to the authenticating account.

### OneDrive

Acquire a refresh token for `Microsoft Office` and perform two actions:
1. Fetch and save all OneDrive drives accessible to the authenticating account.
2. Search all accessible drives for given keywords.

### SharePoint

Acquire a refresh token for `SharePoint` and then use the Microsoft Search API to search content in OneDrive and SharePoint.