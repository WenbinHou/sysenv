#!/usr/bin/env python

"""

This file should NOT be directly used by users.
Please use functions in `sysenv/env.bashrc` instead.
Currently these functions are:
    * env-reload
    * env-mpi-select
    * env-edit


Usage:
    python sysenv/core.py <action> <env_conf_path> <out_path>

    <action> could be:
        * "reload"
        * "mpi-select"

    <env_conf_path>:
        This is where the environment configuration file is placed, usually `$HOME/env.conf`.

    <out_path>:
        This is where the output bashrc file will be placed.
        The output file should immediately be sourced (by functions in `env.bashrc`).

"""

from __future__ import print_function
from collections import defaultdict
import sys
import json
import os
import copy
import codecs
import string
import re

#
# Global variables
#
g_EnvCoufPath = ""
g_OutPath = ""
g_OutMetaPath = ""
g_Home = ""


def env_reload():

    """
    Load or reload environment variables defined in g_EnvCoufPath.
    The output file (g_OutPath) is saved in environment variable SYSENV_CURRENT_OUTPUT.
    This variable will be defined (for the first time - loading) or changed (for the following time - reloading).
    The output file MUST be placed in a tmpfs (eg. /dev/shm) as it will NOT be deleted automatically.

    The following features are provided:
      - Use '~' at start as short for '$HOME'
      - Use $XXX as reference to other environment variables, which will be expanded
    """

    def read_conf_file():
        result = defaultdict(list)
        current_list = None
        patten = re.compile(r'\[(?: \t)*([A-Za-z_][A-Za-z0-9_]*|\.install_root)(?: \t)*\]')
        conf = codecs.open(g_EnvCoufPath, 'r', 'utf-8')
        for line in conf:
            line = line.strip("\r\n\t ")

            # Skip empty lines & comments
            if len(line) == 0 or line.startswith('#'):
                continue

            if line[0] == '[':  # Now starting a new section
                match = patten.match(line)
                if match:
                    current_list = result[match.group(1)]
                else:
                    raise ValueError("The environment name '%s' is invalid" % line)
            else:
                # Check that only legal characters are in this line
                if ':' in line or '\\' in line:
                    raise ValueError("The following line contains invalid character(s): %s" % line)

                # Expand head '~' to $HOME
                if line[0] == '~':
                    if g_Home is None:
                        raise ValueError("'~' is used, but $HOME is not set")
                    line = "$HOME" + line[1:]

                current_list.append(line)
        conf.close()

        return result

    def expand_env_var(ddict_raw, dict_result):

        pattern = re.compile(r'\$[A-Za-z_][A-Za-z0-9_]*|\$\{[A-Za-z_][A-Za-z0-9_]*\}')

        # env[name] is a list := [ <env.conf expanded> ] + [ <system defined> ]
        env = {}
        status_done = {}

        def env_flatten(line, varlist, known_maps):
            for var in varlist:
                assert (var in known_maps)
                assert (len(known_maps[var]) >= 1)

            result = []
            template = string.Template(line)

            dicts = [[], []]
            which = 0
            for var in varlist:
                other = 1 - which
                dicts[which] = []
                if len(dicts[other]) == 0:
                    for s in known_maps[var]:
                        dicts[which].append({var: s})
                else:
                    for d in dicts[other]:
                        for s in known_maps[var]:
                            newd = copy.deepcopy(d)
                            assert (var not in newd)
                            newd[var] = s
                            dicts[which].append(newd)
                which = other

            if len(dicts[1 - which]) == 0:
                result.append(template.substitute({}))
            else:
                for var_dict in dicts[1 - which]:
                    # print(var_dict)
                    result.append(template.substitute(var_dict))

            # print(result)
            return result

        def inner_expand(name):
            if name in status_done:
                if status_done[name]:
                    return
                else:
                    raise RuntimeError("Recursive environment variable dependency in '%s'" % name)
            status_done[name] = False
            env[name] = []

            if name in ddict_raw:
                dict_result[name] = []
                for line in ddict_raw[name]:
                    # print(line)
                    matches = pattern.findall(line)
                    matches = map(lambda s: s[2:-1] if s[1] == '{' else s[1:], matches)
                    matches = list(set(matches)) # Unique
                    for match_name in matches:
                        inner_expand(match_name)
                    expanded = env_flatten(line, matches, env)
                    dict_result[name] += expanded
                    env[name] += expanded
                    # print()

            # Append existing system environments
            if name in curr_env:
                env[name] += filter(lambda s: len(s) > 0, curr_env[name].split(':'))

            # If the environment doesn't exist at last, specify an empty string.
            # Just as if the system had defined it an empty string.
            if len(env[name]) == 0:
                env[name].append("")

            status_done[name] = True

        #
        # Special patch: for ".install_root" section
        #
        DUMMY_NAME = "_SYSENV_INSTALL_ROOT_hAc5pPe9ECE7v9hDcMqrlB349"
        if ".install_root" in ddict_raw and len(ddict_raw[".install_root"]) > 0:
            ddict_raw[DUMMY_NAME] = ddict_raw[".install_root"]
            ddict_raw["C_INCLUDE_PATH"].append("$%s/include" % DUMMY_NAME)
            ddict_raw["CPLUS_INCLUDE_PATH"].append("$%s/include" % DUMMY_NAME)
            ddict_raw["LIBRARY_PATH"].append("$%s/lib" % DUMMY_NAME)
            ddict_raw["LD_LIBRARY_PATH"].append("$%s/lib" % DUMMY_NAME)
            ddict_raw["PKG_CONFIG_PATH"].append("$%s/lib/pkgconfig" % DUMMY_NAME)
            ddict_raw["PATH"].append("$%s/bin" % DUMMY_NAME)
            ddict_raw["MANPATH"].append("$%s/share/man" % DUMMY_NAME)

        for key in ddict_raw:
            inner_expand(key)

        if ".install_root" in ddict_raw and len(ddict_raw[".install_root"]) > 0:
            del ddict_raw[DUMMY_NAME]
            del dict_result[DUMMY_NAME]


    #
    # Remove original loaded environment variables
    #
    unset_env = []
    curr_env = copy.deepcopy(os.environ)
    if os.path.isfile(g_OutMetaPath):
        with codecs.open(g_OutMetaPath, 'r', 'utf-8') as metafile:
            org_dict = json.load(metafile)
        # print(org_dict)
        for env_name in org_dict:
            if env_name not in curr_env:
                continue
            for env_value in org_dict[env_name]:
                if curr_env[env_name] == env_value:
                    curr_env[env_name] = ""
                elif curr_env[env_name].startswith(env_value + ":"):
                    curr_env[env_name] = curr_env[env_name][len(env_value) + 1:]
                elif curr_env[env_name].endswith(":" + env_value):
                    curr_env[env_name] = curr_env[env_name][:-(len(env_value) + 1)]
                else:
                    curr_env[env_name] = curr_env[env_name].replace(":" + env_value + ":", ":")
            if len(curr_env[env_name]) == 0:
                unset_env.append(env_name)
                del curr_env[env_name]

    #
    # Main codes
    #
    env_ddict_raw = read_conf_file()

    #
    # Expand environ variables ($XXX) in conf file
    #
    env_dict = {}
    expand_env_var(env_ddict_raw, env_dict)

    # Print the result to meta
    with codecs.open(g_OutMetaPath, 'w', 'utf-8') as metafile:
        json.dump(env_dict, metafile)

    # Print the result
    with codecs.open(g_OutPath, 'w', 'utf-8') as outfile:
        for env_name in env_dict:
            if env_name.startswith('.'):
                continue
            if env_name in unset_env:
                unset_env.remove(env_name)

            if env_name in curr_env:
                outline = string.join(env_dict[env_name] + [curr_env[env_name]], ':')
            else:
                outline = string.join(env_dict[env_name], ':')
            outline = outline.replace('"', '\\"')
            outfile.write('export %s="%s"\n' % (env_name, outline))

        for env_name in unset_env:
            outfile.write('unset "%s"\n' % env_name)


def env_mpi_select():
    pass


if __name__ == "__main__":
    # Number of arguments should be 4
    # [ "core.py" "<action>" "<env_conf_path>" "<out_path>" ]
    if len(sys.argv) != 4:
        raise SyntaxError("[FATAL] There should be exactly 3 parameters")

    g_EnvCoufPath = sys.argv[2]
    g_OutPath = sys.argv[3]
    g_OutMetaPath = g_OutPath + ".meta"
    g_Home = os.environ["HOME"] or None

    if sys.argv[1] == 'reload':
        env_reload()
    elif sys.argv[1] == 'mpi-select':
        env_mpi_select()
    else:
        raise SyntaxError("[FATAL] Action '%s' is not defined" % sys.argv[1])
