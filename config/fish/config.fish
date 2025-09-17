# load files from conf.d dir
if status is-interactive
    if test -z "$TERMINALSESSION"; and test "$TERM_PROGRAM" = "ghostty"
        # enter terminalsession if TERMINALSESSION is not set and running in Ghostty
        /usr/bin/tsctl
    end


    fzf_key_bindings

    for conf in ~/.config/fish/conf.d/*.fish
        source $conf
    end 

    set -e fish_greeting

    # configure less colors / colored man pages
    set -xg LESS_TERMCAP_mb (printf "\e[01;31m")      # begin blinking
    set -xg LESS_TERMCAP_md (printf "\e[01;31m")      # begin bold
    set -xg LESS_TERMCAP_me (printf "\e[0m")          # end mode
    set -xg LESS_TERMCAP_se (printf "\e[0m")          # end standout-mode
    set -xg LESS_TERMCAP_so (printf "\e[01;44;33m")   # begin standout-mode - info box
    set -xg LESS_TERMCAP_ue (printf "\e[0m")          # end underline
    set -xg LESS_TERMCAP_us (printf "\e[01;32m")      # begin underline

    # load on_pwd_changed handle
    on_pwd_changed
end
