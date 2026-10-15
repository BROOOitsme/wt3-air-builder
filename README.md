# WT3 Air Builder

War Thunder Air Test Drive generator for Linux.

Generates custom user missions with weightless loadouts, weapon overrides,
custom targets, and more.

## Requirements

- Python 3.10+
- PySide6
- War Thunder (Steam, Flatpak, or Snap)
- `wt_ext_cli` on your PATH or in this directory

## Install

Fedora / Nobara:
    sudo dnf install python3-pyside6

Debian / Ubuntu:
    sudo apt install python3-pyside6.qtwidgets

Arch / Manjaro:
    sudo pacman -S pyside6

openSUSE:
    sudo zypper install python3-pyside6

Or via pip (any distro):
    pip install --user -r requirements.txt

## Usage

    python3 wt3-builder-air.py

## License

MIT
