# Git prompt
# https://fishshell.com/docs/current/cmds/fish_git_prompt.html
set __fish_git_prompt_use_informative_chars 'yes'
set __fish_git_prompt_showdirtystate 'yes'
set __fish_git_prompt_showuntrackedfiles 'yes'
set __fish_git_prompt_showcolorhints 'yes'
set __fish_git_prompt_showupstream 'informative'

# Git Status
#set __fish_git_prompt_char_dirtystate '*'
#set __fish_git_prompt_char_stagedstate '⇢'
#set __fish_git_prompt_char_upstream_prefix ' '
#set __fish_git_prompt_char_upstream_equal ''
#set __fish_git_prompt_char_upstream_ahead '⇡'
#set __fish_git_prompt_char_upstream_behind '⇣'
#set __fish_git_prompt_char_upstream_diverged '⇡⇣'

function fish_prompt --description 'Write out the prompt'
  set -l last_status $status

  prompt_login
  echo -n ':'
  set_color $fish_color_cwd
  echo -n (prompt_pwd)
  set_color normal

  # GIT
  fish_git_prompt

  if not test $last_status -eq 0
    set_color $fish_color_error
  end

  # Prompt
  echo -n ' ❯ '
  set_color normal
end


function fish_right_prompt
  # TerminalSession - show current tab name
  if set -q TERMINALSESSION
    set_color $nord15
    echo -n "$TERMINALSESSION "
    set_color $nord7
    echo -n "[C-u to detatch] "
    set_color normal
  end
end
