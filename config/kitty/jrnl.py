import os
import subprocess
import re
import logging
import datetime
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from kitty.boss import Boss

# Constants
DEFAULT_JRNL_DIR = "~/journal"
JRNL_TEMPLATE = "## {date}{title_suffix}\n\n"

# Setup logging
logging.basicConfig(
    filename='/tmp/kittens.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s'
)

def get_journal_dir() -> Path:
    """Get the journal directory, prioritizing JRNL_DIR env var."""
    path = os.environ.get("JRNL_DIR")
    if not path:
        path = os.path.expanduser(DEFAULT_JRNL_DIR)
    journal_path = Path(path).resolve()
    journal_path.mkdir(parents=True, exist_ok=True)
    return journal_path

def list_entries(journal_dir: Path) -> List[str]:
    """List markdown files in the journal directory (newest first)."""
    files = sorted(journal_dir.glob("*.md"), reverse=True)
    return [f.stem for f in files if f.is_file()]

def run_fzf(choices: List[str], prompt: str = "Select> ") -> Optional[str]:
    """Helper to run fzf and return selection or arbitrary input."""
    choices_str = "\n".join(choices)
    fzf_cmd = [
        'fzf', 
        '--prompt', prompt, 
        '--layout=reverse',
        '--header=ESC or Ctrl+C to exit',
        '--print-query'
    ]
    try:
        proc = subprocess.run(fzf_cmd, input=choices_str, stdout=subprocess.PIPE, text=True)
        lines = proc.stdout.splitlines()
        if not lines:
            return None
            
        query = lines[0].strip()
        selection = lines[1].strip() if len(lines) > 1 else ""
        
        # Return selection if valid, otherwise return the query
        return selection if selection else query
    except Exception as e:
        logging.error(f"fzf error: {e}")
    return None

def handle_new_entry(journal_dir: Path, title: Optional[str] = None):
    """Create a new journal entry using a temporary file and vim."""
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    date_header = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    title_suffix = f": {title}" if title else ""
    initial_content = JRNL_TEMPLATE.format(date=date_header, title_suffix=title_suffix)
    
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as tmp:
        tmp.write(initial_content)
        tmp_path = tmp.name

    try:
        # Launch vim at line 1
        subprocess.run(['vim', '+1', tmp_path], check=True)

        with open(tmp_path, "r") as f:
            current_content = f.read()

        if current_content.strip() != initial_content.strip():
            today_file = journal_dir / f"{today_str}.md"
            with open(today_file, "a") as f:
                if today_file.exists() and today_file.stat().st_size > 0:
                    f.write("\n\n")
                f.write(current_content.strip())
            logging.info(f"Entry added to {today_file.name}")
        else:
            logging.info("No changes made, entry discarded.")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def main(args: List[str]) -> str:
    logging.info("Kitten jrnl started")
    journal_dir = get_journal_dir()
    
    while True:
        entries = list_entries(journal_dir)
        choices = ["New Entry"] + entries
        
        selection = run_fzf(choices, "Journal> ")
        if not selection:
            break
            
        if selection == "New Entry":
            logging.info("Starting New Entry process (no title)")
            handle_new_entry(journal_dir)
        elif selection in entries:
            file_path = journal_dir / f"{selection}.md"
            if file_path.exists():
                logging.info(f"Viewing entry: {selection}")
                subprocess.run(['glow', '-t', str(file_path)])
            else:
                logging.error(f"File not found: {file_path}")
        else:
            # Arbritrary string entered
            logging.info(f"Starting New Entry process with title: {selection}")
            handle_new_entry(journal_dir, title=selection)

    return ""

def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    pass
