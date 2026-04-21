"""Archive and restore stashes to/from a portable ZIP file."""

import json
import zipfile
import io
from pathlib import Path
from typing import Dict, List

from stashpoint.storage import load_stashes, save_stashes

ARCHIVE_MANIFEST = "manifest.json"
STASHES_FILE = "stashes.json"


class ArchiveError(Exception):
    """Raised when an archive operation fails."""


class StashNotFoundError(Exception):
    """Raised when a requested stash does not exist."""


def create_archive(names: List[str], path: str) -> Dict:
    """Export named stashes into a ZIP archive at *path*.

    Returns a summary dict with the list of archived stash names.
    Raises StashNotFoundError if any requested name is missing.
    """
    all_stashes = load_stashes()
    missing = [n for n in names if n not in all_stashes]
    if missing:
        raise StashNotFoundError(f"Stashes not found: {', '.join(missing)}")

    selected = {n: all_stashes[n] for n in names}
    manifest = {"version": 1, "stashes": names}

    dest = Path(path)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(ARCHIVE_MANIFEST, json.dumps(manifest, indent=2))
        zf.writestr(STASHES_FILE, json.dumps(selected, indent=2))

    return {"archived": names, "path": str(dest)}


def restore_archive(path: str, overwrite: bool = False) -> Dict:
    """Import stashes from a ZIP archive created by *create_archive*.

    Returns a summary dict with lists of restored and skipped stash names.
    Raises ArchiveError if the file is not a valid stashpoint archive.
    """
    src = Path(path)
    if not src.exists():
        raise ArchiveError(f"Archive not found: {path}")

    try:
        with zipfile.ZipFile(src, "r") as zf:
            names_in_zip = zf.namelist()
            if ARCHIVE_MANIFEST not in names_in_zip or STASHES_FILE not in names_in_zip:
                raise ArchiveError("Not a valid stashpoint archive.")
            archived_stashes = json.loads(zf.read(STASHES_FILE))
    except zipfile.BadZipFile as exc:
        raise ArchiveError(f"Cannot read archive: {exc}") from exc

    existing = load_stashes()
    restored, skipped = [], []

    for name, variables in archived_stashes.items():
        if name in existing and not overwrite:
            skipped.append(name)
        else:
            existing[name] = variables
            restored.append(name)

    save_stashes(existing)
    return {"restored": restored, "skipped": skipped}
