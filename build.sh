#!/usr/bin/env bash
# build.sh — standalone bootstrap builder for wt3-air-builder.
#
# Usage:
#   ./build.sh              # build into ./wt3-air-builder-release/
#   ./build.sh /some/dir    # build into /some/dir/wt3-air-builder-release/
#
# What it does:
#   1. Checks python3, pip, git, and system build tools
#   2. Installs PySide6 + PyInstaller into a throwaway venv
#   3. Uses the local repo if this script is inside one,
#      otherwise downloads it from GitHub
#   4. Builds a single-file binary
#   5. Assembles a release/ folder with the binary and its data
#   6. Copies the release folder into the target directory
#
# Nothing on your system is modified except:
#   - Distro packages needed for the venv (asked via sudo, once)
#   - The output folder you point it at

set -euo pipefail

# ---------- Configurable ----------

REPO_URL="https://github.com/BROOOitsme/wt3-air-builder.git"
REPO_BRANCH="main"
ENTRY_SCRIPT="wt3-air-v3.py"
BIN_NAME="wt3-air-builder"
RELEASE_NAME="wt3-air-builder-release"

# ---------- Args / paths ----------

OUTPUT_PARENT="${1:-$PWD}"
OUTPUT_DIR="$OUTPUT_PARENT/$RELEASE_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

WORK_DIR=""
SOURCE_DIR=""
<<<<<<< HEAD
=======
VENV_PARENT=""
>>>>>>> b555796 (Bootstrap build script with venv cleanup)
VENV_DIR=""

cleanup() {
    if [ -n "$WORK_DIR" ] && [ -d "$WORK_DIR" ]; then
        rm -rf "$WORK_DIR"
    fi
<<<<<<< HEAD
=======
    if [ -n "$VENV_PARENT" ] && [ -d "$VENV_PARENT" ]; then
        rm -rf "$VENV_PARENT"
    fi
>>>>>>> b555796 (Bootstrap build script with venv cleanup)
}
trap cleanup EXIT

# ---------- Pretty printing ----------

say()  { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!! \033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mERR\033[0m %s\n' "$*" >&2; exit 1; }

# ---------- Distro detection ----------

DISTRO_ID=""
DISTRO_LIKE=""
if [ -f /etc/os-release ]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    DISTRO_ID="${ID:-}"
    DISTRO_LIKE="${ID_LIKE:-}"
fi
DISTRO_FAMILY="$DISTRO_ID $DISTRO_LIKE"

install_system_pkg() {
    local pkg_deb="$1" pkg_fed="$2" pkg_arch="$3" pkg_suse="$4"
    case "$DISTRO_FAMILY" in
        *debian*|*ubuntu*)  sudo apt update && sudo apt install -y "$pkg_deb" ;;
        *fedora*|*rhel*|*nobara*) sudo dnf install -y "$pkg_fed" ;;
        *arch*|*manjaro*)   sudo pacman -S --noconfirm "$pkg_arch" ;;
        *suse*|*opensuse*)  sudo zypper --non-interactive install "$pkg_suse" ;;
        *) return 1 ;;
    esac
}

# ---------- Prerequisite checks ----------

say "Checking prerequisites"

if ! command -v python3 >/dev/null 2>&1; then
    die "python3 is required. Install it with your distro's package manager."
fi

PY_OK=$(python3 -c 'import sys; print("yes" if sys.version_info >= (3,10) else "no")')
if [ "$PY_OK" != "yes" ]; then
    die "Python 3.10+ required. Your version: $(python3 -V)"
fi

if ! python3 -c 'import venv' 2>/dev/null; then
    say "Installing python3-venv (needs sudo, one time)"
    install_system_pkg python3-venv python3 python python3-virtualenv \
        || die "Could not auto-install python3-venv. Install it manually."
fi

if ! command -v git >/dev/null 2>&1; then
    say "Installing git (needs sudo, one time)"
    install_system_pkg git git git git \
        || die "Could not auto-install git. Install it manually."
fi

# ---------- Locate source ----------

