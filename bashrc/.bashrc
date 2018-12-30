# Custom configuration for bash.

# PS1 settings.
return_code_color() {
    RETVAL=$?
    if [ "${RETVAL}" -ne 0 ]; then
        printf '\033[01;31m' # error -> red
    else
        printf '\033[01;32m' # success -> green
    fi
    return "${RETVAL}" # preserve return code
}

show_return_code() {
    python3 -c "print('[%s]' % '$?'.center(3))"
}

user_color() {
    if [ "`id -u`" -eq 0 ]; then
        printf '\033[01;31m' # root -> red
    else
        printf '\033[01;32m' # non-root -> green
    fi
}

parse_git_branch() {
    BRANCH=`git branch 2> /dev/null | sed -n 's/^\* //p'`
    if [ -n "${BRANCH}" ]; then
        if [ -n "`git status --porcelain`" ]; then
            STAT=' *' # modified
        else
            STAT='' # clean
        fi
        printf %s " (${BRANCH}${STAT})"
    fi
}

export PS1="${debian_chroot:+($debian_chroot)}\[\`return_code_color\`\]\`show_return_code\` \[\033[01;33m\][\t] \[\`user_color\`\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[01;35m\]\`parse_git_branch\`\[\033[00m\]\n\\$ "

# History grepping.
hgrep() {
    if [ -z "$1" ]; then
        echo 'hgrep: missing keyword'
        return 1
    fi

    history | egrep -- "$1"
}

# List all processes.
alias pa='sudo ps aux'

# List all listening ports.
alias lp='sudo netstat -46lnp'

# Kill the process listening on a TCP port.
rp() {
    if [ -z "$1" ]; then
        echo 'rp: missing port'
        return 1
    fi

    PORT_PID=`sudo lsof -n -P "-iTCP:$1" -sTCP:LISTEN | tail -n +2 | awk '{ print $2 }' | head -n 1`

    if [ -z "${PORT_PID}" ]; then
        echo "rp: no process listening on port $1"
        return 1
    fi

    sudo kill -- "${PORT_PID}"
}

# Do SSH port forwarding that keeps alive in the background.
alias spf='ssh -fNT -o ServerAliveInterval=30 -o ServerAliveCountMax=10'

# List active SSH port forwarding.
alias lspf='pgrep -a '\''^ssh$'\'' | `which grep` -P --color=never '\''\s-[LRD]\s'\'''

# Set Python interactive startup file.
export PYTHONSTARTUP=/path/to/python_startup # TODO: change this to your path to the startup file
