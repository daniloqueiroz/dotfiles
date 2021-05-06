#!/bin/bash


notes_app=/home/danilopenna/tools/Obsidian-0.8.15.AppImage
notes_class=obsidian
pids=$(xdotool search --class obsidian)


function window_props() {
    w_pid=$1
    current_desktop=$(bspc query -D -d focused)
    bspc node $w_pid --to-desktop $current_desktop
    bspc node $w_pid -t floating
    bspc node $w_pid --focus
}


if [ -z "$pids" ]; then
    $notes_app &
    sleep 10s
    pids=$(xdotool search --class obsidian)
    for pid in $pids; do
        window_props $pid
    done
else
    for pid in $pids; do
        window_props $pid
        bspc node $pid --flag hidden -f
    done
fi