if [ -f "$SCRIPT_DIR/$ENTRY_SCRIPT" ] && [ -d "$SCRIPT_DIR/database" ]; then
    say "Using local repo at $SCRIPT_DIR"
    SOURCE_DIR="$SCRIPT_DIR"
else
    WORK_DIR="$(mktemp -d)"
    SOURCE_DIR="$WORK_DIR/wt3-air-builder"
    say "Cloning $REPO_URL"
    git clone --depth 1 --branch "$REPO_BRANCH" "$REPO_URL" "$SOURCE_DIR" \
        || die "Could not clone $REPO_URL. Check the URL and your network."
fi

# ---------- Build venv ----------

<<<<<<< HEAD
VENV_DIR="$(mktemp -d)/venv"
=======
VENV_PARENT="$(mktemp -d)"
VENV_DIR="$VENV_PARENT/venv"
>>>>>>> b555796 (Bootstrap build script with venv cleanup)
say "Creating build venv at $VENV_DIR"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

say "Upgrading pip inside venv"
pip install --quiet --upgrade pip

say "Installing PySide6 and PyInstaller (this can take a few minutes)"
pip install --quiet "PySide6>=6.6.0" pyinstaller \
    || die "pip install failed. Check your network connection."

# ---------- Build ----------

say "Building binary"
cd "$SOURCE_DIR"
rm -rf build dist "$BIN_NAME.spec"

pyinstaller \
    --onefile \
    --noconfirm \
    --name "$BIN_NAME" \
    --exclude-module tkinter \
    --exclude-module PySide6.QtWebEngineCore \
    --exclude-module PySide6.QtWebEngineWidgets \
    --exclude-module PySide6.Qt3DCore \
    --exclude-module PySide6.QtQuick \
    --exclude-module PySide6.QtQml \
    "$ENTRY_SCRIPT" \
    || die "PyInstaller build failed."

[ -f "dist/$BIN_NAME" ] || die "Binary not found at dist/$BIN_NAME after build."

# ---------- Assemble release ----------

say "Assembling release folder"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

cp "dist/$BIN_NAME" "$OUTPUT_DIR/$BIN_NAME"
chmod +x "$OUTPUT_DIR/$BIN_NAME"

if [ -d "database" ]; then
    cp -r database "$OUTPUT_DIR/database"
    find "$OUTPUT_DIR/database" -name '*.tmp' -delete 2>/dev/null || true
else
    warn "database/ not in source — release will not have vehicle data"
fi

if [ -d "templates" ]; then
    cp -r templates "$OUTPUT_DIR/templates"
else
    mkdir -p "$OUTPUT_DIR/templates"
    warn "templates/ not in source — you will need to supply air.blk manually"
fi

if [ -f "wt_ext_cli" ]; then
    cp wt_ext_cli "$OUTPUT_DIR/wt_ext_cli"
    chmod +x "$OUTPUT_DIR/wt_ext_cli"
else
    warn "wt_ext_cli not in source — plane extraction will not work"
fi

cat > "$OUTPUT_DIR/README.txt" <<'EOF'
WT3 Air Builder — portable release
==================================

Run:
    ./wt3-air-builder

Requirements on the target machine:
    - War Thunder installed via Steam
    - War Thunder CDK (for aces.vromfs.bin)
    - Python is NOT required — it's bundled in the binary

Layout:
    wt3-air-builder    the app (single-file executable)
    database/          vehicle data and icons (do not delete)
    templates/         mission templates (do not delete)
    wt_ext_cli         vromfs extraction tool (do not delete)

Keep this folder together. If you move the binary elsewhere,
copy database/, templates/ and wt_ext_cli alongside it.
EOF

deactivate 2>/dev/null || true

# ---------- Report ----------

say "Build complete"
echo
echo "    Release folder: $OUTPUT_DIR"
echo "    Binary size:    $(du -h "$OUTPUT_DIR/$BIN_NAME" | cut -f1)"
echo "    Total size:     $(du -sh "$OUTPUT_DIR" | cut -f1)"
echo
echo "Test it with:"
echo "    $OUTPUT_DIR/$BIN_NAME"
<<<<<<< HEAD
echo
=======
echo
>>>>>>> b555796 (Bootstrap build script with venv cleanup)
