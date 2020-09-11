#!/bin/bash
stow -vR -t ~ home/
stow -vR -t ~/.config/ config

mkdir -p ~/tools/utils
stow -vR -t ~/tools/utils utils
