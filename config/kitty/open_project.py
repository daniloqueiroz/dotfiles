import os
import subprocess
import logging
import tempfile
from typing import List, Optional
from kitty.boss import Boss

# Setup logging
logging.basicConfig(
    filename='/tmp/kittens.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s'
)

def get_project_selection() -> Optional[str]:
    """Use fd and fzf to let the user select a project root folder."""
    home_dir = os.path.expanduser('~')
    # Use markers: (.git/, .idea/, .env/, src/, .tools_version, .gitignore)
    # Exclude common large directories to speed up search.
    exclude_dirs = [".cache", ".local", "node_modules", ".npm", ".cargo", ".rustup", "Library", "Pictures", "Movies"]
    exclude_args = " ".join([f"-E {d}" for d in exclude_dirs])
    
    # fd search command
    # find markers, echo parent, sort unique, fzf
    cmd = (
        f"fd -H -I -t d -t f {exclude_args} "
        f"'^(\\.git|\\.idea|\\.env|src|\\.tools_version|\\.gitignore)$' "
        f"{home_dir} --max-depth 5 --prune "
        "-x echo {//} | sort -u | fzf --prompt='Select Project> '"
    )
    
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception as e:
        logging.error(f"Error selecting project: {e}")
    return None

def main(args: List[str]) -> str:
    logging.info(f"Open Project kitten started with args: {args}")
    
    folder = None
    # If a parameter is passed and it's a valid folder, use it as project root.
    if len(args) > 1:
        potential_dir = args[1]
        if os.path.isdir(potential_dir):
            folder = os.path.abspath(potential_dir)
            logging.info(f"Using directory from arguments: {folder}")

    if not folder:
        folder = get_project_selection()
        
    if not folder:
        return ""
        
    logging.info(f"selected project folder: {folder}")
    return folder

def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    try:
        if not answer:
           return
        
        project_root = answer
        project_name = os.path.basename(project_root.rstrip(os.sep))
        
        # This creates a new TAB in the current OS window
        first_window = boss.launch('--type=tab', '--tab-title', project_name, '--cwd', project_root, '--', 'fish', '-c', 'fresh')

        # Set layout to tall in the new tab
        if boss.active_tab:
            boss.active_tab.goto_layout('tall')

            # These commands launch PANES inside the new tab
            #first_window = boss.launch('--type=window', '--cwd', project_root, '--', 'fish', '-c', 'fresh')
            boss.launch('--type=window', '--cwd', project_root, '--', 'fish', '-c', 'gemini')
            boss.launch('--type=window', '--cwd', project_root, '--', 'fish', '-c', 'gitui')
            
            # Set focus to the first window
            if first_window:
                boss.set_active_window(first_window)
        
    except Exception as e:
        logging.exception(f"Command failed: {e}")
