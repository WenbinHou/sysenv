
if [ -z "$SYSENV_OUTPUT_DIRECTORY" ]; then
export SYSENV_OUTPUT_DIRECTORY="/dev/shm/sysenv/${RANDOM}${RANDOM}${RANDOM}${RANDOM}"

env-reload() {
    if [ ! -d "$SYSENV_OUTPUT_DIRECTORY" ]; then
        mkdir -p "$SYSENV_OUTPUT_DIRECTORY"
    fi

    python /sysenv/core.py reload ~/env.conf "$SYSENV_OUTPUT_DIRECTORY/bashrc"

    #cat "$SYSENV_OUTPUT_DIRECTORY/bashrc"
    source "$SYSENV_OUTPUT_DIRECTORY/bashrc"
    rm "$SYSENV_OUTPUT_DIRECTORY/bashrc"
}

#env-mpi-select() {
#    # Do nothing
#}


env-reload

fi
