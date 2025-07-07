![banner](https://github.com/Archento/Music-Scanner/blob/main/banner.jpg)

# Music Scanner

A simple tool to scan your local music files and identify missing albums, while automatically downloading artist images and album covers.

## Requires

- [Python](https://www.python.org) 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for package management
- Fill out the `.env` file with your MariaDB connection details.
- [MariaDB](https://mariadb.com) for storing artist and album information

## Features

- [x] Scan local music files
- [x] Identify missing albums
- [x] Connect to a remote MariaDB database
- [x] Download artist image automatically ("folder.jpg")
- [ ] Download album covers automatically ("cover.jpg")
- [x] Save the list to a file
- [x] CLI interface

## Usage

To run the Music Scanner, you can use the following command:

```bash
uv run main.py --p /path/to/your/music/library --v
```

## CLI

```
usage: music-scanner [-h] [-p PATH] [-v]

Scan your local music library and retrieve artist and album information.

options:
  -h, --help       show this help message and exit
  -p, --path PATH  The path to the music library. (default: .)
  -v, --verbose    Enable verbose file and cli output. (default: False)

source: https://github.com/Archento/Music-Scanner
```
