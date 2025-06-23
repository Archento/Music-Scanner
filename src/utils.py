import os

from src.config import BLACKLIST


def fast_scandir(dirname: str, blacklist: set | None = None) -> list[str]:
    """Fast directory scanner to retrieve all subdirectories."""
    if blacklist is None:
        blacklist = BLACKLIST
    subfolders = [
        f.path
        for f in os.scandir(dirname)
        if f.is_dir() and f.name not in blacklist
    ]
    for dir_name in list(subfolders):
        subfolders.extend(fast_scandir(dir_name))
    return subfolders
