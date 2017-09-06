#!/usr/bin/env python

from __future__ import print_function
import sys
import os

script_path = os.path.realpath(sys.argv[0])
dir_path = os.path.dirname(script_path)

print(
    "Sorry, this file has not been implemented.\n"
    "\n"
    "Please manually add the following line\n"
    "    source \"%s/env.bashrc\"\n"
    "at the top of /etc/bash.bashrc (for Ubuntu) or /etc/bashrc (for CentOS)\n" % dir_path,
    file=sys.stderr)

exit(1)
