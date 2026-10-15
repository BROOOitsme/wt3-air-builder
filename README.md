# WT3 Air Builder

A War Thunder **Air Test Drive generator** for Linux.

Builds custom user missions with configurable loadouts, weightless weapons,
foreign-weapon overrides, custom targets, weather, and gameplay tweaks — all
through a native Qt interface. No Windows, no Wine, no manual `.blk` editing.

---

## Quick start

    curl -sL https://raw.githubusercontent.com/BROOOitsme/wt3-air-builder/main/build.sh | bash
    ./wt3-air-builder-release/wt3-air-builder

The bootstrap script downloads the source, installs PySide6 + PyInstaller into
a temporary virtual environment, builds a single-file binary, and drops a
self-contained `wt3-air-builder-release/` folder in your current directory.

Nothing on your system is modified except that output folder.

---

## Requirements

**For the bootstrap build (once):**

- Python 3.10 or newer
- `git`
- An internet connection for the first run

Missing system packages (`python3-venv`, `git`) are installed automatically
via your distro's package manager. The script detects apt, dnf, pacman, and
zypper.

**On the target machine (once the release folder is built):**

- War Thunder installed via Steam
- War Thunder CDK (needed for `aces.vromfs.bin` access)
- Nothing else — Python is bundled inside the binary

Works with native Steam, Flatpak Steam, and Snap Steam.

---

## Manual build

If you'd rather run the build by hand:

    git clone https://github.com/BROOOitsme/wt3-air-builder.git
    cd wt3-air-builder
    ./build.sh

That produces `wt3-air-builder-release/` in the same folder.

You can also point the output somewhere else:

    ./build.sh /opt/games
    # → /opt/games/wt3-air-builder-release/

---

## Usage

Open the app:

    ./wt3-air-builder-release/wt3-air-builder

### 1. Player

Click the aircraft button at the top to pick your plane. Filter by nation,
rank, or type. Search by name or vehicle ID.

Once a plane is selected, its pylons appear as a horizontal strip of slot
cards. Click a card to pick a weapon for that pylon. Hover a weapon in the
picker to see its mass, modification requirements, and incompatibility list.

### 2. Experimental

- **Weapon Override** — swap the entire cannon/launcher for a custom one
- **Engine Override** — change horsepower, mass, RPM limits
- **Rapid Fire** — increase the gun's rate of fire
- **No Recoil** — zero out the gun kick and camera shake
- **Shell Override** — set the bullet's speed, caliber, mass, and filler

### 3. Targets

Choose up to five ground targets, a mover, an enemy aircraft, a helicopter,
and up to three ships. Each slot has a **Respawn** checkbox with a shared
delay spinbox.

### 4. Gameplay

- Weather and time of day
- Player immortality
- Enemy AI skill and accuracy
- Enemies ignore player
- Aced crew and research modules

### 5. Generate

Click **GENERATE AIR MISSION**. The mission lands at:

    ~/.local/share/Steam/steamapps/common/War Thunder/UserMissions/Ask3lad/ask3lad_testdrive_air.blk

In-game: **Hangar → User Missions → Ask3lad → Test Drive 3.0 - Air**.

---

## Features

- **Weightless loadouts** — carried weapons contribute zero drag and mass
- **Foreign weapon override** — mount any weapon from any plane on any pylon
  by substituting the blk path inside the target's native preset
- **Full loadout grid** — per-pylon selection with type filters, mass display,
  and icon preview
- **Cross-distro** — Steam install detected in all standard locations,
  PySide6 install hints tailored per distro
- **Spoofed ownership** — write a stub at `flightModels/ask3lad_air_player.blk`
  that includes any plane's real file, bypassing ownership checks
- **Self-contained release folder** — the built binary finds `database/` and
  `templates/` next to itself, no environment variables needed

---

## Layout of a release folder

    wt3-air-builder-release/
    ├── wt3-air-builder      the app (single-file executable)
    ├── database/            vehicle data, icons, and mod metadata
    ├── templates/           mission .blk templates
    ├── wt_ext_cli           vromfs extraction tool
    └── README.txt           quick start note

Keep the folder together. If you move the binary, move the three data folders
with it.

---

## Troubleshooting

### "Steam installation not found"

The script checks these locations:

    ~/.local/share/Steam
    ~/.steam/steam
    ~/.var/app/com.valvesoftware.Steam/.local/share/Steam
    ~/snap/steam/common/.local/share/Steam

If your War Thunder is in a custom Steam library on another drive, edit
`find_steam_root()` in the script and add the path, or create a symlink:

    ln -s /path/to/your/library ~/.steam/steam/steamapps

### "PySide6 not installed"

The error message prints the exact command for your distro. For example on
Fedora it says `sudo dnf install python3-pyside6`; on Debian it says
`sudo apt install python3-pyside6.qtwidgets`. Or use `pip install --user PySide6`.

### Aircraft doesn't spawn

Three things to check:

1. `content/pkg_local/gameData/flightModels/ask3lad_air_player.blk` exists on disk
2. The mission's `unit_class:t="ask3lad_air_player"` matches the filename exactly
3. War Thunder CDK is installed and `aces.vromfs.bin` is readable

### Large binary, slow startup

The single-file binary is 60–100 MB and unpacks itself to `/tmp` on first
launch. Subsequent launches reuse the extracted cache. To skip this entirely,
build with `--onedir` instead of `--onefile` in `build.sh` — you get a folder
instead of a file, and startup is instant.

---

## Known limitations

- PyInstaller binaries are compiled against your glibc. Running on an older
  distro than the one you built on may fail. If you need broad compatibility,
  build inside a container of the oldest distro you want to support.
- Steam libraries on non-standard paths need the symlink or manual edit
  described above.
- The Bootstrap build script requires `sudo` for the first run if `python3-venv`
  or `git` are missing. Everything after that runs entirely in user space.

---

## License

MIT. See [LICENSE](LICENSE).
