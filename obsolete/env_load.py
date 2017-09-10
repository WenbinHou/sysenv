
from __future__ import print_function

import codecs
import re
import os
from collections import defaultdict


def read_conf_file(confpath):
    # type: (str) -> defaultdict[str, list[str]]
    result = defaultdict(list)  # type: defaultdict[str, list[str]]
    current_lists = []  # type: list[list[str]]
    patten = re.compile(r'\s*(\.?[A-Za-z_][A-Za-z0-9_]*)\s*')
    with codecs.open(confpath, "r", "utf-8") as conffile:
        for line in conffile:
            line = line.strip("\r\n\t ")

            # Skip empty lines & comments
            if len(line) == 0 or line.startswith('#'):
                continue

            if line[0] == '[' and line[-1] == ']':  # Now starting a new section
                current_lists = list(map(lambda name: result[name], patten.findall(line[1:-1])))
                if not current_lists:
                    raise ValueError("The environment name '%s' is invalid" % line)
            else:
                # Check that only legal characters are in this line
                # if '\\' in line:
                #    raise ValueError("The following line contains invalid character(s): %s" % line)

                # Replace head '~' with $HOME
                if line[0] == '~':
                    if "HOME" not in os.environ:
                        raise ValueError("'~' is used, but $HOME is not set")
                    line = "$HOME" + line[1:]

                for current_list in current_lists:
                    current_list.append(line)

    return result


def entrypoint(argv):
    # type: (list[str]) -> None
    confpath = argv[0]
    outpath = argv[1]
    conf = read_conf_file(confpath)  # type: dict[str, list[str]]
    with codecs.open(outpath, "w", "utf-8") as outfile
        for name in conf:
            if
            if name in os.environ:
                outfile.write()

    pass
