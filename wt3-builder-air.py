#!/usr/bin/env python3
"""wt3-builder-air v2 — War Thunder Air Test Drive Generator.

Mod-1: weightless loadouts + full loadout maker UI.
v2.9: weightless now also injects mass/dragCx into carried Weapon blocks,
      matching how Ask3lad's own planes achieve zero carried weight.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

BUILDER_DIR = Path.home() / "wt-builder"
DB_DIR = BUILDER_DIR / "database"
ICONS_DIR = DB_DIR / "icons"
TEMPLATE_DIR = BUILDER_DIR / "templates"
TEMPLATE = TEMPLATE_DIR / "air.blk"
EXTRACTED = BUILDER_DIR / "extracted" / "flightmodels"

WT_DIR = Path.home() / ".local/share/Steam/steamapps/common/War Thunder"
ACES = WT_DIR / "aces.vromfs.bin"
MISSIONS = WT_DIR / "UserMissions" / "Ask3lad"
PKG = WT_DIR / "content" / "pkg_local" / "gameData"
FLIGHT_MODELS = PKG / "flightModels"
LIGHT_DIR = PKG / "Weapons" / "ask3lad"
PLAYER_STUB = FLIGHT_MODELS / "ask3lad_air_player.blk"
BASE_MISSION = MISSIONS / "ask3lad_testdrive_air.blk"
WT_EXT_CLI = BUILDER_DIR / "wt_ext_cli"

PRESET_NAME = "ask3lad_air_custom.blk"
WEAPON_PRESETS_VARIANTS = [
    PKG / "flightModels" / "weaponPresets",
    PKG / "flightmodels" / "weaponpresets",
    PKG / "FlightModels" / "weaponPresets",
    PKG / "FlightModels" / "WeaponPresets",
]


QSS = """
QWidget { background-color: transparent; color: #e0e0e0;
    font-family: "Segoe UI", "Noto Sans", sans-serif; font-size: 13px; }
QMainWindow { background: #0a0d1a; }
QWidget#mainCanvas {
    background: qlineargradient(x1:0, y1:0, x2:0.3, y2:1,
        stop:0 #1a1e3a, stop:0.45 #12162e, stop:1 #0a0d1a); }
QDialog { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    stop:0 #161a2e, stop:1 #0c0f1e); }
QTabWidget::pane { border: 1px solid #2a2e4a; border-radius: 6px;
    background: rgba(20, 24, 42, 0.85); top: -1px; }
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #202444, stop:1 #1a1e34);
    color: #a0a8c0; padding: 10px 22px; margin-right: 2px;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
    border: 1px solid #2a2e4a; border-bottom: none; font-weight: 500; }
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a5cdb, stop:1 #2a3a9e);
    color: #ffffff; border-color: #6a7aee; }
QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #353a5c, stop:1 #242844);
    color: #d0d5e8; }
QGroupBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(28, 32, 58, 0.9), stop:1 rgba(20, 24, 44, 0.9));
    border: 1px solid #2a2e4a; border-radius: 6px;
    margin-top: 12px; padding: 14px 8px 8px 8px;
    font-weight: 600; color: #c0c5d8; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left;
    padding: 2px 10px; color: #8c9cee; background: transparent; }
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b4cca, stop:1 #2a3a9e);
    color: #fff; border: 1px solid #4a5cdb; border-radius: 6px;
    padding: 8px 18px; font-weight: 600; min-height: 20px; }
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a6ceb, stop:1 #3b4cca);
    border-color: #8a9aee; }
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1f2a7a, stop:1 #151c5c); }
QPushButton:disabled { background: #2a2e3a; color: #606878; border-color: #3a3e4a; }
QPushButton#vehiclePicker {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2a3a6e, stop:0.5 #3a4a9e, stop:1 #2a3a6e);
    border: 1px dashed #6a7aee; text-align: left; padding: 14px 18px;
    font-weight: 500; font-size: 14px; min-height: 24px; }
QPushButton#vehiclePicker:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a4a8e, stop:0.5 #5a6cdb, stop:1 #3a4a8e);
    border-style: solid; border-color: #a0b0ff; }
QPushButton#targetPicker {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(28, 32, 58, 0.9), stop:1 rgba(18, 22, 40, 0.9));
    border: 1px solid #2a2e4a; text-align: left;
    padding: 8px 12px; font-weight: 400; font-size: 13px; min-height: 22px; }
QPushButton#targetPicker:hover { border-color: #6a7aee;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(38, 42, 76, 0.95), stop:1 rgba(26, 30, 56, 0.95)); }
QPushButton#targetPicker[filled="true"] { border-color: #4a8a4a; color: #e0ffe0; }
QPushButton#targetPicker[filled="false"] { color: #707890; font-style: italic; }
QPushButton#clearBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a2a2a, stop:1 #2a1e1e);
    border: 1px solid #5a3a3a; color: #d09090;
    padding: 6px; font-weight: 700; min-width: 26px; font-size: 14px; }
QPushButton#clearBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6a2a2a, stop:1 #4a1e1e);
    border-color: #d05a5a; color: #ffd0d0; }
QPushButton#generateBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #d09000, stop:0.5 #f5c518, stop:1 #d09000);
    color: #1a1a2e; border: 2px solid #ffd700; border-radius: 8px;
    font-size: 18px; font-weight: 800; padding: 16px; min-height: 30px;
    letter-spacing: 1px; }
QPushButton#generateBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f0b000, stop:0.5 #ffdd33, stop:1 #f0b000);
    border-color: #ffffff; }
QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #22263e, stop:1 #1a1e30);
    border: 1px solid #2a2e4a; border-radius: 5px;
    padding: 6px 10px; color: #e0e0e0; min-height: 18px; }
