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

# Python Flask Configuration

import os
import multiprocessing

# Statement for enabling the development environment
DEBUG = False

# Use 2x the number of processor cores for application
# threads to handle incoming requests. One thread to handle
# requests and one to perform background operations
THREADS_PER_PAGE = multiprocessing.cpu_count() * 2

# Enable protection against Cross-site Request Forgery (CSRF)
CSRF_ENABLED = True

# Use a unique key for signing the data
CSRF_SESSION_KEY = os.urandom(32)

# Secret key for signing cookies
SECRET_KEY = os.urandom(32)
