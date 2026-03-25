import os
import subprocess
import re
import logging
import datetime
from pathlib import Path
from typing import List, Optional, Tuple
from kitty.boss import Boss

# Setup logging
logging.basicConfig(
    filename='/tmp/kittens.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(module)s:%(funcName)s - %(message)s'
)
DEFAULT_NOTES_DIR = "~/workspace/notes"

def get_notes_dir() -> Path:
    path = os.environ.get("NOTES_DIR", DEFAULT_NOTES_DIR)
    notes_path = Path(path).expanduser().resolve()
    notes_path.mkdir(parents=True, exist_ok=True)
    return notes_path

def list_notes(notes_dir: Path) -> List[Path]:
    files = []
    # Find all .md files, ignoring those inside 'archive'
    for f in notes_dir.rglob("*.md"):
        if "archive" not in f.parts:
            files.append(f)
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

def run_fzf_list(choices: List[str], cwd: Path) -> Tuple[Optional[str], Optional[str], str]:
    choices_str = "\n".join(choices)
    fzf_cmd = [
        'fzf', 
        '--prompt', 'Notes> ', 
        '--layout=reverse',
        '--header', 'Enter:View | C-e:Edit | C-a:Archive | C-s:Search Content | C-n:New Note | ESC:Exit',
        '--expect', 'ctrl-e,ctrl-a,ctrl-s,ctrl-n',
        '--print-query',
        '--preview', 'glow -p {}'
    ]
    try:
        proc = subprocess.run(fzf_cmd, input=choices_str, cwd=cwd, stdout=subprocess.PIPE, text=True)
        lines = proc.stdout.splitlines()
        if not lines:
            return None, None, ""
            
        query = lines[0].strip()
        key = lines[1].strip() if len(lines) > 1 else ""
        selection = lines[2].strip() if len(lines) > 2 else ""
        
        return key, selection, query
    except Exception as e:
        logging.error(f"fzf error: {e}")
        return None, None, ""

def run_fzf_search(notes_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    # Dynamic ripgrep search using fzf
    RG_PREFIX = "rg --column --line-number --no-heading --color=always --smart-case --type md --glob '!archive/*'"
    fzf_cmd = [
        'fzf',
        '--ansi', '--disabled',
        '--prompt', 'Search Content> ',
        '--bind', f'start:reload:{RG_PREFIX} ""',
        '--bind', f'change:reload:sleep 0.1; {RG_PREFIX} {{q}} || true',
        '--delimiter', ':',
        '--preview', 'glow -p {1}',
        '--preview-window', 'up,60%,border-bottom',
        '--header', 'Enter:View | C-e:Edit | C-a:Archive | C-l:List Mode | ESC:Exit',
        '--expect', 'ctrl-e,ctrl-a,ctrl-l'
    ]
    try:
        proc = subprocess.run(fzf_cmd, cwd=notes_dir, stdout=subprocess.PIPE, text=True)
        lines = proc.stdout.splitlines()
        if not lines:
            return None, None
        key = lines[0].strip()
        selection = lines[1].strip() if len(lines) > 1 else ""
        if selection:
            # Format: filename:line:col:text
            selection = selection.split(':', 1)[0]
        return key, selection
    except Exception as e:
        logging.error(f"fzf search error: {e}")
        return None, None

def archive_note(notes_dir: Path, filename: str):
    src = notes_dir / filename
    archive_dir = notes_dir / "archive"
    dst = archive_dir / Path(filename).name
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        logging.info(f"Archived {filename}")

def create_note(notes_dir: Path, title: str):
    title_slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-') if title else "note"
    date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{date_str}-{title_slug}.md"
    file_path = notes_dir / filename
    
    header_title = title if title else "New Note"
    content = f"# {header_title}\n\n"
    with open(file_path, "w") as f:
        f.write(content)
        
    edit_note(file_path)

def edit_note(file_path: Path):
    editor = os.environ.get("EDITOR", "vim")
    subprocess.run([editor, str(file_path)])

def view_note(file_path: Path):
    subprocess.run(['glow', '-t', str(file_path)])

def main(args: List[str]) -> str:
    logging.info("Kitten notes started")
    notes_dir = get_notes_dir()
    
    archive_dir = notes_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    mode = "list"

    while True:
        if mode == "list":
            files = list_notes(notes_dir)
            choices = [str(f.relative_to(notes_dir)) for f in files]
            
            key, selection, query = run_fzf_list(choices, notes_dir)
            
            if key is None and not query and not selection:
                break
                
            if key == 'ctrl-s':
                mode = "search"
                continue
                
            if key == 'ctrl-n':
                create_note(notes_dir, query)
                continue
                
            target = selection if selection else query
            if not target:
                continue
                
            if key == 'ctrl-a':
                if target in choices:
                    archive_note(notes_dir, target)
                continue
                
            if key == 'ctrl-e':
                if target in choices:
                    edit_note(notes_dir / target)
                else:
                    create_note(notes_dir, target)
                continue
                
            # Enter (no key captured for enter in --expect usually, but it means view)
            if target in choices:
                view_note(notes_dir / target)
            else:
                create_note(notes_dir, target)
                
        elif mode == "search":
            key, selection = run_fzf_search(notes_dir)
            
            if key is None and not selection:
                mode = "list"
                continue
                
            if key == 'ctrl-l':
                mode = "list"
                continue
                
            if not selection:
                continue
                
            if key == 'ctrl-a':
                archive_note(notes_dir, selection)
                continue
                
            if key == 'ctrl-e':
                edit_note(notes_dir / selection)
                continue
                
            # Enter
            view_note(notes_dir / selection)

    return ""

def handle_result(args: List[str], answer: str, target_window_id: int, boss: Boss) -> None:
    pass