QComboBox:hover { border-color: #6a7aee; background: #262a4a; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #1e2238; border: 1px solid #4a5cdb; color: #e0e0e0;
    selection-background-color: #3b4cca; selection-color: #fff; outline: none; }
QLineEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1e30, stop:1 #15182a);
    border: 1px solid #2a2e4a; border-radius: 5px;
    padding: 7px 10px; color: #e0e0e0; }
QLineEdit:focus { border-color: #8a9aee; background: #202440; }
QSpinBox, QDoubleSpinBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a1e30, stop:1 #15182a);
    border: 1px solid #2a2e4a; border-radius: 5px;
    padding: 5px 8px; color: #e0e0e0; }
QCheckBox { spacing: 8px; color: #c0c5d8; }
QCheckBox::indicator {
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid #3a3e5a; background: #1e2238; }
QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a5cdb, stop:1 #7a8cff);
    border-color: #8a9aee; }
QListWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161a2a, stop:1 #101220);
    border: 1px solid #2a2e4a; border-radius: 6px;
    color: #e0e0e0; outline: none; }
QListWidget::item { padding: 8px 10px; border-bottom: 1px solid #1e2238; }
QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b4cca, stop:1 #2a3a9e);
    color: #fff; }
QListWidget::item:hover:!selected { background: #222642; }
QPlainTextEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #060812, stop:1 #0c0e1c);
    border: 1px solid #2a2e4a; border-radius: 6px;
    color: #a0d0a0; font-family: "JetBrains Mono", monospace;
    font-size: 12px; padding: 6px; }
QScrollBar:vertical { background: #161a2a; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a3e5a, stop:1 #4a4e6a);
    border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #6a7aee; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #161a2a; height: 10px; border-radius: 5px; }
QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3e5a, stop:1 #4a4e6a);
    border-radius: 5px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #6a7aee; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QLabel { color: #c0c5d8; background: transparent; }
QLabel#header { font-size: 24px; font-weight: 800; color: #9aacee;
    padding: 8px 0; letter-spacing: 1px; }
QLabel#subheader { font-size: 11px; color: #707890; padding-bottom: 4px; }
QLabel#detailBox {
    background: rgba(18, 20, 40, 0.95); border: 1px solid #2a2e4a; border-radius: 6px;
    padding: 10px; color: #a0a5c0;
    font-family: "JetBrains Mono", monospace; font-size: 12px; }

QFrame#slotCard {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1c2038, stop:1 #14182c);
    border: 2px solid #2a2e4a; border-radius: 6px;
}
QFrame#slotCard[state="filled"] { border-color: #4a5cdb; }
QFrame#slotCard[state="empty"]  { border-color: #232744; }

QPushButton#slotClear {
    background: #3a2a2a; color: #d09090;
    border: 1px solid #5a3a3a; border-radius: 3px;
    font-size: 11px; font-weight: 700;
    padding: 0; min-width: 0; min-height: 0;
}
QPushButton#slotClear:hover { background: #6a2a2a; color: #ffd0d0; }

QFrame[frameShape="4"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 transparent, stop:0.5 #4a5cdb, stop:1 transparent);
    max-height: 1px; border: none; }
"""


def load_vehicles(kind):
    path = DB_DIR / f"{kind}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "vehicles" in data:
        return data["vehicles"]
    if isinstance(data, list):
        return data
    return []


def all_vehicles():
    out = {}
    for k in ("air", "heli", "ground", "naval"):
        v = load_vehicles(k)
        if v:
            out[k] = v
    return out


def find_vehicle(vehicles, vehicle_id):
    for vs in vehicles.values():
        for v in vs:
            if v.get("id") == vehicle_id:
                return v
    return None


def collect_nations(vehicles):
    s = set()
    for vs in vehicles.values():
        for v in vs:
            n = v.get("nation")
            if n: s.add(n)
    return sorted(s)


def collect_ranks(vehicles):
    s = set()
    for vs in vehicles.values():
        for v in vs:
            r = v.get("rank")
            if isinstance(r, int): s.add(r)
    return sorted(s)


def get_plane_pylons(vehicles, plane_id):
    v = find_vehicle(vehicles, plane_id)
    if not v: return []
    if v.get("loadoutKind") != "slots":
        return []
    return v.get("pylons") or []


def get_plane_presets(vehicles, plane_id):
    v = find_vehicle(vehicles, plane_id)
    if not v: return []
    if v.get("loadoutKind") != "presets":
        return []
    return v.get("presets") or []


def build_global_weapon_index(vehicles):
    idx = {}
    for v in vehicles.get("air", []) + vehicles.get("heli", []):
        plane_id = v.get("id", "?")
        plane_name = v.get("name", "?")
        for pylon in (v.get("pylons") or []):
            for opt in (pylon.get("options") or []):
                oid = opt.get("id")
                if not oid or oid in idx: continue
                entry = dict(opt)
                entry["_source_plane_id"] = plane_id
                entry["_source_plane_name"] = plane_name
                blks = [w.get("blk") for w in (opt.get("weapons") or [])
                        if w.get("blk")]
                entry["_source_blk"] = blks[0] if blks else None
                idx[oid] = entry
    return idx


def extract_plane(plane_id):
    EXTRACTED.mkdir(parents=True, exist_ok=True)
    target = EXTRACTED / f"{plane_id}.blk"
    if target.exists() and target.stat().st_size > 100:
        return target

    cli = WT_EXT_CLI if WT_EXT_CLI.exists() else Path("wt_ext_cli")
    if not cli.exists():
        raise FileNotFoundError(f"wt_ext_cli not found at {cli}")

    tmp = EXTRACTED / "_tmp"
    tmp.mkdir(exist_ok=True)

    for prefix in ("gameData", "gamedata"):
        try:
            subprocess.run([
                str(cli), "unpack_vromf",
                "-i", str(ACES),
                "-o", str(tmp),
                "--format", "BlkText",
                "--folder", f"{prefix}/flightmodels/{plane_id}.blk",
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            continue
        matches = list(tmp.rglob(f"{plane_id}.blk"))
        if matches:
            matches[0].replace(target)
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)
            return target

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return None


def find_matching_brace(text, open_brace_idx):
    depth = 0
    for i in range(open_brace_idx, len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return -1


def find_weaponslot_range(text, slot_idx):
    for m in re.finditer(r'\bWeaponSlot\s*\{', text):
        open_idx = text.index('{', m.start())
        close_idx = find_matching_brace(text, open_idx)
        if close_idx < 0: continue
        block = text[m.start():close_idx + 1]
        idx_m = re.search(r'\bindex:i\s*=\s*(\d+)', block)
        if idx_m and int(idx_m.group(1)) == slot_idx:
            return m.start(), close_idx + 1
    return None


def replace_weapon_in_preset(target_text, slot_idx, preset_name, source_blk):
    slot_range = find_weaponslot_range(target_text, slot_idx)
    if not slot_range:
        return target_text, 0
    s_start, s_end = slot_range
    slot_text = target_text[s_start:s_end]

    preset_start = preset_end = None
    pos = 0
    while True:
        m = re.search(r'\bWeaponPreset\s*\{', slot_text[pos:])
        if not m: break
        abs_open = pos + m.start()
        brace_open = slot_text.index('{', abs_open)
        brace_close = find_matching_brace(slot_text, brace_open)
        if brace_close < 0: break
        block = slot_text[abs_open:brace_close + 1]
        nm = re.search(r'\bname:t\s*=\s*"([^"]+)"', block)
        if nm and nm.group(1) == preset_name:
            preset_start = abs_open
            preset_end = brace_close + 1
            break
        pos = brace_close + 1

    if preset_start is None:
        return target_text, 0

    preset_text = slot_text[preset_start:preset_end]
    new_preset, n = re.subn(
        r'(blk:t\s*=\s*")gameData/Weapons/[^"]+(")',
        rf'\g<1>{source_blk}\g<2>',
        preset_text
    )

    lines = new_preset.split('\n')
    out_lines = []
    for line in lines:
        out_lines.append(line)
        if re.match(r'^\s*separate:b\s*=\s*true\s*$', line):
            indent = re.match(r'^(\s*)', line).group(1)
            out_lines.append(f'{indent}launcher:b = true')
    new_preset = '\n'.join(out_lines)

    new_slot = slot_text[:preset_start] + new_preset + slot_text[preset_end:]
    return target_text[:s_start] + new_slot + target_text[s_end:], n


def parse_plane_weaponslots(text):
    m = re.search(r'\nWeaponSlots\s*\{', text)
    if not m:
        return []
    open_idx = text.index('{', m.start())
    close_idx = find_matching_brace(text, open_idx)
    if close_idx < 0:
        return []
    block = text[open_idx:close_idx + 1]
    blks = re.findall(r'blk:t\s*=\s*"(gameData/Weapons/[^"]+)"',
                      block, re.IGNORECASE)
    seen = set(); out = []
    for b in blks:
        if b not in seen:
            seen.add(b); out.append(b)
    return out


def add_mass_drag_to_weapon(block):
    """Insert or force `mass:r = 0.01` and `dragCx:r = 0.01` in a Weapon{}
    block. Returns (new_block, changed)."""
    lines = block.split('\n')
    if not lines:
        return block, False

    # Find the closing brace line (last line whose stripped form is "}")
    close_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '}':
            close_idx = i
            break
    if close_idx < 0:
        return block, False

    close_indent = re.match(r'^(\s*)', lines[close_idx]).group(1)
    inner_indent = close_indent + '\t'
    # Try to infer from the first field line
    for i in range(1, close_idx):
        m = re.match(r'^(\s*)\S', lines[i])
        if m:
            inner_indent = m.group(1)
            break

    has_mass = has_drag = False
    changed = False
    for i in range(1, close_idx):
        line = lines[i]
        m = re.match(r'^(\s*)mass:r\s*=\s*([\d.]+)', line)
        if m:
            has_mass = True
            new_line = f'{m.group(1)}mass:r = 0.01'
            if new_line != line:
                lines[i] = new_line; changed = True
        m = re.match(r'^(\s*)dragCx:r\s*=\s*([\d.]+)', line)
        if m:
            has_drag = True
            new_line = f'{m.group(1)}dragCx:r = 0.01'
            if new_line != line:
                lines[i] = new_line; changed = True

    inserts = []
    if not has_mass:
        inserts.append(f'{inner_indent}mass:r = 0.01')
    if not has_drag:
        inserts.append(f'{inner_indent}dragCx:r = 0.01')
    if inserts:
        lines = lines[:close_idx] + inserts + lines[close_idx:]
        changed = True

    return '\n'.join(lines), changed


def apply_weightless_to_weapon_blocks(text):
    """For every carried Weapon{} in WeaponSlots, force mass and dragCx to
    near zero. Skips dummy weapons and countermeasures. Returns (new_text, n)."""
    m = re.search(r'\nWeaponSlots\s*\{', text)
    if not m:
        return text, 0
    open_idx = text.index('{', m.start())
    close_idx = find_matching_brace(text, open_idx)
    if close_idx < 0:
        return text, 0
    ws_start = m.start()
    ws_end = close_idx + 1

    ws_block = text[ws_start:ws_end]

    parts = []
    last_end = 0
    count = 0

    # We deliberately match `Weapon {` not `WeaponPreset {` nor `WeaponSlot {`
    for wm in re.finditer(r'(?<![A-Za-z_])Weapon\s*\{', ws_block):
        brace_open = ws_block.index('{', wm.start())
        brace_close = find_matching_brace(ws_block, brace_open)
        if brace_close < 0:
            continue
        block = ws_block[brace_open:brace_close + 1]

        if 'external:b = true' not in block:
            continue
        if 'ask3lad_cm_' in block:
            continue
        if 'dummy_weapon' in block:
            continue

        new_block, changed = add_mass_drag_to_weapon(block)
        if changed:
            parts.append(ws_block[last_end:brace_open])
            parts.append(new_block)
            last_end = brace_close + 1
            count += 1

    if not parts:
        return text, 0
    parts.append(ws_block[last_end:])
    new_ws = "".join(parts)
    return text[:ws_start] + new_ws + text[ws_end:], count


def write_light_wrapper(wrapper_index, source_blk):
    """Weightless wrapper: zero in-flight drag AND zero the missile's own
    bullet mass, so the missile contributes no weight to the plane."""
    LIGHT_DIR.mkdir(parents=True, exist_ok=True)
    path = LIGHT_DIR / f"ask3lad_light_{wrapper_index}.blk"
    content = (
        f"// WT3 Air Builder: weightless wrapper for {source_blk}\n"
        f'include "#/develop/gameBase/{source_blk}"\n'
        f'"@override:rocket" {{ "@override:dragCx":r = 0 }}\n'
        f'"@override:bullet" {{ "@override:mass":r = 0.001 }}\n'
    )
    path.write_text(content, encoding="utf-8")
    return path


def write_player_stub(plane_id, plane_text, slot_options, global_weapons_idx,
                      plane_pylons, weightless=True):
    text = plane_text

    custom_entry = (
        '\tpreset {\n'
        '\t\tname:t = "ask3lad_custom"\n'
        '\t\tblk:t = "gameData/FlightModels/weaponPresets/ask3lad_air_custom.blk"\n'
        '\t}\n'
    )
    if 'ask3lad_custom' not in text:
        m = re.search(r'(weapon_presets\s*\{)', text)
        if m:
            insert_at = m.end()
            text = text[:insert_at] + '\n' + custom_entry + text[insert_at:]

    native_by_slot = {}
    for p in plane_pylons:
        idx = p.get("index")
        native_by_slot[idx] = [o.get("id") for o in (p.get("options") or [])]

    override_report = []
    native_preset_for_custom = {}

    for slot_idx, chosen_id in sorted(slot_options.items(), key=lambda x: int(x[0])):
        slot_idx = int(slot_idx)
        natives = native_by_slot.get(slot_idx, [])

        if chosen_id in natives:
            native_preset_for_custom[slot_idx] = chosen_id
            override_report.append((slot_idx, chosen_id, "native", ""))
            continue

        gw = global_weapons_idx.get(chosen_id)
        if not gw:
            override_report.append((slot_idx, chosen_id, "fail", "no global entry"))
            continue
        source_blk = gw.get("_source_blk")
        if not source_blk:
            override_report.append((slot_idx, chosen_id, "fail", "no source blk"))
            continue

        if not natives:
            override_report.append((slot_idx, chosen_id, "fail", "slot has no native preset"))
            continue
        native_name = natives[0]

        text, n = replace_weapon_in_preset(text, slot_idx, native_name, source_blk)
        if n == 0:
            override_report.append((slot_idx, chosen_id, "fail",
                                    f"preset '{native_name}' not found"))
            continue

        native_preset_for_custom[slot_idx] = native_name
        override_report.append((slot_idx, chosen_id, "inject",
                                f"into '{native_name}' ({n} blk swaps)"))

    # Inject mass/dragCx=0.01 into every carried Weapon block
    if weightless:
        text, n_wl = apply_weightless_to_weapon_blocks(text)
        override_report.append((0, f"{n_wl} carried Weapon blocks", "weightless", ""))

    wrapper_map = {}
    if weightless:
        blks = parse_plane_weaponslots(text)
        for i, b in enumerate(blks):
            wrapper_path = f"gameData/Weapons/ask3lad/ask3lad_light_{i}.blk"
            wrapper_map[b] = i
            text = text.replace(f'blk:t = "{b}"', f'blk:t = "{wrapper_path}"')

    header = (
        f'// WT3 Air Builder player: {plane_id}\n'
        f'// Auto-generated. Delete this file to restore normal behaviour.\n'
        f'// weightless: {weightless}\n'
    )
    text = header + text

    FLIGHT_MODELS.mkdir(parents=True, exist_ok=True)
    PLAYER_STUB.write_text(text, encoding="utf-8")

    if weightless:
        for src_blk, idx in wrapper_map.items():
            write_light_wrapper(idx, src_blk)

    return PLAYER_STUB, wrapper_map, override_report, native_preset_for_custom


def write_custom_preset(slot_options_by_preset_name):
    lines = ["// WT3 Air Builder custom preset", ""]
    for slot in sorted(slot_options_by_preset_name.keys(), key=lambda x: int(x)):
        opt = slot_options_by_preset_name[slot]
        lines.append("Weapon {")
        lines.append(f"\tslot:i = {int(slot)}")
        lines.append(f'\tpreset:t = "{opt}"')
        lines.append("}")
    content = "\n".join(lines) + "\n"

    written = []
    for d in WEAPON_PRESETS_VARIANTS:
        try:
            d.mkdir(parents=True, exist_ok=True)
            path = d / PRESET_NAME
            path.write_text(content, encoding="utf-8")
            written.append(str(path))
        except Exception as e:
            print(f"[wt3-air] preset write warning: {d}: {e}")
    return written


def swap_unit_class(text, unit_name, new_class):
    pattern = (rf'name:t="{re.escape(unit_name)}"'
               rf'((?:(?!name:t=)[\s\S])*?)unit_class:t="[^"]*"')
    return re.subn(pattern,
                   rf'name:t="{unit_name}"\1unit_class:t="{new_class}"',
                   text, count=1)


def swap_unit_preset(text, unit_name, new_preset):
    pattern = (rf'(name:t="{re.escape(unit_name)}"'
               rf'(?:(?!name:t=)[\s\S])*?weapons:t=")[^"]*(")')
    return re.subn(pattern, rf'\g<1>{new_preset}\g<2>', text, count=1)


def ensure_player_mods(text, aced, modules):
    if not aced and not modules:
        return text, 0
    pattern = r'(name:t="You"(?:(?!name:t=)[\s\S])*?)([ \t]*\n[ \t]*props[ \t]*\{)'
    m = re.search(pattern, text)
    if not m: return text, 0
    head, tail = m.group(1), m.group(2)
    head = re.sub(r'\n[ \t]*crewSkillK:r=[\d.]+', '', head)
    head = re.sub(r'\n[ \t]*applyAllMods:b=\w+', '', head)
    add = []
    if aced:    add.append('    crewSkillK:r=1')
    if modules: add.append('    applyAllMods:b=yes')
    new_head = head.rstrip() + '\n' + '\n'.join(add)
    return text[:m.start()] + new_head + tail + text[m.end():], len(add)


def patch_air_mission(player_plane, player_preset, targets, vehicles,
                      aced=False, modules=False, fuel=30, thrust_mult=1.0):
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Air template missing at {TEMPLATE}")
    text = TEMPLATE.read_text(encoding="utf-8")
    report = []

    text, nc = swap_unit_class(text, "You", "ask3lad_air_player")
    text, np = swap_unit_preset(text, "You", player_preset)
    report.append(f"player -> ask3lad_air_player (real: {player_plane}) "
                  f": class {nc} preset {np} ({player_preset})")

    text, n = ensure_player_mods(text, aced, modules)
    if n:
        bits = []
        if aced: bits.append("aced")
        if modules: bits.append("modules")
        report.append(f"player mods ({'+'.join(bits)}) : {n}")

    pat = r'(name:t="You"(?:(?!name:t=)[\s\S])*?fuel:r=)[\d.]+'
    text, n = re.subn(pat, rf'\g<1>{fuel}', text, count=1)
    if n: report.append(f"fuel -> {fuel}%")

    pat = r'(thrust_mult:r=)[\d.]+'
    text, n = re.subn(pat, rf'\g<1>{thrust_mult}', text, count=1)
    if n: report.append(f"thrust_mult -> {thrust_mult}")

    target_map = {
        "air": "Target_Air_01", "heli": "Target_Heli_01",
        "ship1": "Target_Ship_01", "ship2": "Target_Ship_02",
        "ship3": "Target_Ship_03",
        "ground1": "Target_Ground_01", "ground2": "Target_Ground_02",
        "ground3": "Target_Ground_03", "spaa": "Target_Ground_SPAA",
        "mover": "Target_Ground_Mover",
    }
    for key, unit_name in target_map.items():
        tid = targets.get(key)
        if tid:
            text, n = swap_unit_class(text, unit_name, tid)
            report.append(f"{key} -> {tid} : class {n}")

    BASE_MISSION.parent.mkdir(parents=True, exist_ok=True)
    BASE_MISSION.write_text(text, encoding="utf-8")
    return report


_ICON_CACHE = {}

def load_icon_pixmap(icon_name, size=48):
    if not icon_name:
        return None
    key = (icon_name, size)
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]

    from PySide6.QtGui import QPixmap
    from PySide6.QtCore import Qt

    candidates = [
        ICONS_DIR / f"{icon_name}.png",
        ICONS_DIR / f"{icon_name.lower()}.png",
        ICONS_DIR / f"{icon_name.replace('/', '_')}.png",
        ICONS_DIR / f"{icon_name.lower().replace('/', '_')}.png",
    ]
    pm = None
    for c in candidates:
        if c.exists():
            pm = QPixmap(str(c))
            if not pm.isNull():
                pm = pm.scaled(size, size, Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
                break
            pm = None

    _ICON_CACHE[key] = pm
    return pm


def make_vehicle_picker(vehicles, nations, ranks, title, kinds_filter=None):
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
        QListWidget, QListWidgetItem, QDialogButtonBox,
    )
    from PySide6.QtCore import Qt

    class VehiclePickerDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title)
            self.resize(880, 680)
            self._selected = None
            root = QVBoxLayout(self)
            self.search = QLineEdit()
            self.search.setPlaceholderText("Search by name or ID…")
            root.addWidget(self.search)
            fr = QHBoxLayout()
            fr.addWidget(QLabel("Kind:"))
            self.kind = QComboBox()
            allowed = kinds_filter or list(vehicles.keys())
            self.kind.addItems([k for k in allowed if k in vehicles])
            fr.addWidget(self.kind)
            fr.addWidget(QLabel("Nation:"))
            self.nation = QComboBox(); self.nation.addItem("All", "")
            for n in nations: self.nation.addItem(n.upper(), n)
            fr.addWidget(self.nation)
            fr.addWidget(QLabel("Rank:"))
            self.rank = QComboBox(); self.rank.addItem("All", 0)
            for r in ranks: self.rank.addItem(f"R{r}", r)
            fr.addWidget(self.rank)
            fr.addStretch()
            root.addLayout(fr)
            self.list = QListWidget(); root.addWidget(self.list, 1)
            self.count_label = QLabel("")
            self.count_label.setObjectName("subheader")
            root.addWidget(self.count_label)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
            root.addWidget(buttons)
            self.search.textChanged.connect(self.refresh)
            self.kind.currentTextChanged.connect(self.refresh)
            self.nation.currentTextChanged.connect(self.refresh)
            self.rank.currentTextChanged.connect(self.refresh)
            self.list.itemDoubleClicked.connect(lambda _: self.accept())
            self.refresh()
            self.search.setFocus()

        def refresh(self):
            self.list.clear()
            kind = self.kind.currentText()
            nation = self.nation.currentData()
            rank = self.rank.currentData()
            q = self.search.text().lower()
            count = 0
            for v in vehicles.get(kind, []):
                name = v.get("name", "?"); vid = v.get("id", "?")
                if nation and v.get("nation") != nation: continue
                if rank and v.get("rank") != rank: continue
                if q and q not in name.lower() and q not in vid.lower(): continue
                br = v.get("br", {}) or {}
                rb = br.get("rb") if isinstance(br, dict) else None
                br_s = f" · BR {rb}" if rb else ""
                rank_s = f" · R{v.get('rank','?')}"
                item = QListWidgetItem(f"{name}{rank_s}{br_s}   [{vid}]")
                item.setData(Qt.UserRole, vid)
                item.setData(Qt.UserRole + 1, name)
                self.list.addItem(item); count += 1
            self.count_label.setText(f"{count} vehicles")

        def accept(self):
            item = self.list.currentItem()
            if not item: return
            self._selected = (item.data(Qt.UserRole), item.data(Qt.UserRole + 1))
            super().accept()

        def selected(self): return self._selected

    return VehiclePickerDialog()


def make_weapon_picker(plane_pylons, slot_index, current_option_id, title,
                       all_options=None, show_override=False):
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
        QListWidget, QListWidgetItem, QDialogButtonBox, QCheckBox,
    )
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QIcon

    def classify_icon(opt):
        ic = (opt.get("icon") or "").lower()
        if "missile_type_b_air_to_air" in ic or "aam" in ic: return "AAM"
        if "missile_air_to_air_midrange" in ic: return "AAM (M)"
        if "missile_air_to_uni" in ic: return "AGM"
        if "missile_air_to_earth" in ic: return "ASM"
        if "bombs_" in ic: return "BOMB"
        if "nar_ap" in ic or "rocket" in ic: return "RKT"
        if "ptb" in ic or "drop_tank" in ic or "fuel" in ic: return "FT"
        if "torpedo" in ic: return "TORP"
        if "gun" in ic or "cannon" in ic: return "GUN"
        return "?"

    def short_label(opt):
        n = opt.get("name", "?")
        if len(n) > 32: n = n[:30] + "…"
        return n

    class WeaponPickerDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title)
            self.resize(960, 680)
            self._selected = None

            root = QVBoxLayout(self)
            self.search = QLineEdit()
            self.search.setPlaceholderText("Search by name or ID…")
            root.addWidget(self.search)

            self.show_all = QCheckBox("Show ALL weapons (from every plane)")
            self.show_all.setToolTip(
                "Off: only weapons this pylon normally accepts.\n"
                "On: every weapon in the entire game, ignoring plane restrictions,\n"
                "modifications, and bans. Foreign weapons are swapped into the\n"
                "slot's native preset blk at generation time.")
            self.show_all.setChecked(show_override)

            fr = QHBoxLayout()
            fr.addWidget(QLabel("Type:"))
            self.atype = QComboBox(); self.atype.addItem("All", "")
            types = sorted({
                classify_icon(o) for o in self._pool()
                if classify_icon(o) != "?"
            })
            for t in types: self.atype.addItem(t, t)
            fr.addWidget(self.atype)
            fr.addWidget(self.show_all)
            fr.addStretch()
            root.addLayout(fr)

            body = QHBoxLayout()
            self.list = QListWidget()
            self.list.setIconSize(QSize(32, 32))
            body.addWidget(self.list, 3)
            self.detail = QLabel("Hover a weapon to see its specs.")
            self.detail.setObjectName("detailBox")
            self.detail.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.detail.setMinimumWidth(280)
            self.detail.setWordWrap(True)
            body.addWidget(self.detail, 1)
            root.addLayout(body, 1)

            self.count_label = QLabel("")
            self.count_label.setObjectName("subheader")
            root.addWidget(self.count_label)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
            root.addWidget(buttons)

            self.search.textChanged.connect(self.refresh)
            self.atype.currentTextChanged.connect(self.refresh)
            self.show_all.toggled.connect(self.refresh)
            self.list.itemDoubleClicked.connect(lambda _: self.accept())
            self.list.currentItemChanged.connect(self.on_hover)
            self.list.itemEntered.connect(self.on_hover)

            self.refresh()
            self.search.setFocus()
            if current_option_id:
                self.select_by_id(current_option_id)

        def _pool(self):
            if getattr(self, "show_all", None) and self.show_all.isChecked() and all_options:
                return list(all_options)
            for p in plane_pylons:
                if p.get("index") == slot_index:
                    return p.get("options") or []
            return []

        def refresh(self):
            self.list.clear()
            q = self.search.text().lower()
            atype = self.atype.currentData()
            count = 0
            for opt in self._pool():
                oid = opt.get("id", "?")
                if atype and classify_icon(opt) != atype: continue
                if q and q not in oid.lower() and q not in (opt.get("name","")).lower():
                    continue
                src = opt.get("_source_plane_name")
                suffix = f"  ·  {src}" if (src and self.show_all.isChecked()) else ""
                label = f"[{classify_icon(opt)}]  {short_label(opt)}   [{oid}]{suffix}"
                item = QListWidgetItem(label)
                item.setData(Qt.UserRole, oid)
                item.setData(Qt.UserRole + 1, opt)
                pm = load_icon_pixmap(opt.get("icon"), size=32)
                if pm:
                    item.setIcon(QIcon(pm))
                self.list.addItem(item)
                count += 1
            self.count_label.setText(
                f"{count} weapons  ·  "
                f"{'ALL planes' if self.show_all.isChecked() else 'compatible with slot'}")

        def on_hover(self, item, *_):
            if not item:
                self.detail.setText("Hover a weapon to see its specs.")
                return
            opt = item.data(Qt.UserRole + 1) or {}
            mass = opt.get("mass", "—")
            req = opt.get("requires") or "—"
            bans = opt.get("bans") or []
            bans_s = ", ".join(f"slot {b[0]}→{b[1]}" for b in bans[:4]) or "—"
            src = opt.get("_source_plane_name") or "—"
            blk = opt.get("_source_blk") or "—"
            self.detail.setText(
                f"<b>{opt.get('name', opt.get('id','?'))}</b><br><br>"
                f"<b>ID</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {opt.get('id','?')}<br>"
                f"<b>Source</b> &nbsp;&nbsp; {src}<br>"
                f"<b>Type</b> &nbsp;&nbsp;&nbsp; {classify_icon(opt)}<br>"
                f"<b>Mass</b> &nbsp;&nbsp;&nbsp; {mass} kg<br>"
                f"<b>Requires</b> {req}<br>"
                f"<b>Bans</b> &nbsp;&nbsp;&nbsp; {bans_s}<br><br>"
                f"<span style='color:#606078'>blk: {blk}</span>"
            )

        def select_by_id(self, oid):
            for i in range(self.list.count()):
                it = self.list.item(i)
                if it.data(Qt.UserRole) == oid:
                    self.list.setCurrentItem(it)
                    self.list.scrollToItem(it)
                    return

        def accept(self):
            item = self.list.currentItem()
            if not item: return
            self._selected = (item.data(Qt.UserRole),
                              item.data(Qt.UserRole + 1))
            super().accept()

        def selected(self): return self._selected

    return WeaponPickerDialog()


def launch_gui():
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QLabel, QPushButton, QPlainTextEdit, QCheckBox, QSpinBox,
            QDoubleSpinBox, QComboBox, QTabWidget, QGroupBox, QFormLayout,
            QFrame, QSizePolicy, QMessageBox, QScrollArea,
        )
        from PySide6.QtCore import Qt, Signal, QRect
        from PySide6.QtGui import QPainter, QColor, QPixmap
    except ImportError:
        print("PySide6 not installed.")
        sys.exit(1)

    class SlotCard(QFrame):
        clicked = Signal()
        cleared = Signal()

        def __init__(self, slot_idx, parent=None):
            super().__init__(parent)
            self.slot_idx = slot_idx
            self.setObjectName("slotCard")
            self.setFixedSize(118, 138)
            self.setCursor(Qt.PointingHandCursor)
            self.setProperty("state", "empty")
            self._weapon_name = None
            self._icon_pixmap = None

            self.clear_btn = QPushButton("✕", self)
            self.clear_btn.setObjectName("slotClear")
            self.clear_btn.setFixedSize(18, 18)
            self.clear_btn.move(118 - 22, 4)
            self.clear_btn.setVisible(False)
            self.clear_btn.clicked.connect(lambda _=False: self.cleared.emit())

        def set_weapon(self, name, icon_name=None):
            self._weapon_name = name
            if name:
                self._icon_pixmap = load_icon_pixmap(icon_name, size=44) if icon_name else None
                self.setProperty("state", "filled")
                self.clear_btn.setVisible(True)
            else:
                self._icon_pixmap = None
                self.setProperty("state", "empty")
                self.clear_btn.setVisible(False)
            self.style().unpolish(self); self.style().polish(self)
            self.update()

        def mousePressEvent(self, ev):
            if ev.button() == Qt.LeftButton:
                self.clicked.emit()
            super().mousePressEvent(ev)

        def paintEvent(self, ev):
            super().paintEvent(ev)
            p = QPainter(self)

            f = p.font()
            f.setPixelSize(11)
            f.setBold(True)
            f.setItalic(False)
            p.setFont(f)
            p.setPen(QColor("#8c9cee"))
            p.drawText(QRect(8, 6, 40, 16),
                       Qt.AlignLeft | Qt.AlignVCenter,
                       f"{self.slot_idx:02d}")

            if self._weapon_name:
                if self._icon_pixmap and not self._icon_pixmap.isNull():
                    iw = self._icon_pixmap.width()
                    ih = self._icon_pixmap.height()
                    ix = (self.width() - iw) // 2
                    iy = 26
                    p.drawPixmap(ix, iy, self._icon_pixmap)
                    name_y = iy + ih + 4
                    name_h = self.height() - name_y - 6
                else:
                    name_y = 26
                    name_h = self.height() - name_y - 6

                f.setPixelSize(11)
                f.setBold(False)
                p.setFont(f)
                p.setPen(QColor("#e0e6ff"))
                p.drawText(QRect(6, name_y, self.width() - 12, name_h),
                           Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
                           self._weapon_name)
            else:
                f.setPixelSize(11)
                f.setBold(False)
                f.setItalic(True)
                p.setFont(f)
                p.setPen(QColor("#6a7290"))
                p.drawText(QRect(6, 30, self.width() - 12, self.height() - 40),
                           Qt.AlignCenter,
                           "(Empty)")

            p.end()

    vehicles = all_vehicles()
    if not vehicles:
        print(f"No vehicle database at {DB_DIR}.")
        sys.exit(1)
    nations = collect_nations(vehicles)
    ranks = collect_ranks(vehicles)
    global_weapons_idx = build_global_weapon_index(vehicles)
    global_weapons = list(global_weapons_idx.values())
    print(f"[wt3-air] {sum(len(v) for v in vehicles.values())} vehicles, "
          f"{len(global_weapons)} unique weapons indexed")

    if ICONS_DIR.exists():
        png_count = len(list(ICONS_DIR.glob("*.png")))
        print(f"[wt3-air] {png_count} icon PNGs found in {ICONS_DIR}")

    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)

    win = QMainWindow()
    win.setWindowTitle("WT3 Air Builder v2")
    win.resize(1360, 940)
    win.setMinimumSize(1100, 760)

    central = QWidget(); central.setObjectName("mainCanvas")
    ml = QVBoxLayout(central)
    ml.setContentsMargins(16, 12, 16, 16); ml.setSpacing(8)

    hdr = QLabel("WT3 Air Builder"); hdr.setObjectName("header"); ml.addWidget(hdr)
    sub = QLabel("Weightless loadout air test drive generator")
    sub.setObjectName("subheader"); ml.addWidget(sub)
    sep = QFrame(); sep.setFrameShape(QFrame.HLine); ml.addWidget(sep)
    tabs = QTabWidget(); ml.addWidget(tabs, 1)

    selected = {"id": None, "name": None}
    plane_data = {"pylons": [], "presets": [], "kind": None}
    loadout = {}

    ptab = QWidget(); pl = QVBoxLayout(ptab)
    pl.addWidget(QLabel("Player Aircraft"))
    player_btn = QPushButton("No plane selected — click to pick")
    player_btn.setObjectName("vehiclePicker")
    pl.addWidget(player_btn)

    loadout_header = QHBoxLayout()
    loadout_header.addWidget(QLabel("Loadout"))
    loadout_header.addStretch()
    override_cb = QCheckBox("Loadout override (ALL weapons, ALL planes)")
    loadout_header.addWidget(override_cb)
    clear_all_btn = QPushButton("Clear all")
    clear_all_btn.setFixedWidth(90)
    loadout_header.addWidget(clear_all_btn)
    pl.addLayout(loadout_header)

    slot_scroll = QScrollArea()
    slot_scroll.setWidgetResizable(True)
    slot_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    slot_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    slot_scroll.setMinimumHeight(158)
    slot_scroll.setMaximumHeight(175)
    slot_scroll.setStyleSheet("QScrollArea { border: 1px solid #2a2e4a;"
                              " border-radius: 6px; background: #14182c; }")
    slot_container = QWidget()
    slot_layout = QHBoxLayout(slot_container)
    slot_layout.setContentsMargins(8, 8, 8, 8)
    slot_layout.setSpacing(8)
    slot_layout.addStretch()
    slot_scroll.setWidget(slot_container)
    pl.addWidget(slot_scroll)

    preset_group = QGroupBox("Loadout Preset")
    preset_l = QVBoxLayout(preset_group)
    preset_l.addWidget(QLabel("Only used for planes with named loadout presets "
                              "(e.g. A-20G). Ignored for slot-based planes."))
    preset_box = QComboBox()
    preset_l.addWidget(preset_box)
    pl.addWidget(preset_group)

    opts = QGroupBox("Mission Options")
    opt_l = QFormLayout(opts)
    fuel_spin = QSpinBox(); fuel_spin.setRange(0, 200); fuel_spin.setValue(30)
    fuel_spin.setSuffix(" %")
    opt_l.addRow("Fuel:", fuel_spin)
    thrust_spin = QDoubleSpinBox(); thrust_spin.setRange(0.1, 20.0)
    thrust_spin.setValue(1.0); thrust_spin.setSingleStep(0.1); thrust_spin.setDecimals(2)
    opt_l.addRow("Thrust multiplier:", thrust_spin)
    aced_cb = QCheckBox("Aced Crew"); opt_l.addRow(aced_cb)
    modules_cb = QCheckBox("Research Modules"); opt_l.addRow(modules_cb)
    weightless_cb = QCheckBox("Weightless Loadout (zero carried drag/mass)")
    weightless_cb.setChecked(True)
    weightless_cb.setToolTip(
        "Injects mass:r=0.01 and dragCx:r=0.01 into every carried weapon\n"
        "block, and wraps each weapon in a stub that zeroes its in-flight\n"
        "drag. The plane flies as if the loadout weighed nothing.")
    opt_l.addRow(weightless_cb)
    pl.addWidget(opts)
    pl.addStretch()
    tabs.addTab(ptab, "  Player  ")

    ttab = QWidget(); tl = QVBoxLayout(ttab)

    def make_target_picker(label, default_kind):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        btn = QPushButton("(keep template default)")
        btn.setObjectName("targetPicker")
        btn.setProperty("filled", "false")
        btn.setMinimumHeight(34)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row.addWidget(btn, 1)
        clear = QPushButton("✕")
        clear.setObjectName("clearBtn")
        clear.setFixedWidth(34); clear.setFixedHeight(34)
        row.addWidget(clear)
        state = {"id": None, "name": None, "kind": default_kind}

        def refresh_btn(_checked=False):
            if state["id"]:
                btn.setText(f"{state['name']}   [{state['id']}]")
                btn.setProperty("filled", "true")
            else:
                btn.setText("(keep template default)")
                btn.setProperty("filled", "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

        def open_picker(_checked=False):
            dlg = make_vehicle_picker(
                vehicles, nations, ranks,
                f"Select Target — {label.strip().rstrip(':')}",
                kinds_filter=["air", "heli", "ground", "naval"])
            if dlg.exec():
                sel = dlg.selected()
                if sel:
                    state["id"] = sel[0]; state["name"] = sel[1]
                    state["kind"] = dlg.kind.currentText()
                    refresh_btn()

        def clear_sel(_checked=False):
            state["id"] = None; state["name"] = None
            refresh_btn()

        btn.clicked.connect(open_picker)
        clear.clicked.connect(clear_sel)
        c = QWidget(); c.setLayout(row)
        return c, state

    _, air_state  = make_target_picker("Enemy Air:",  "air");   tl.addWidget(_)
    _, heli_state = make_target_picker("Enemy Heli:", "heli");  tl.addWidget(_)
    tl.addWidget(QLabel(""))
    _, g1 = make_target_picker("Ground 1:", "ground"); tl.addWidget(_)
    _, g2 = make_target_picker("Ground 2:", "ground"); tl.addWidget(_)
    _, g3 = make_target_picker("Ground 3:", "ground"); tl.addWidget(_)
    _, sp = make_target_picker("SPAA:",     "ground"); tl.addWidget(_)
    _, mv = make_target_picker("Mover:",    "ground"); tl.addWidget(_)
    tl.addWidget(QLabel(""))
    _, s1 = make_target_picker("Ship 1:", "naval"); tl.addWidget(_)
    _, s2 = make_target_picker("Ship 2:", "naval"); tl.addWidget(_)
    _, s3 = make_target_picker("Ship 3:", "naval"); tl.addWidget(_)
    tl.addStretch()
    tabs.addTab(ttab, "  Targets  ")

    gtab = QWidget(); gl = QVBoxLayout(gtab)
    log_box = QPlainTextEdit(); log_box.setReadOnly(True)
    log_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    gl.addWidget(QLabel("Output:")); gl.addWidget(log_box, 1)

    def log(msg):
        log_box.appendPlainText(msg); print(f"[wt3-air] {msg}")

    slot_cards = []

    def lookup_option_anywhere(opt_id):
        for p in plane_data["pylons"]:
            for o in p.get("options", []):
                if o.get("id") == opt_id:
                    return o
        return global_weapons_idx.get(opt_id)

    def refresh_card(idx, card):
        opt_id = loadout.get(idx)
        if not opt_id:
            card.set_weapon(None)
            return
        opt = lookup_option_anywhere(opt_id)
        name = (opt or {}).get("name") or opt_id
        icon = (opt or {}).get("icon")
        card.set_weapon(name, icon)

    def on_card_clicked(idx, card):
        cur = loadout.get(idx)
        all_opts = list(global_weapons) if override_cb.isChecked() else None
        dlg = make_weapon_picker(
            plane_data["pylons"], idx, cur,
            f"Slot {idx:02d} — Select Weapon",
            all_options=all_opts,
            show_override=override_cb.isChecked())
        if dlg.exec():
            sel = dlg.selected()
            if sel:
                loadout[idx] = sel[0]
                refresh_card(idx, card)

    def on_card_cleared(idx, card):
        loadout.pop(idx, None)
        refresh_card(idx, card)

    def rebuild_slot_grid():
        while slot_layout.count():
            item = slot_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        slot_cards.clear()

        if not plane_data["pylons"]:
            lbl = QLabel("This plane uses named loadout presets — "
                         "no per-pylon grid available.")
            lbl.setStyleSheet("color: #707890; font-style: italic; padding: 20px;")
            slot_layout.addWidget(lbl)
            slot_layout.addStretch()
            return

        for pylon in plane_data["pylons"]:
            idx = pylon.get("index", 0)
            if idx == 0:
                continue
            card = SlotCard(idx)
            card.set_weapon(None)
            slot_layout.addWidget(card)
            slot_cards.append((idx, card))

            card.clicked.connect(lambda i=idx, c=card: on_card_clicked(i, c))
            card.cleared.connect(lambda i=idx, c=card: on_card_cleared(i, c))

        slot_layout.addStretch()
        for idx, card in slot_cards:
            refresh_card(idx, card)

    def clear_all_slots(_checked=False):
        loadout.clear()
        for idx, card in slot_cards:
            refresh_card(idx, card)

    clear_all_btn.clicked.connect(clear_all_slots)

    def repopulate_presets():
        preset_box.clear()
        if not selected["id"]:
            preset_box.addItem("(no plane selected)", None)
            return
        if plane_data["kind"] == "presets":
            for p in plane_data["presets"]:
                pid = p.get("id"); lbl = p.get("label") or pid
                preset_box.addItem(f"{lbl}   [{pid}]", pid)
        else:
            preset_box.addItem("(slot-based — use the grid above)", None)

    def pick_player(_checked=False):
        dlg = make_vehicle_picker(vehicles, nations, ranks,
                                  "Select Player Aircraft",
                                  kinds_filter=["air", "heli"])
        if dlg.exec():
            sel = dlg.selected()
            if sel:
                selected["id"] = sel[0]; selected["name"] = sel[1]
                player_btn.setText(f"{sel[1]}   [{sel[0]}]")
                v = find_vehicle(vehicles, sel[0])
                plane_data["kind"] = v.get("loadoutKind") if v else None
                plane_data["pylons"] = get_plane_pylons(vehicles, sel[0])
                plane_data["presets"] = get_plane_presets(vehicles, sel[0])
                loadout.clear()
                rebuild_slot_grid()
                repopulate_presets()

    player_btn.clicked.connect(pick_player)
    repopulate_presets()

    def do_generate(_checked=False):
        if not selected["id"]:
            QMessageBox.warning(win, "No plane", "Pick a player aircraft first.")
            return

        slot_options = dict(loadout)
        if plane_data["kind"] == "presets":
            preset_id = preset_box.currentData()
            p = next((x for x in plane_data["presets"] if x.get("id") == preset_id), None)
            if p:
                slot_options = {int(k): v for k, v in (p.get("slots") or {}).items()}

        weightless = weightless_cb.isChecked()

        try:
            log(f"Extracting {selected['id']} from aces.vromfs.bin…")
            src = extract_plane(selected["id"])
            if not src:
                raise RuntimeError(f"could not extract {selected['id']}.blk")
            log(f"  OK: {src}")
        except Exception as e:
            log(f"ERROR extracting plane: {e}")
            QMessageBox.critical(win, "Extraction failed", str(e))
            return

        try:
            plane_text = src.read_text(encoding="utf-8", errors="replace")
            stub, wrappers, report, custom_preset_map = write_player_stub(
                selected["id"], plane_text, slot_options,
                global_weapons_idx, plane_data["pylons"],
                weightless=weightless)
            log(f"WROTE PLAYER STUB: {stub}")
            if weightless:
                log(f"WROTE {len(wrappers)} WEIGHTLESS WRAPPERS")
            else:
                log("WEIGHTLESS OFF — using stock weapon blks")
            log("LOADOUT REPORT:")
            for slot_idx, chosen, kind, detail in report:
                log(f"    slot {slot_idx:02d}: {chosen} [{kind}] {detail}")
        except Exception as e:
            log(f"ERROR writing stub: {e}")
            QMessageBox.critical(win, "Stub write failed", str(e))
            return

        try:
            preset_paths = write_custom_preset(custom_preset_map)
            for p in preset_paths:
                log(f"WROTE PRESET: {p}")
            if not preset_paths:
                raise RuntimeError("no preset paths written")
        except Exception as e:
            log(f"ERROR writing preset: {e}")
            QMessageBox.critical(win, "Preset write failed", str(e))
            return

        targets = {}
        for key, st in [("air", air_state), ("heli", heli_state),
                        ("ground1", g1), ("ground2", g2), ("ground3", g3),
                        ("spaa", sp), ("mover", mv),
                        ("ship1", s1), ("ship2", s2), ("ship3", s3)]:
            if st["id"]:
                targets[key] = st["id"]

        try:
            report_mission = patch_air_mission(
                selected["id"], "ask3lad_custom", targets, vehicles,
                aced=aced_cb.isChecked(),
                modules=modules_cb.isChecked(),
                fuel=fuel_spin.value(),
                thrust_mult=thrust_spin.value(),
            )
            for line in report_mission:
                log(f"  {line}")
            log(f"WROTE MISSION: {BASE_MISSION}")
            log("DONE.")
        except Exception as e:
            log(f"ERROR patching mission: {e}")
            QMessageBox.critical(win, "Mission patch failed", str(e))

    gen_btn = QPushButton("GENERATE AIR MISSION")
    gen_btn.setObjectName("generateBtn")
    gen_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    gen_btn.clicked.connect(do_generate)
    gl.addWidget(gen_btn)
    tabs.addTab(gtab, "  Generate  ")

    win.setCentralWidget(central)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()