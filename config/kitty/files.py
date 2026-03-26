import os
import subprocess
import logging
from typing import List
from kitty.boss import Boss
from kittens.tui.loop import debug

# Setup logging
logging.basicConfig(
    filename='/tmp/kittens.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s'
)

def main(args: List[str]) -> str:
    logging.info(f"Files kitten started with args: {args}")
    # Always launch from home directory
    folder = os.path.expanduser('~')
    logging.info(f"selected folder: {folder}")
    return folder

def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    try:
        debug(f"folder: {answer}")
        if not answer:
           return
        cmd = ['xplr']
        tab_title = "Files"

        # Always launch a new tab
        boss.launch('--type=tab', '--tab-title', tab_title, '--cwd', answer, '--', *cmd)
    except Exception as e:
        logging.exception(f"Command failed: {e}")
