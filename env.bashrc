
if [ $_ == $0 ]; then
    echo "[ERROR] sysenv: $(realpath "$0") must be sourced but not invoked"
    exit 1
fi

if [ -z "$SYSENV_OUTPUT_DIRECTORY" ]; then
export SYSENV_OUTPUT_DIRECTORY="/dev/shm/sysenv/${RANDOM}${RANDOM}${RANDOM}${RANDOM}"

env-reload() {

    if [ ! -r "$HOME/env.conf" ]; then
        echo "[ERROR] sysenv: \$HOME/env.conf is not found"
        return 1
    fi

    if [ ! -d "$SYSENV_OUTPUT_DIRECTORY" ]; then
        mkdir -p "$SYSENV_OUTPUT_DIRECTORY"
    fi

    python "$(dirname "${BASH_SOURCE[0]}")/core.py" reload "$HOME/env.conf" "$SYSENV_OUTPUT_DIRECTORY/bashrc"
    if [ $? == 0 ]; then
        #cat "$SYSENV_OUTPUT_DIRECTORY/bashrc"
        source "$SYSENV_OUTPUT_DIRECTORY/bashrc"
    fi
    rm "$SYSENV_OUTPUT_DIRECTORY/bashrc"
}

#env-mpi-select() {
#    # Do nothing
#}


env-reload

fi
