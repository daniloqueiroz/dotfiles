#!/usr/bin/fish

pgrep -a ssh-agent > /dev/null
if test $status -eq 1
    set -e SSH_AUTH_SOCK
    set -Ux SSH_AUTH_SOCK (ssh-agent | grep SSH_AUTH_SOCK| awk -F'[=;]' '{ print $2 }')
    ssh-add -L
end
