import os
from logging import getLogger

from src.config import BLACKLIST

logger = getLogger(__name__)


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


def write_markdown_file(
    filename: str,
    content: dict[str, list[str]],
    library: dict[str, list[str]],
    overwrite: bool = False,
) -> None:
    """Write content to a markdown file."""
    if not overwrite and os.path.exists(filename):
        if (
            input(
                f"File {filename} already exists. "
                "Do you want to overwrite it? (y/n): "
            )
            .strip()
            .lower()
            != "y"
        ):
            logger.error("File not overwritten. Exiting.")
            return
    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Artist Albums Comparison\n\n")
        f.write(
            "This file contains a list of artists and their albums and "
            "marks them if they are not in the music library.\n"
            "Please note that the results of this scan are entirely based on "
            "the available data on Deezer.\n\n"
        )
        if not content:
            f.write("No artists or albums found in the music library.\n")
            return
        for mapped_artist, mapped_albums in content.items():
            f.write(f"**{mapped_artist}**\n")
            if mapped_albums:
                for album in mapped_albums:
                    if album not in library.get(mapped_artist, []):
                        f.write(f"- {album}  :warning: not in library\n")
                    else:
                        f.write(f"- {album}\n")
            else:
                f.write("- No albums found.\n")
            f.write("\n\n")
    print(f"Markdown file {filename} written successfully.")
