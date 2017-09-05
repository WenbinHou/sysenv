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
        The output file should immediately be sourced and deleted (by functions in `env.bashrc`).

"""

from __future__ import print_function

g_EnvCoufPath = ""
g_OutPath = ""


def env_reload():
    pass


if __name__ == "__main__":
    pass
