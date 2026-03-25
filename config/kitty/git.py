import os
import subprocess
import logging
from typing import List, Optional
from kitty.boss import Boss
from kittens.tui.loop import debug

# Setup logging
logging.basicConfig(
    filename='/tmp/kittens.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s'
)

def get_folder_selection() -> Optional[str]:
    """Use fd and fzf to let the user select a Git repository root."""
    home_dir = os.path.expanduser('~')
    # Search for .git directories and get their parents
    cmd = f"fd -H -t d '^\\.git$' {home_dir} --prune -x echo {{//}} | fzf --prompt='Select Git Repo> '"
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception as e:
        logging.error(f"Error selecting folder: {e}")
    return None

def main(args: List[str]) -> str:
    logging.info(f"Git kitten started with args: {args}")
    
    folder = None
    # args[0] is the path to the kitten script itself
    if len(args) > 1:
        potential_dir = args[1]
        if os.path.isdir(potential_dir):
            folder = os.path.abspath(potential_dir)
            logging.info(f"Using directory from arguments: {folder}")

    if not folder:
        folder = get_folder_selection()
        
    if not folder:
        return ""
    logging.info(f"selected folder: {folder}")
    return folder

def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    try:
        debug(f"folder: {answer}")
        if not answer:
           return
        cmd = ['tig']
        folder_name = os.path.basename(answer.rstrip(os.sep))
        tab_title = f"Git {folder_name}"

        # Always launch a new tab
        boss.launch('--type=tab', '--tab-title', tab_title, '--cwd', answer, '--', *cmd)
    except Exception as e:
        logging.exception(f"Command failed: {e}")
