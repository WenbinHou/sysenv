#!/usr/bin/env python

from __future__ import print_function

import codecs
import copy
import os
import json
import re
import sys


def write_to_file(filepath, obj):
    with codecs.open(filepath, "w", "utf-8") as f:
        json.dump(obj, f, indent=4, sort_keys=True)


def read_from_file(filepath):
    with codecs.open(filepath, "r", "utf-8") as f:
        return json.load(f)


def guess_env_colon_separate(var_name):
    # type: (str) -> bool
    if not hasattr(guess_env_colon_separate, "pattern"):
        guess_env_colon_separate.pattern = re.compile(
            """(?:.+)(?: 
                        _DIR | DIRS | 
                        _DIRECTORY | _DIRECTORIES |
                        PATH |      # CPATH, MANPATH, INFOPATH, MODULEPATH, NLSPATH, XXX_PATH
                        _FILE |     # INTEL_LICENSE_FILE
                        _COLORS |   # LS_COLORS, GCC_COLORS
                        MODULES     # GTK_MODULES, GTK2_MODULES, LOADEDMODULES
                     )$     # The above are valid suffixes
                | ^(?:
                        PATH
                   )$       # The above are full matches
            """, re.VERBOSE | re.IGNORECASE)
    return bool(guess_env_colon_separate.pattern.match(var_name))


def get_current_exports(envs):
    # type: (dict[str, str]) -> dict[str, list[str]]
    result = {}  # type: dict[str, list[str]]
    for name in envs:
        if guess_env_colon_separate(name):  # colon-separated variable
            result[name] = list(filter(lambda s: s, envs[name].split(":"))) or [""]
        else:
            result[name] = [envs[name]]
    return result


def get_exports_difference(
        env_old,  # type: dict[str, list[str]]
        env_new  # type: dict[str, list[str]]
        ):
    # type: (...) -> list[dict[str, list[str]], dict[str, list[list[str], list[str]]], dict[str, list[str]]]
    # returned tuple:
    #   [0]: created[name, values]
    #   [1]: modified[name, [values_added, values_removed]]
    #   [2]: removed[name, values]
    created = {}  # type: dict[str, list[str]]
    modified = {}  # type: dict[str, list[list[str], list[str]]]
    removed = []  # type: dict[str, list[str]]

    # Get "removed" first
    for name in env_old:
        if name not in env_new:
            removed[name] = copy.deepcopy(env_old[name])

    # Get "created" and "modified"
    for name in env_new:
        if name not in env_old:
            created[name] = copy.deepcopy(env_new[name])
            continue
        values_new = set(env_new[name])  # type: set[str]
        values_old = set(env_old[name])  # type: set[str]
        if values_new != values_old:
            modified[name] = [None, None]
            modified[name][0] = list(values_new - values_old)
            modified[name][1] = list(values_old - values_new)

    return [created, modified, removed]


def restore_exports_difference(
        source,  # type: dict[str, list[str]]
        created,  # type: dict[str, list[str]]
        modified,  # type: dict[str, list[list[str], list[str]]]
        removed  # type: dict[str, list[str]]]
        ):
    # type: (...) -> dict[str, list[str]]
    result = copy.deepcopy(source)

    for name in created:
        if name in result:
            result[name] = list(set(result[name]) - set(created[name]))
            if not result[name]:
                result[name] = None  # this means to remove this variable
            else:
                # TODO: print a warning?
                pass

    for name in modified:
        if name in result:
            # Remove added values
            for add in modified[name][0]:
                try:
                    result[name].remove(add)
                except ValueError:
                    pass
            # Add removed values
            for rm in modified[name][1]:
                result[name].insert(0, rm)

    for name in removed:
        if name in result:
            # TODO: print a warning?
            pass
        else:
            result[name] = removed[name]

    return result


def env_restore(diffpath, outpath):
    # type: (str, str) -> None
    env_curr = get_current_exports(dict(os.environ))
    [created, modified, removed] = read_from_file(diffpath)
    restore = restore_exports_difference(env_curr, created, modified, removed)

    with codecs.open(outpath, "w", "utf-8") as outfile:
        for name in restore:
            if (name not in created) and (name not in modified) and (name not in removed):
                continue
            if restore[name] is None:
                outfile.write("unset %s\n" % name)
            else:
                value = ":".join(restore[name]).replace("\\", "\\\\").replace("$", "\\$").replace('"', '\\"')
                outfile.write('export %s="%s"\n' % (name, value))
        outfile.write("\n")


def main():
    if sys.argv[1] == "dump":
        write_to_file(sys.argv[2], dict(os.environ))

    elif sys.argv[1] == "diff":
        env_old = get_current_exports(read_from_file(sys.argv[2]))
        env_new = get_current_exports(read_from_file(sys.argv[3]))
        [created, modified, removed] = get_exports_difference(env_old, env_new)
        write_to_file(sys.argv[4], [created, modified, removed])

    elif sys.argv[1] == "restore":
        env_restore(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == "env-load":
        import env_load
        env_load.entrypoint(sys.argv[1:])


if __name__ == "__main__":
    main()
