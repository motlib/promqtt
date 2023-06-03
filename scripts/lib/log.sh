#!/bin/bash
#
# Function to print out colored log messages
#
# First param: Log level, one of DEBUG, INFO, WARNING or ERROR
# All further params: The log message
#
# You can set the LOG_LEVEL env. variable to limit output to messages less or 
# equal to this level. If unset, eveything up to level INFO is printed.

function log {
    LEVEL=$1
    shift
    MSG=$*

    declare -A _LOG_LEVELS=(
        ["ERROR"]="0"
        ["WARNING"]="1"
        ["INFO"]="2"
        ["DEBUG"]="3"
    )

    if test -t 1; then
        declare -A _LOG_COLORS=(
            ["ERROR"]="$(tput setaf 1)"
            ["WARNING"]="$(tput setaf 3)"
            ["INFO"]="$(tput setaf 2)"
            ["DEBUG"]="$(tput setaf 5)"
        )
        _NORMAL=$(tput sgr0)
    else
        declare -A _LOG_COLORS=(
            ["ERROR"]=""
            ["WARNING"]=""
            ["INFO"]=""
            ["DEBUG"]=""
        )
        _NORMAL=""
    fi

    # set default log level
    if [ -z "${LOG_LEVEL}" ]; then
        LOG_LEVEL="INFO"
    fi

    # Check if the current and maximum log levels are valid
    [ -z "${_LOG_LEVELS[${LOG_LEVEL}]}" ] && echo "ERROR: Supplied maximum log level '${LOG_LEVEL}' is not supported!!!" && return
    [ -z "${_LOG_LEVELS[${LEVEL}]}" ] && echo "ERROR: Supplied log level '${LEVEL}' is not supported!!!" && return

    _MAX_LEVEL=${_LOG_LEVELS[${LOG_LEVEL}]}
    _COLOR=${_LOG_COLORS[${LEVEL}]}

    if [ "${_LOG_LEVELS[${LEVEL}]}" -le "${_MAX_LEVEL}" ]; then
        echo "${_COLOR}${LEVEL}${_NORMAL}: ${MSG}"
    fi
}
