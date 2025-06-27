import json
import os
from logging import getLogger

import requests

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


def write_json_file(
    filename: str,
    content: dict[str, list[str]],
    sort_keys: bool = True,
):
    """Write content to a JSON file."""
    if not filename.endswith(".json"):
        filename += ".json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(content, indent=4, sort_keys=sort_keys))


def _write_markdown_file(
    filename: str,
    text_content: str,
    overwrite: bool = False,
) -> None:
    """Write content to a markdown file."""
    if not filename.endswith(".md"):
        filename += ".md"
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
        f.write(text_content)
    logger.info("Markdown file %s written successfully.", filename)


def write_results_markdown(
    filename: str,
    content: dict[str, list[str]],
    library: dict[str, list[str]],
    overwrite: bool = False,
) -> None:
    """Write results to a markdown file."""

    text_content = """# Artist Albums Comparison

    This file contains a list of artists and their albums and marks them if they are not in the music library.
    Please note that the results of this scan are entirely based on the available data on Deezer.

    """
    if not content:
        text_content += "No artists or albums found in the music library.\n"
        _write_markdown_file(filename, text_content, overwrite)
        return

    for mapped_artist, mapped_albums in content.items():
        text_content += f"\n**{mapped_artist}**\n"
        if mapped_albums:
            for album in mapped_albums:
                if album not in library.get(mapped_artist, []):
                    text_content += f"- {album}  :warning: not in library\n"
                else:
                    text_content += f"- {album}\n"
        else:
            text_content += "- No albums found.\n"
        text_content += "\n\n"

    _write_markdown_file(filename, text_content, overwrite)


def write_diff_markdown(
    filename: str,
    content: dict[str, list[str]],
    overwrite: bool = False,
) -> None:
    """Write differences to a markdown file."""

    text_content = """# Artist Albums Comparison

    This file contains a list of artists and their albums which are not in the music library
    or new since the last scan.
    Please note that the results of this scan are entirely based on the available data on Deezer.

    """
    if not content:
        text_content += "No changes detected.\n"
        _write_markdown_file(filename, text_content, overwrite)
        return

    for mapped_artist, mapped_albums in content.items():
        text_content += f"\n**{mapped_artist}**\n"
        if mapped_albums:
            for album in mapped_albums:
                text_content += f"- {album}\n"
        else:
            text_content += "- No albums found.\n"
        text_content += "\n\n"

    _write_markdown_file(filename, text_content, overwrite)


def download_image(
    url: str,
    filename: str = "artist",
    download_path: str = "./",
):
    """
    Download an image from a URL and save it to the specified path.
    """
    file = f"{download_path}{filename}.jpg"
    try:
        if os.path.exists(file):
            logger.debug("File %s already exists. Skipping download.", file)
            return
        img_data = requests.get(url, timeout=10).content
        with open(file, "wb") as handler:
            handler.write(img_data)
    except Exception as e:
        logger.error("Failed to download artist image for '%s': %s", file, e)
