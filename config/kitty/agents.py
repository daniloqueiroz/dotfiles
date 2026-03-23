import os
import subprocess
import re
import logging
from typing import List, Optional, Tuple
from kitty.boss import Boss

# Setup logging
logging.basicConfig(
    filename='/tmp/kitten-agents.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_folder_selection() -> Optional[str]:
    """Use fd and fzf to let the user select a folder."""
    home_dir = os.path.expanduser('~')
    cmd = f"fd -t d . {home_dir} | fzf --prompt='Select Folder> '"
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if proc.returncode == 0:
            return proc.stdout.strip()
    except Exception as e:
        logging.error(f"Error selecting folder: {e}")
    return None

def get_gemini_sessions(cwd: str) -> List[str]:
    """Extract sessions from gemini --list-sessions."""
    try:
        result = subprocess.run(['gemini', '--list-sessions'], capture_output=True, text=True, cwd=cwd)
        output = result.stdout
        lines = output.splitlines()
        session_lines = []
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.', line):
                session_lines.append(line)
        return session_lines
    except Exception as e:
        logging.error(f"Error fetching sessions: {e}")
        return []

def get_user_selection(choices: List[str], folder: str) -> Tuple[Optional[str], Optional[str]]:
    """Use fzf to let the user select a session or delete one."""
    choices_str = "\n".join(choices)
    fzf_cmd = [
        'fzf',
        '--expect=ctrl-d',
        f'--header=Folder: {folder} | Enter: Resume/Start session | Ctrl+D: Delete selected session',
        '--prompt=Session> '
    ]
    try:
        fzf_proc = subprocess.run(fzf_cmd, input=choices_str, stdout=subprocess.PIPE, text=True)
        fzf_out = fzf_proc.stdout.splitlines()
        
        if fzf_proc.returncode != 0 and len(fzf_out) <= 1:
            return None, None
            
        key = fzf_out[0].strip() if len(fzf_out) > 0 else ""
        selected = fzf_out[1].strip() if len(fzf_out) > 1 else ""
        return key, selected
    except Exception as e:
        logging.error(f"Error in fzf selection: {e}")
        return None, None

def parse_session_index(answer: str) -> Optional[str]:
    """Extract the index number from the session string."""
    match = re.match(r'^(\d+)\.', answer)
    return match.group(1) if match else None

def main(args: List[str]) -> str:
    logging.info("Main started")
    folder = get_folder_selection()
    if not folder:
        return ""
        
    while True:
        session_lines = get_gemini_sessions(folder)
        choices = ["<New Session>"] + session_lines
        
        key, selected = get_user_selection(choices, folder)
        
        if not selected:
            return ""
            
        if key == 'ctrl-d':
            if selected == "<New Session>":
                continue
            index = parse_session_index(selected)
            if index:
                logging.info(f"Deleting session {index} in {folder}")
                subprocess.run(['gemini', '--delete-session', index], cwd=folder)
            continue
            
        logging.info(f"Returning selection: {selected} in {folder}")
        return f"{folder}\n{selected}"

def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    logging.info(f"handle_result: answer='{answer}', target_window_id={target_window_id}")
    if not answer:
        return
        
    parts = answer.split('\n', 1)
    if len(parts) != 2:
        logging.error(f"Invalid answer format: {answer}")
        return
    folder, session = parts
       
    # Prepare command
    cmd = ['gemini']
    if session != "<New Session>":
        index = parse_session_index(session)
        if index:
            cmd.extend(['--resume', index])
        else:
            logging.error(f"Failed to parse index: {session}")
            return
    logging.info(f"command: `{' '.join(cmd)}` in `{folder}`")

    tab_title = "Agents"
    existing_tab = None
    logging.info("--- Current Tabs ---")
    for tab in boss.active_tab_manager.tabs:
        logging.info(f"Tab ID: {tab.id}, Title: '{tab.title}', Name: '{tab.name}'")
          
        # Match by name
        if tab.name == tab_title: 
            existing_tab = tab
            break
    logging.info("--------------------")

    try:
        if existing_tab:
            logging.info(f"Reusing tab {existing_tab.id}")
            # Focus the existing tab first
            boss.set_active_tab(existing_tab)
            # Launch window in the active tab (which is now the Agents tab)
            boss.launch('--type=window', '--cwd', folder, '--', *cmd)
        else:
            logging.info("Creating new tab")
            # Create tab in current OS window
            boss.launch('--type=tab', '--tab-title', tab_title, '--cwd', folder, '--', *cmd)
            # Set layout to grid (it operates on the active tab)
            if boss.active_tab:
                boss.active_tab.goto_layout('grid')
    except Exception as e:
        logging.exception(f"Command failed: {e}")
