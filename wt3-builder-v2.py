#!/usr/bin/env python3
"""wt3-builder-v2 — War Thunder Test Drive Generator.

v2.5: research modules / aced crew are now inserted at the same position
Ask3lad's own templates put them — right before the You block's props{}.
Previously we inserted them after unit_class, which the parser ignored.
"""
import json
import re
import sys
from pathlib import Path

BUILDER_DIR = Path.home() / "wt-builder"
DB_DIR = BUILDER_DIR / "database"
TEMPLATE_DIR = BUILDER_DIR / "templates"
TEMPLATE = TEMPLATE_DIR / "ground.blk"

WT_DIR = Path.home() / ".local/share/Steam/steamapps/common/War Thunder"
MISSIONS = WT_DIR / "UserMissions" / "Ask3lad"
USER_VEHICLES = WT_DIR / "content" / "pkg_local" / "gameData" / "units" / "tankModels" / "userVehicles"
WEAPON_PRESETS = WT_DIR / "content" / "pkg_local" / "gameData" / "units" / "tankModels" / "weaponPresets"
ASK3LAD_WEAPONS = WT_DIR / "content" / "pkg_local" / "gameData" / "weapons" / "ask3lad"

BASE_MISSION = MISSIONS / "ask3lad_testdrive.blk"
BASE_STUB = "us_m2a4"


QSS = """
QWidget {
    background-color: transparent;
    color: #e0e0e0;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}
QMainWindow { background: #0f0f1e; }
QWidget#mainCanvas {
    background: qlineargradient(x1:0, y1:0, x2:0.3, y2:1,
        stop:0   #1e1e3a,
        stop:0.45 #17172e,
        stop:1   #0f0f1e);
}
QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a2e, stop:1 #10101e);
}

QTabWidget::pane {
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    background: rgba(22, 22, 42, 0.85);
    top: -1px;
}
QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #232342, stop:1 #1c1c34);
    color: #a0a0b8;
    padding: 10px 22px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #2a2a4a;
    border-bottom: none;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a5cdb, stop:1 #2a3a9e);
    color: #ffffff;
    border-color: #6a7aee;
}
QTabBar::tab:hover:!selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #35355c, stop:1 #242444);
    color: #d0d0e8;
}

QGroupBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(30, 30, 56, 0.9), stop:1 rgba(22, 22, 44, 0.9));
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    margin-top: 12px;
    padding: 14px 8px 8px 8px;
    font-weight: 600;
    color: #c0c0d8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: #8c9cee;
    background: transparent;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b4cca, stop:1 #2a3a9e);
    color: #ffffff;
    border: 1px solid #4a5cdb;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a6ceb, stop:1 #3b4cca);
    border-color: #8a9aee;
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1f2a7a, stop:1 #151c5c);
    border-color: #3b4cca;
}
QPushButton:disabled {
    background: #2a2a3a; color: #606078; border-color: #3a3a4a;
}

QPushButton#vehiclePicker {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2a3a6e, stop:0.5 #3a4a9e, stop:1 #2a3a6e);
    border: 1px dashed #6a7aee;
    text-align: left;
    padding: 14px 18px;
    font-weight: 500;
    font-size: 14px;
    min-height: 24px;
}
QPushButton#vehiclePicker:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a4a8e, stop:0.5 #5a6cdb, stop:1 #3a4a8e);
    border-style: solid;
    border-color: #a0b0ff;
}
QPushButton#vehiclePicker:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1e2a4e, stop:0.5 #2a3a6e, stop:1 #1e2a4e);
}

QPushButton#shellSlot {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(30, 30, 56, 0.9), stop:1 rgba(20, 20, 40, 0.9));
    border: 1px solid #2a2a4a;
    text-align: left;
    padding: 9px 12px;
    font-weight: 400;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
    min-height: 22px;
}
QPushButton#shellSlot:hover {
    border-color: #6a7aee;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(40, 40, 76, 0.95), stop:1 rgba(28, 28, 56, 0.95));
}
QPushButton#shellSlot:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(20, 20, 40, 1), stop:1 rgba(30, 30, 56, 1));
}
QPushButton#shellSlot[filled="true"] {
    border-color: #4a8a4a;
    color: #e0ffe0;
}
QPushButton#shellSlot[filled="false"] {
    color: #707088;
    font-style: italic;
}

QPushButton#targetPicker {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(30, 30, 56, 0.9), stop:1 rgba(20, 20, 40, 0.9));
    border: 1px solid #2a2a4a;
    text-align: left;
    padding: 8px 12px;
    font-weight: 400;
    font-size: 13px;
    min-height: 22px;
}
QPushButton#targetPicker:hover {
    border-color: #6a7aee;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(40, 40, 76, 0.95), stop:1 rgba(28, 28, 56, 0.95));
}
QPushButton#targetPicker:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(20, 20, 40, 1), stop:1 rgba(30, 30, 56, 1));
}
QPushButton#targetPicker[filled="true"] {
    border-color: #4a8a4a;
    color: #e0ffe0;
}
QPushButton#targetPicker[filled="false"] {
    color: #707088;
    font-style: italic;
}

QPushButton#clearBtn {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3a2a2a, stop:1 #2a1e1e);
    border: 1px solid #5a3a3a;
    color: #d09090;
    padding: 6px;
    font-weight: 700;
    min-width: 26px;
    font-size: 14px;
}
QPushButton#clearBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6a2a2a, stop:1 #4a1e1e);
    border-color: #d05a5a;
    color: #ffd0d0;
}
QPushButton#clearBtn:pressed {
    background: #3a1a1a;
    border-color: #8a3a3a;
    color: #ff9090;
}

QPushButton#generateBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #d09000, stop:0.5 #f5c518, stop:1 #d09000);
    color: #1a1a2e;
    border: 2px solid #ffd700;
    border-radius: 8px;
    font-size: 18px;
    font-weight: 800;
    padding: 16px;
    min-height: 30px;
    letter-spacing: 1px;
}
QPushButton#generateBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f0b000, stop:0.5 #ffdd33, stop:1 #f0b000);
    border-color: #ffffff;
}
QPushButton#generateBtn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #b07000, stop:1 #b07000);
    border-color: #d09000;
}

QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #22223e, stop:1 #1a1a30);
    border: 1px solid #2a2a4a;
    border-radius: 5px;
    padding: 6px 10px;
    color: #e0e0e0;
    min-height: 18px;
}
QComboBox:hover { border-color: #6a7aee; background: #26264a; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #1e1e38;
    border: 1px solid #4a5cdb;
    color: #e0e0e0;
    selection-background-color: #3b4cca;
    selection-color: #ffffff;
    outline: none;
}

QLineEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a30, stop:1 #15152a);
    border: 1px solid #2a2a4a;
    border-radius: 5px;
    padding: 7px 10px;
    color: #e0e0e0;
}
QLineEdit:hover { border-color: #4a5cdb; }
QLineEdit:focus { border-color: #8a9aee; background: #202040; }

QSpinBox, QDoubleSpinBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a30, stop:1 #15152a);
    border: 1px solid #2a2a4a;
    border-radius: 5px;
    padding: 5px 8px;
    color: #e0e0e0;
}
QSpinBox:hover, QDoubleSpinBox:hover { border-color: #4a5cdb; }
QSpinBox:focus, QDoubleSpinBox:focus { border-color: #8a9aee; }

QCheckBox { spacing: 8px; color: #c0c0d8; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 1px solid #3a3a5a;
    background: #1e1e38;
}
QCheckBox::indicator:hover { border-color: #6a7aee; }
QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #4a5cdb, stop:1 #7a8cff);
    border-color: #8a9aee;
}

QListWidget {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #16162a, stop:1 #101020);
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    color: #e0e0e0;
    outline: none;
}
QListWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #1e1e38;
}
QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3b4cca, stop:1 #2a3a9e);
    color: #ffffff;
}
QListWidget::item:hover:!selected { background: #222242; }

QPlainTextEdit {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #080814, stop:1 #0e0e1e);
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    color: #a0d0a0;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12px;
    padding: 6px;
}

QScrollBar:vertical { background: #16162a; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a3a5a, stop:1 #4a4a6a);
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #6a7aee; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QLabel { color: #c0c0d8; background: transparent; }
QLabel#header {
    font-size: 24px;
    font-weight: 800;
    color: #9aacee;
    padding: 8px 0;
    letter-spacing: 1px;
}
QLabel#subheader { font-size: 11px; color: #707088; padding-bottom: 4px; }
QLabel#detailBox {
    background: rgba(18, 18, 42, 0.95);
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 10px;
    color: #a0a0c0;
    font-family: "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
}

QFrame[frameShape="4"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 transparent, stop:0.5 #4a5cdb, stop:1 transparent);
    max-height: 1px;
    border: none;
}
"""


NATION_FROM_PREFIX = {
    "us": "USA", "usa": "USA",
    "germ": "Germany", "ger": "Germany", "germany": "Germany",
    "ussr": "USSR", "rus": "Russia", "russia": "USSR", "su": "USSR",
    "brit": "Britain", "uk": "Britain", "gb": "Britain",
    "jp": "Japan", "japan": "Japan", "jpn": "Japan",
    "cn": "China", "china": "China", "ch": "China",
    "it": "Italy", "italy": "Italy", "ita": "Italy",
    "fr": "France", "france": "France", "fra": "France",
    "sw": "Sweden", "swe": "Sweden", "sweden": "Sweden",
    "il": "Israel", "isr": "Israel", "israel": "Israel",
}

AMMO_TYPES = [
    ("APFSDS", "APFSDS"), ("APDSFS", "APFSDS"),
    ("APDS",   "APDS"),
    ("APCR",   "APCR"), ("HVAP", "APCR"),
    ("APCBC",  "APCBC"), ("APBC", "APBC"),
    ("APHE",   "APHE"), ("APC", "APC"), ("AP", "AP"),
    ("SAP",    "SAP"),
    ("HEATFS", "HEATFS"), ("HEAT-FS", "HEATFS"),
    ("HEAT",   "HEAT"),
    ("HESH",   "HESH"),
    ("HEFI",   "HEFI"), ("HEI", "HEI"), ("HEF", "HEF"), ("HE", "HE"),
    ("ATGM",   "ATGM"), ("SAM", "SAM"), ("AAM", "AAM"),
    ("RKT",    "Rocket"),
]


def parse_nation(ammo_id, ammo_name, fallback=None):
    if ammo_id:
        low = ammo_id.lower()
        for prefix, nation in NATION_FROM_PREFIX.items():
            if low.startswith(prefix + "_"):
                return nation
    if ammo_name:
        low = ammo_name.lower()
        for prefix, nation in NATION_FROM_PREFIX.items():
            if low.startswith(prefix + " "):
                return nation
    return fallback or "?"


def parse_ammo_type(ammo_name, ammo_id):
    for hay in (ammo_name, ammo_id):
        if not hay: continue
        up = hay.upper()
        for key, label in AMMO_TYPES:
            if key in up:
                return label
    return "?"


def parse_caliber(ammo_name, ammo_id):
    for hay in (ammo_name, ammo_id):
        if not hay: continue
        m = re.search(r'(\d+(?:[.,]\d+)?)\s*mm', hay, re.IGNORECASE)
        if m:
            return f"{m.group(1).replace(',', '.')} mm"
    return "?"


def enrich_ammo(ammo, fallback_nation=None):
    aid = ammo.get("id") or ""
    name = ammo.get("name") or aid
    nation = ammo.get("nation") or parse_nation(aid, name, fallback_nation)
    atype = ammo.get("type") or ammo.get("ammoType") or parse_ammo_type(name, aid)
    caliber = ammo.get("caliber") or parse_caliber(name, aid)
    vel = (ammo.get("velocity") or ammo.get("speed")
           or ammo.get("muzzleVelocity") or ammo.get("v0"))
    pen = (ammo.get("penetration") or ammo.get("pen")
           or ammo.get("penetrationAt100m") or ammo.get("pen100"))
    out = dict(ammo)
    out.update({"nation": nation, "type": atype, "caliber": caliber,
                "velocity": vel, "penetration": pen})
    return out


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
    for k in ("ground", "air", "heli", "naval"):
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


def get_vehicle_preset(vehicles, vehicle_id):
    v = find_vehicle(vehicles, vehicle_id)
    if v and v.get("preset"):
        return v["preset"]
    return f"{vehicle_id}_default"


def collect_cannon_paths(vehicles):
    paths = {}
    for vs in vehicles.values():
        for v in vs:
            for w in v.get("weapons", []):
                blk = w.get("blk", "")
                if blk and "cannon" in blk.lower():
                    paths.setdefault(blk, set()).add(v.get("name", "?"))
    return paths


def build_cannon_ammo_index(vehicles):
    idx = {}
    for vs in vehicles.values():
        for v in vs:
            limits = v.get("ammoLimits", {})
            nation = v.get("nation")
            cannons = set()
            for w in v.get("weapons", []):
                blk = w.get("blk", "")
                if blk and "cannon" in blk.lower():
                    cannons.add(blk)
            for cannon_blk in cannons:
                bucket = idx.setdefault(cannon_blk, {})
                for a in v.get("ammo", []):
                    aid = a.get("id")
                    if not aid or aid in bucket: continue
                    pool = a.get("pool", "")
                    bucket[aid] = enrich_ammo(
                        {"id": aid, "name": a.get("name", aid),
                         "pool": pool, "limit": limits.get(pool, 30)},
                        fallback_nation=nation)
    return {k: sorted(v.values(), key=lambda x: x["name"]) for k, v in idx.items()}


def build_global_ammo_index(vehicles):
    idx = {}
    for vs in vehicles.values():
        for v in vs:
            nation = v.get("nation")
            for a in v.get("ammo", []):
                aid = a.get("id")
                if not aid or aid in idx: continue
                idx[aid] = enrich_ammo(
                    {"id": aid, "name": a.get("name", aid),
                     "pool": a.get("pool", ""), "limit": 30},
                    fallback_nation=nation)
    return idx


def collect_nations(vehicles):
    s = set()
    for vs in vehicles.values():
        for v in vs:
            n = v.get("nation")
            if n: s.add(n)
    return sorted(s)


def collect_classes(vehicles):
    s = set()
    for vs in vehicles.values():
        for v in vs:
            c = v.get("class")
            if c: s.add(c)
    return sorted(s)


def build_vehicle_stub(vehicle_id, features):
    lines = [f'include "#/develop/gameBase/gameData/units/tankModels/{vehicle_id}.blk"', ""]
    wo = features.get("weapon_override")
    if wo:
        preset = wo["preset_name"] or f"{vehicle_id}_default"
        preset_blk = wo.get("preset_blk") or f"gameData/units/tankmodels/{vehicle_id}.blk"
        lines += [
            f'"@override:weapon_presets" {{ "@override:preset[1]" {{ "@override:name":t = "{preset}"}}}}',
            f'"@override:weapon_presets" {{ "@override:preset[1]" {{ "@override:blk":t = "{preset_blk}"}}}}',
            "",
            f'"@override:commonWeapons" {{ "@override:Weapon[1]" {{ "@override:trigger":t = "gunner0"}}}}',
            f'"@override:commonWeapons" {{ "@override:Weapon[1]" {{ "@override:blk":t = "{wo["weapon_blk"]}"}}}}',
            "",
        ]
    eo = features.get("engine_override")
    if eo:
        lines += [
            f'"@override:VehiclePhys" {{ "@override:Mass" {{ "@override:Empty":r={eo["mass"]}}}}}',
            f'"@override:VehiclePhys" {{ "@override:engine" {{ "@override:horsePowers":r={eo["hp"]}}}}}',
            f'"@override:VehiclePhys" {{ "@override:engine" {{ "@override:maxRPM":r={eo["max_rpm"]}}}}}',
            f'"@override:VehiclePhys" {{ "@override:engine" {{ "@override:minRPM":r={eo["min_rpm"]}}}}}',
            "",
        ]
    lines += ["//Generated by wt3-builder-v2", f"//Change '{BASE_STUB}' from line to any Tank ID", ""]
    return "\n".join(lines)


def build_weapon_stub(name, base_weapon_blk, overrides):
    lines = [f"// wt3-builder-v2 custom weapon: {name}", f'include "#/develop/gameBase/{base_weapon_blk}"']
    for kind, params in overrides:
        if kind == "bullet_speed":
            lines.append(f'"@override:bullets[0]" {{ "@override:speed":r={params["speed"]}}}')
        elif kind == "caliber":
            lines.append(f'"@override:bullets[0]" {{ "@override:caliber":r={params["caliber"]}}}')
        elif kind == "mass":
            lines.append(f'"@override:bullets[0]" {{ "@override:mass":r={params["mass"]} }}')
        elif kind == "explosive":
            lines.append(f'"@override:bullets[0]" {{ "@override:explosiveMass":r={params["mass"]} }}')
        elif kind == "no_recoil":
            lines += ['recoilMultiplier:r=0.0', 'recoilOffset:r=0.0']
        elif kind == "rapid_fire":
            freq = params["freq"]
            lines += [
                f'"@override:shotFreq":r={freq}',
                f'reloadTime:r={round(1.0/freq, 4)}',
                f'"@override:reloadTime":r={round(1.0/freq, 4)}',
                "bEnablePause:b=no",
                '"@override:bEnablePause":b=no',
            ]
    return "\n".join(lines) + "\n"


def build_triggers_block(gameplay, respawn_names, respawn_time):
    blocks = []
    gp_actions = []
    if gameplay:
        if gameplay.get("player_immortal"):
            gp_actions.append('          unitSetProperties {\n'
                              '            object:t="You"\n'
                              '            isImmortal:b=yes\n'
                              '          }')
        if gameplay.get("ai_skill") is not None:
            gp_actions.append(f'          unitSetProperties {{\n'
                              f'            object:t="Target_Ground_01"\n'
                              f'            ai_skill:r={gameplay["ai_skill"]}\n'
                              f'          }}')
        if gameplay.get("enemy_accuracy") is not None:
            gp_actions.append(f'          unitSetProperties {{\n'
                              f'            object:t="Target_Ground_01"\n'
                              f'            accuracy:r={gameplay["enemy_accuracy"]}\n'
                              f'          }}')
        if gameplay.get("ignore_player"):
            gp_actions.append('          unitSetProperties {\n'
                              '            object:t="Target_Ground_01"\n'
                              '            ignoresEnemy:b=yes\n'
                              '          }')
    if gp_actions:
        actions_str = "\n".join(gp_actions)
        blocks.append(
            '  wt3_gameplay{\n'
            '    is_enabled:b=yes\n'
            '    comments:t="auto-generated by wt3-builder-v2"\n'
            '    props{\n'
            '      actionsType:t="PERFORM_ONE_BY_ONE"\n'
            '      conditionsType:t="ALL"\n'
            '      enableAfterComplete:b=no\n'
            '    }\n'
            '    events{\n'
            '      initMission{}\n'
            '    }\n'
            '    conditions{}\n'
            f'    actions{{\n{actions_str}\n    }}\n'
            '    else_actions{}\n'
            '  }\n'
        )
    for unit_name in respawn_names:
        safe = unit_name.replace('"', '')
        blocks.append(
            f'  wt3_respawn_{safe}{{\n'
            f'    is_enabled:b=yes\n'
            f'    comments:t="auto respawn"\n'
            f'    props{{\n'
            f'      actionsType:t="PERFORM_ONE_BY_ONE"\n'
            f'      conditionsType:t="ALL"\n'
            f'      enableAfterComplete:b=yes\n'
            f'    }}\n'
            f'    events{{\n'
            f'      periodicEvent{{\n'
            f'        time:r=1\n'
            f'      }}\n'
            f'    }}\n'
            f'    conditions{{\n'
            f'      unitWhenStatus{{\n'
            f'        object_type:t="isKilled"\n'
            f'        check_objects:t="any"\n'
            f'        object_marking:i=0\n'
            f'        object_var_name:t=""\n'
            f'        object_var_comp_op:t="equal"\n'
            f'        object_var_value:i=0\n'
            f'        target_type:t="isAlive"\n'
            f'        check_period:r=1\n'
            f'        object:t="{safe}"\n'
            f'      }}\n'
            f'    }}\n'
            f'    actions{{\n'
            f'      wait{{\n'
            f'        time:r={respawn_time}\n'
            f'      }}\n'
            f'      unitRestore{{\n'
            f'        target_marking:i=0\n'
            f'        ressurectIfDead:b=yes\n'
            f'        fullRestore:b=yes\n'
            f'        target:t="{safe}"\n'
            f'      }}\n'
            f'    }}\n'
            f'    else_actions{{}}\n'
            f'  }}\n'
        )
    return "\n".join(blocks)


def swap_unit_class(text, unit_name, new_class, new_preset=None):
    n_class = n_wpn = 0
    pattern = rf'name:t="{re.escape(unit_name)}"((?:(?!name:t=)[\s\S])*?)unit_class:t="[^"]*"'
    replacement = rf'name:t="{unit_name}"\1unit_class:t="{new_class}"'
    text, n_class = re.subn(pattern, replacement, text, count=1)
    if new_preset:
        pat_w = rf'(name:t="{re.escape(unit_name)}"(?:(?!name:t=)[\s\S])*?weapons:t=")[^"]*(")'
        text, n_wpn = re.subn(pat_w, rf'\g<1>{new_preset}\g<2>', text, count=1)
    return text, n_class, n_wpn


def set_heli_altitude(text, altitude):
    n_total = 0
    tm_pat = (r'(name:t="{unit}"(?:(?!name:t=)[\s\S])*?'
              r'tm:m=\[\[[^\]]*\] \[[^\]]*\] \[[^\]]*\] \[[^,]+,\s*)[-\d.]+')
    for unit in ("Target_Heli_01", "Point_Heli_01", "Point_Heli_02"):
        pat = tm_pat.replace("{unit}", re.escape(unit))
        text, n = re.subn(pat, rf'\g<1>{altitude}', text, count=1)
        n_total += n
    pat = r'(name:t="Target_Heli_01"(?:(?!name:t=)[\s\S])*?altLimit:r=)[-\d.]+'
    text, n = re.subn(pat, rf'\g<1>{altitude + 1000}', text, count=1)
    n_total += n
    pat = r'(name:t="Target_Heli_01"(?:(?!name:t=)[\s\S])*?minimum_distance_to_earth:r=)[-\d.]+'
    text, n = re.subn(pat, rf'\g<1>50', text, count=1)
    n_total += n
    pat = r'(altRange:p2=-100000,\s*)300'
    text, n = re.subn(pat, rf'\g<1>{altitude + 500}', text, count=1)
    n_total += n
    return text, n_total


def ensure_player_mods(text, aced, modules):
    """Insert crewSkillK / applyAllMods at the very end of the You block's
    field list, immediately before its props{ opening. This matches exactly
    where Ask3lad's own templates place them — putting them anywhere else
    (e.g. right after unit_class) makes the parser ignore them.
    """
    if not aced and not modules:
        return text, 0

    # Capture (a) the You block fields section and (b) the props{ opener.
    # The negative lookahead prevents crossing into a following unit.
    pattern = r'(name:t="You"(?:(?!name:t=)[\s\S])*?)([ \t]*\n[ \t]*props[ \t]*\{)'
    m = re.search(pattern, text)
    if not m:
        return text, 0

    head = m.group(1)
    tail = m.group(2)

    # Remove any existing crewSkillK / applyAllMods from the head so we
    # don't end up with duplicates.
    head = re.sub(r'\n[ \t]*crewSkillK:r=[\d.]+', '', head)
    head = re.sub(r'\n[ \t]*applyAllMods:b=\w+', '', head)

    additions = []
    if aced:
        additions.append('    crewSkillK:r=1')
    if modules:
        additions.append('    applyAllMods:b=yes')

    new_head = head.rstrip() + '\n' + '\n'.join(additions)

    new_text = text[:m.start()] + new_head + tail + text[m.end():]
    return new_text, len(additions)


def inject_weather(text, env, weather):
    n_env = n_wx = 0
    if env:
        text, n_env = re.subn(r'(environment:t=")[^"]*(")', rf'\g<1>{env}\g<2>', text, count=1)
    if weather:
        text, n_wx = re.subn(r'(weather:t=")[^"]*(")', rf'\g<1>{weather}\g<2>', text, count=1)
    return text, n_env, n_wx


def inject_triggers(text, extra_triggers):
    if not extra_triggers.strip():
        return text, 0
    m = re.search(r'\ntriggers\s*\{[\s\S]*?\n\}', text)
    if m:
        insert_pos = m.end() - 2
        new_text = text[:insert_pos] + "\n\n" + extra_triggers.rstrip() + text[insert_pos:]
        return new_text, 1
    else:
        wrapped = ("triggers{\n"
                   "  isCategory:b=yes\n"
                   "  is_enabled:b=yes\n\n"
                   + extra_triggers.rstrip() + "\n}\n")
        return text.rstrip() + "\n\n" + wrapped, 1


def patch_mission(player_vehicle, targets, vehicles, player_ammo=None,
                  player_preset_override=None, aced=False, modules=False,
                  respawn=None, weather=None, gameplay=None,
                  heli_altitude=None):
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Template missing at {TEMPLATE}")

    text = TEMPLATE.read_text(encoding="utf-8")
    report = []

    player_preset = player_preset_override or get_vehicle_preset(vehicles, player_vehicle)
    text, n, n_p = swap_unit_class(text, "You", f"userVehicles/{BASE_STUB}", player_preset)
    report.append(f"player -> userVehicles/{BASE_STUB} (real: {player_vehicle}) : class {n} preset {n_p}")

    text, n_mods = ensure_player_mods(text, aced, modules)
    if n_mods:
        bits = []
        if aced: bits.append("aced")
        if modules: bits.append("modules")
        report.append(f"player mods ({'+'.join(bits)}) : {n_mods} edits")

    if player_ammo:
        for slot, entry in player_ammo.items():
            ammo_id, count = entry
            pat_t = rf'(name:t="You"(?:(?!name:t=)[\s\S])*?bullets{slot}:t=")[^"]*(")'
            text, n3 = re.subn(pat_t, rf'\g<1>{ammo_id}\g<2>', text, count=1)
            pat_c = rf'(name:t="You"(?:(?!name:t=)[\s\S])*?bulletsCount{slot}:i=)\d+'
            text, n4 = re.subn(pat_c, rf'\g<1>{count}', text, count=1)
            report.append(f"ammo slot {slot} -> {ammo_id} x{count} : {n3}/{n4}")

    if weather:
        text, n_env, n_wx = inject_weather(text, weather.get("environment"), weather.get("weather"))
        if n_env: report.append(f"environment -> {weather['environment']}")
        if n_wx:  report.append(f"weather -> {weather['weather']}")

    respawn = respawn or {}
    rtime = respawn.get("time", 5.0)
    rflags = respawn.get("flags", {})

    unit_slot_map = {
        "ground1": "Target_Ground_01", "ground2": "Target_Ground_02",
        "ground3": "Target_Ground_03", "ground4": "Target_Ground_04",
        "ground5": "Target_Ground_05",
        "mover":   "Target_Ground_Mover",
        "air":     "Target_Air_01",
        "heli":    "Target_Heli_01",
        "ship":    "Target_Ship_01",
    }

    respawn_names = []
    for slot_key, unit_name in unit_slot_map.items():
        tid = targets.get(slot_key)
        if tid:
            new_preset = get_vehicle_preset(vehicles, tid)
            text, n, n_p = swap_unit_class(text, unit_name, tid, new_preset)
            report.append(f"{slot_key} -> {tid} : class {n} preset {n_p} ({new_preset})")
        if rflags.get(slot_key):
            respawn_names.append(unit_name)

    if heli_altitude and heli_altitude > 0:
        text, n = set_heli_altitude(text, heli_altitude)
        report.append(f"heli safety altitude -> {heli_altitude} m : {n} edits")

    trigger_block = build_triggers_block(gameplay or {}, respawn_names, rtime)
    if trigger_block:
        text, n = inject_triggers(text, trigger_block)
        report.append(f"triggers injected (respawn: {len(respawn_names)}) : {n}")

    BASE_MISSION.parent.mkdir(parents=True, exist_ok=True)
    BASE_MISSION.write_text(text, encoding="utf-8")
    return report


def make_vehicle_picker_dialog(vehicles, nations, classes,
                               title="Select Vehicle", preset_kind=None):
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
        QListWidget, QListWidgetItem, QDialogButtonBox,
    )
    from PySide6.QtCore import Qt

    class VehiclePickerDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle(title)
            self.resize(820, 640)
            self._selected = None

            root = QVBoxLayout(self)
            self.search = QLineEdit()
            self.search.setPlaceholderText("Search by name or ID…")
            root.addWidget(self.search)

            filter_row = QHBoxLayout()
            filter_row.addWidget(QLabel("Kind:"))
            self.kind = QComboBox(); self.kind.addItems(list(vehicles.keys()))
            if preset_kind and preset_kind in vehicles:
                self.kind.setCurrentText(preset_kind)
            filter_row.addWidget(self.kind)
            filter_row.addWidget(QLabel("Nation:"))
            self.nation = QComboBox(); self.nation.addItem("All", "")
            for n in nations:
                self.nation.addItem(n.capitalize(), n)
            filter_row.addWidget(self.nation)
            filter_row.addWidget(QLabel("Type:"))
            self.klass = QComboBox(); self.klass.addItem("All", "")
            for c in classes:
                self.klass.addItem(c.replace("_", " "), c)
            filter_row.addWidget(self.klass)
            filter_row.addStretch()
            root.addLayout(filter_row)

            self.list = QListWidget()
            root.addWidget(self.list, 1)

            self.count_label = QLabel("")
            self.count_label.setObjectName("subheader")
            root.addWidget(self.count_label)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            root.addWidget(buttons)

            self.search.textChanged.connect(self.refresh)
            self.kind.currentTextChanged.connect(self.refresh)
            self.nation.currentTextChanged.connect(self.refresh)
            self.klass.currentTextChanged.connect(self.refresh)
            self.list.itemDoubleClicked.connect(lambda _: self.accept())

            self.refresh()
            self.search.setFocus()

        def refresh(self):
            self.list.clear()
            kind = self.kind.currentText()
            nation = self.nation.currentData()
            klass = self.klass.currentData()
            q = self.search.text().lower()
            count = 0
            for v in vehicles.get(kind, []):
                name = v.get("name", "?"); vid = v.get("id", "?")
                if nation and v.get("nation") != nation: continue
                if klass and v.get("class") != klass: continue
                if q and q not in name.lower() and q not in vid.lower(): continue
                item = QListWidgetItem(f"{name}  ·  [{vid}]")
                item.setData(Qt.UserRole, vid)
                item.setData(Qt.UserRole + 1, name)
                self.list.addItem(item)
                count += 1
            self.count_label.setText(f"{count} vehicles")

        def accept(self):
            item = self.list.currentItem()
            if not item:
                return
            self._selected = (item.data(Qt.UserRole), item.data(Qt.UserRole + 1))
            super().accept()

        def selected(self):
            return self._selected

    return VehiclePickerDialog()


def make_shell_picker_dialog(compatible_ammo, all_ammo_index,
                             current_ammo_id=None, cannon_label=""):
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
        QListWidget, QListWidgetItem, QDialogButtonBox, QCheckBox,
    )
    from PySide6.QtCore import Qt

    all_types = sorted({
        (a.get("type") or "?")
        for a in list(compatible_ammo) + list(all_ammo_index.values())
        if a.get("type")
    })
    all_nations = sorted({
        (a.get("nation") or "?")
        for a in list(compatible_ammo) + list(all_ammo_index.values())
        if a.get("nation")
    })

    class ShellPickerDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Select Ammunition")
            self.resize(920, 700)
            self._selected = None

            root = QVBoxLayout(self)
            if cannon_label:
                lbl = QLabel(f"cannon: {cannon_label}")
                lbl.setObjectName("subheader")
                root.addWidget(lbl)

            self.search = QLineEdit()
            self.search.setPlaceholderText("Search by name or ID…")
            root.addWidget(self.search)

            filter_row = QHBoxLayout()
            filter_row.addWidget(QLabel("Type:"))
            self.atype = QComboBox(); self.atype.addItem("All", "")
            for t in all_types:
                self.atype.addItem(t, t)
            filter_row.addWidget(self.atype)
            filter_row.addWidget(QLabel("Nation:"))
            self.nation = QComboBox(); self.nation.addItem("All", "")
            for n in all_nations:
                self.nation.addItem(n, n)
            filter_row.addWidget(self.nation)

            self.show_all = QCheckBox("Show all ammo")
            self.show_all.setToolTip(
                "Off: only ammo compatible with this cannon.\n"
                "On: every ammo in the database, even if it won't load.")
            filter_row.addWidget(self.show_all)
            filter_row.addStretch()
            root.addLayout(filter_row)

            body = QHBoxLayout()
            self.list = QListWidget()
            body.addWidget(self.list, 3)

            self.detail = QLabel("Hover an item to see its specs.")
            self.detail.setObjectName("detailBox")
            self.detail.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.detail.setMinimumWidth(250)
            self.detail.setWordWrap(True)
            body.addWidget(self.detail, 1)
            root.addLayout(body, 1)

            self.count_label = QLabel("")
            self.count_label.setObjectName("subheader")
            root.addWidget(self.count_label)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            root.addWidget(buttons)

            self.search.textChanged.connect(self.refresh)
            self.atype.currentTextChanged.connect(self.refresh)
            self.nation.currentTextChanged.connect(self.refresh)
            self.show_all.toggled.connect(self.refresh)
            self.list.itemDoubleClicked.connect(lambda _: self.accept())
            self.list.currentItemChanged.connect(self.on_hover)
            self.list.itemEntered.connect(self.on_hover)

            self.refresh()
            self.search.setFocus()
            if current_ammo_id:
                self.select_by_id(current_ammo_id)

        def _pool(self):
            if self.show_all.isChecked():
                return sorted(all_ammo_index.values(), key=lambda x: x.get("name", ""))
            return list(compatible_ammo)

        def refresh(self):
            self.list.clear()
            q = self.search.text().lower()
            atype = self.atype.currentData()
            nation = self.nation.currentData()
            count = 0
            for a in self._pool():
                name = a.get("name", a.get("id", "?"))
                aid = a.get("id", "?")
                if atype and a.get("type") != atype: continue
                if nation and a.get("nation") != nation: continue
                if q and q not in name.lower() and q not in aid.lower(): continue
                display = f"{a.get('nation','?')}  ·  {a.get('caliber','?')}  ·  {a.get('type','?')}  ·  {name}"
                item = QListWidgetItem(display)
                item.setData(Qt.UserRole, aid)
                item.setData(Qt.UserRole + 1, a)
                item.setToolTip(self._tooltip_html(a))
                self.list.addItem(item)
                count += 1
            self.count_label.setText(
                f"{count} shells  ·  {'all' if self.show_all.isChecked() else 'compatible'}")

        @staticmethod
        def _tooltip_html(a):
            def val(k):
                v = a.get(k)
                if v is None or v == "": return "—"
                return str(v)
            return (
                f"<b>{a.get('name', a.get('id','?'))}</b><br>"
                f"<table cellpadding='2'>"
                f"<tr><td><b>Nation</b></td><td>{a.get('nation','?')}</td></tr>"
                f"<tr><td><b>Type</b></td><td>{a.get('type','?')}</td></tr>"
                f"<tr><td><b>Caliber</b></td><td>{a.get('caliber','?')}</td></tr>"
                f"<tr><td><b>Velocity</b></td><td>{val('velocity')}</td></tr>"
                f"<tr><td><b>Penetration</b></td><td>{val('penetration')}</td></tr>"
                f"<tr><td><b>ID</b></td><td><code>{a.get('id','?')}</code></td></tr>"
                f"</table>"
            )

        def on_hover(self, item, *_):
            if not item:
                self.detail.setText("Hover an item to see its specs.")
                return
            a = item.data(Qt.UserRole + 1) or {}
            def val(k):
                v = a.get(k)
                if v is None or v == "": return "—"
                return str(v)
            self.detail.setText(
                f"<b>{a.get('name', a.get('id','?'))}</b><br><br>"
                f"<b>Nation</b> &nbsp; {a.get('nation','?')}<br>"
                f"<b>Type</b> &nbsp;&nbsp;&nbsp; {a.get('type','?')}<br>"
                f"<b>Caliber</b> &nbsp;&nbsp; {a.get('caliber','?')}<br>"
                f"<b>Velocity</b> &nbsp; {val('velocity')}<br>"
                f"<b>Pen</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {val('penetration')}<br><br>"
                f"<span style='color:#606078'>id: {a.get('id','?')}</span>"
            )

        def select_by_id(self, aid):
            for i in range(self.list.count()):
                it = self.list.item(i)
                if it.data(Qt.UserRole) == aid:
                    self.list.setCurrentItem(it)
                    self.list.scrollToItem(it)
                    return

        def accept(self):
            item = self.list.currentItem()
            if not item:
                return
            a = item.data(Qt.UserRole + 1) or {}
            self._selected = (a.get("id"), a)
            super().accept()

        def selected(self):
            return self._selected

    return ShellPickerDialog()


def launch_gui():
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QComboBox, QLabel, QLineEdit, QPushButton, QListWidget,
            QListWidgetItem, QCheckBox, QSpinBox, QGroupBox, QMessageBox,
            QDoubleSpinBox, QTabWidget, QFormLayout, QPlainTextEdit,
            QGridLayout, QFrame, QSizePolicy,
        )
        from PySide6.QtCore import Qt
    except ImportError:
        print("PySide6 not installed. Run: sudo dnf install python3-pyside6")
        sys.exit(1)

    vehicles = all_vehicles()
    if not vehicles:
        print(f"No vehicle database at {DB_DIR}.")
        sys.exit(1)

    cannon_map = collect_cannon_paths(vehicles)
    cannon_list = sorted(cannon_map.keys())
    cannon_ammo_index = build_cannon_ammo_index(vehicles)
    global_ammo_index = build_global_ammo_index(vehicles)
    nations = collect_nations(vehicles)
    classes = collect_classes(vehicles)

    print(f"[wt3-v2] {sum(len(v) for v in vehicles.values())} vehicles, "
          f"{len(cannon_list)} cannons indexed, "
          f"{len(global_ammo_index)} unique ammo types")

    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)

    win = QMainWindow()
    win.setWindowTitle("WT3 Builder v2 — Test Drive Generator")
    win.resize(1300, 1020)
    win.setMinimumSize(1100, 800)

    central = QWidget()
    central.setObjectName("mainCanvas")
    main_layout = QVBoxLayout(central)
    main_layout.setContentsMargins(16, 12, 16, 16)
    main_layout.setSpacing(8)

    header = QLabel("WT3 Builder  ·  v2")
    header.setObjectName("header")
    header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    main_layout.addWidget(header)
    sub = QLabel("Native Linux Test Drive generator for War Thunder")
    sub.setObjectName("subheader")
    main_layout.addWidget(sub)
    sep = QFrame(); sep.setFrameShape(QFrame.HLine)
    main_layout.addWidget(sep)

    tabs = QTabWidget()
    tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    main_layout.addWidget(tabs, 1)

    selected_vehicle_id = {"id": None, "name": None}
    slot_state = [{"ammo": None, "count": 0} for _ in range(4)]

    player_tab = QWidget()
    pl = QVBoxLayout(player_tab)
    pl.setSpacing(10)

    pl.addWidget(QLabel("Player Vehicle"))
    vehicle_btn = QPushButton("No vehicle selected  —  click to pick")
    vehicle_btn.setObjectName("vehiclePicker")
    vehicle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    pl.addWidget(vehicle_btn)

    ammo_group = QGroupBox("Ammo Loadout (4 slots)")
    ammo_grid = QGridLayout(ammo_group)
    ammo_grid.setHorizontalSpacing(8)
    ammo_grid.setVerticalSpacing(6)
    ammo_grid.addWidget(QLabel("Slot"), 0, 0)
    ammo_grid.addWidget(QLabel("Shell"), 0, 1)
    ammo_grid.addWidget(QLabel("Count"), 0, 2)
    ammo_grid.addWidget(QLabel(""), 0, 3)

    slot_buttons = []
    slot_counts = []
    slot_clears = []
    for i in range(4):
        btn = QPushButton("(empty)  —  click to pick")
        btn.setObjectName("shellSlot")
        btn.setProperty("filled", "false")
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setMinimumHeight(40)
        ammo_grid.addWidget(QLabel(f"{i}"), i + 1, 0)
        ammo_grid.addWidget(btn, i + 1, 1)

        spin = QSpinBox(); spin.setRange(0, 9999); spin.setValue(0)
        spin.setMinimumWidth(90)
        spin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        ammo_grid.addWidget(spin, i + 1, 2)

        clear_btn = QPushButton("✕")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setFixedWidth(34)
        clear_btn.setFixedHeight(34)
        clear_btn.setToolTip("Remove ammo from this slot")
        ammo_grid.addWidget(clear_btn, i + 1, 3)

        slot_buttons.append(btn)
        slot_counts.append(spin)
        slot_clears.append(clear_btn)

    ammo_grid.setColumnStretch(1, 1)
    pl.addWidget(ammo_group)
    pl.addStretch()
    tabs.addTab(player_tab, "  Player + Ammo  ")

    exp_tab = QWidget()
    el = QVBoxLayout(exp_tab)

    wo_group = QGroupBox("Weapon Override")
    wo_group.setCheckable(True); wo_group.setChecked(False)
    wo_layout = QFormLayout(wo_group)
    wo_preset = QLineEdit(); wo_preset.setPlaceholderText("leave blank for auto")
    wo_layout.addRow("Preset name:", wo_preset)
    wo_preset_blk = QLineEdit(); wo_preset_blk.setPlaceholderText("leave blank for auto")
    wo_layout.addRow("Preset blk:", wo_preset_blk)
    wo_search = QLineEdit(); wo_search.setPlaceholderText("Search cannons…")
    wo_layout.addRow("Search:", wo_search)
    wo_weapon = QComboBox(); wo_weapon.setEditable(True)
    wo_weapon.setInsertPolicy(QComboBox.NoInsert)
    wo_weapon.setMinimumWidth(600)
    wo_weapon.addItems(cannon_list)
    c = wo_weapon.completer()
    c.setCaseSensitivity(Qt.CaseInsensitive)
    c.setFilterMode(Qt.MatchContains)
    wo_layout.addRow("Weapon blk:", wo_weapon)

    def filter_cannons(text):
        wo_weapon.blockSignals(True)
        wo_weapon.clear()
        q = text.lower()
        for c_ in cannon_list:
            if not q or q in c_.lower():
                wo_weapon.addItem(c_)
        wo_weapon.blockSignals(False)

    wo_search.textChanged.connect(filter_cannons)

    wo_users_label = QLabel("")
    wo_users_label.setStyleSheet("color: gray;")
    wo_layout.addRow(wo_users_label)
    el.addWidget(wo_group)

    eo_group = QGroupBox("Engine Override")
    eo_group.setCheckable(True); eo_group.setChecked(False)
    eo_layout = QFormLayout(eo_group)
    hp = QSpinBox(); hp.setRange(100, 100000); hp.setValue(2000); eo_layout.addRow("Horsepower:", hp)
    mass = QSpinBox(); mass.setRange(100, 500000); mass.setValue(50000); eo_layout.addRow("Mass (kg):", mass)
    maxrpm = QSpinBox(); maxrpm.setRange(1000, 50000); maxrpm.setValue(15000); eo_layout.addRow("Max RPM:", maxrpm)
    minrpm = QSpinBox(); minrpm.setRange(100, 20000); minrpm.setValue(3000); eo_layout.addRow("Min RPM:", minrpm)
    el.addWidget(eo_group)

    rf_group = QGroupBox("Rapid Fire")
    rf_group.setCheckable(True); rf_group.setChecked(False)
    rf_layout = QFormLayout(rf_group)
    freq = QDoubleSpinBox(); freq.setRange(0.5, 100.0); freq.setValue(10.0); freq.setSingleStep(0.5)
    rf_layout.addRow("Shots per second:", freq)
    el.addWidget(rf_group)

    norecoil_group = QGroupBox("No Recoil")
    norecoil_group.setCheckable(True); norecoil_group.setChecked(False)
    norecoil_layout = QFormLayout(norecoil_group)
    norecoil_layout.addRow(QLabel("Zeroes out gun kick and camera shake."))
    el.addWidget(norecoil_group)

    sh_group = QGroupBox("Shell Override")
    sh_group.setCheckable(True); sh_group.setChecked(False)
    sh_layout = QFormLayout(sh_group)
    speed = QSpinBox(); speed.setRange(100, 10000); speed.setValue(2000); sh_layout.addRow("Speed (m/s):", speed)
    caliber = QDoubleSpinBox(); caliber.setRange(0.01, 1.0); caliber.setValue(0.12); caliber.setSingleStep(0.01)
    sh_layout.addRow("Caliber (m):", caliber)
    shell_mass = QDoubleSpinBox(); shell_mass.setRange(0.1, 500.0); shell_mass.setValue(10.0)
    sh_layout.addRow("Shell mass (kg):", shell_mass)
    explosive = QDoubleSpinBox(); explosive.setRange(0.0, 500.0); explosive.setValue(50.0)
    sh_layout.addRow("Explosive filler (kg):", explosive)
    el.addWidget(sh_group)
    el.addStretch()
    tabs.addTab(exp_tab, "  Experimental  ")

    tgt_tab = QWidget()
    tl = QVBoxLayout(tgt_tab)

    delay_row = QHBoxLayout()
    delay_row.addWidget(QLabel("Respawn delay (s):"))
    respawn_delay = QDoubleSpinBox()
    respawn_delay.setRange(0.5, 300.0); respawn_delay.setValue(5.0); respawn_delay.setSingleStep(0.5)
    delay_row.addWidget(respawn_delay)
    delay_row.addStretch()
    tl.addLayout(delay_row)

    heli_row = QHBoxLayout()
    heli_row.addWidget(QLabel("Heli safety altitude (m):"))
    heli_altitude = QDoubleSpinBox()
    heli_altitude.setRange(0.0, 5000.0)
    heli_altitude.setValue(400.0)
    heli_altitude.setSingleStep(50.0)
    heli_altitude.setToolTip(
        "Raises the helicopter and its two patrol points to this altitude.\n"
        "Set to 0 to leave the template's default (200 m) untouched.")
    heli_row.addWidget(heli_altitude)
    heli_row.addStretch()
    tl.addLayout(heli_row)

    def make_target_picker(label, default_kind):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))

        btn = QPushButton("(keep default)")
        btn.setObjectName("targetPicker")
        btn.setProperty("filled", "false")
        btn.setMinimumHeight(34)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        row.addWidget(btn, 1)

        clear_btn = QPushButton("✕")
        clear_btn.setObjectName("clearBtn")
        clear_btn.setFixedWidth(34)
        clear_btn.setFixedHeight(34)
        clear_btn.setToolTip("Reset to template default")
        row.addWidget(clear_btn)

        respawn_cb = QCheckBox("Respawn")
        row.addWidget(respawn_cb)

        state = {"id": None, "name": None, "kind": default_kind}

        def refresh_btn():
            if state["id"]:
                btn.setText(f"{state['name']}  ·  [{state['id']}]")
                btn.setProperty("filled", "true")
            else:
                btn.setText("(keep default)")
                btn.setProperty("filled", "false")
            btn.style().unpolish(btn); btn.style().polish(btn)

        def open_picker():
            dlg = make_vehicle_picker_dialog(
                vehicles, nations, classes,
                title=f"Select Target — {label.strip().rstrip(':')}",
                preset_kind=state["kind"])
            if dlg.exec():
                sel = dlg.selected()
                if sel:
                    state["id"] = sel[0]
                    state["name"] = sel[1]
                    state["kind"] = dlg.kind.currentText()
                    refresh_btn()

        def clear_selection():
            state["id"] = None
            state["name"] = None
            refresh_btn()

        btn.clicked.connect(open_picker)
        clear_btn.clicked.connect(clear_selection)

        c = QWidget(); c.setLayout(row)
        return c, state, respawn_cb

    ground_pickers = []
    for i in range(1, 6):
        c, state, respawn_cb = make_target_picker(f"Ground {i}:", "ground")
        tl.addWidget(c); ground_pickers.append((state, respawn_cb))
    tl.addWidget(QLabel(""))
    _, mover_state, mover_respawn = make_target_picker("Mover:", "ground"); tl.addWidget(_)
    _, air_state, air_respawn = make_target_picker("Air:", "air"); tl.addWidget(_)
    _, heli_state, heli_respawn = make_target_picker("Heli:", "heli"); tl.addWidget(_)
    _, ship_state, ship_respawn = make_target_picker("Ship:", "naval"); tl.addWidget(_)
    tl.addStretch()
    tabs.addTab(tgt_tab, "  Targets  ")

    gp_tab = QWidget()
    gl2 = QVBoxLayout(gp_tab)

    wx_group = QGroupBox("Weather & Time of Day")
    wx_layout = QFormLayout(wx_group)
    env_box = QComboBox(); env_box.addItem("(keep template)", "")
    for e in ("Day", "Evening", "Night", "Morning", "Dawn", "Dusk"):
        env_box.addItem(e, e)
    wx_layout.addRow("Environment:", env_box)
    weather_box = QComboBox(); weather_box.addItem("(keep template)", "")
    for w in ("clear", "good", "cloudy", "rainy", "thunderstorm", "foggy", "snowy"):
        weather_box.addItem(w, w)
    wx_layout.addRow("Weather:", weather_box)
    gl2.addWidget(wx_group)

    gp_group = QGroupBox("Player & Enemy Gameplay")
    gp_layout = QFormLayout(gp_group)
    immortal_check = QCheckBox("Player is immortal"); gp_layout.addRow(immortal_check)
    ignore_check = QCheckBox("Enemies ignore player (passive)"); gp_layout.addRow(ignore_check)
    ai_skill = QDoubleSpinBox(); ai_skill.setRange(0.0, 1.0); ai_skill.setValue(0.5)
    ai_skill.setSingleStep(0.1); ai_skill.setDecimals(2)
    gp_layout.addRow("AI skill (0-1):", ai_skill)
    enemy_acc = QDoubleSpinBox(); enemy_acc.setRange(0.0, 1.0); enemy_acc.setValue(0.3)
    enemy_acc.setSingleStep(0.05); enemy_acc.setDecimals(2)
    gp_layout.addRow("Enemy accuracy (0-1):", enemy_acc)
    aced_check = QCheckBox("Aced Crew"); gp_layout.addRow(aced_check)
    modules_check = QCheckBox("Research Modules"); gp_layout.addRow(modules_check)
    gl2.addWidget(gp_group)
    gl2.addStretch()
    tabs.addTab(gp_tab, "  Gameplay  ")

    gen_tab = QWidget()
    gl = QVBoxLayout(gen_tab)
    log_box = QPlainTextEdit(); log_box.setReadOnly(True)
    log_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    gl.addWidget(QLabel("Output:"))
    gl.addWidget(log_box, 1)

    def log(msg):
        log_box.appendPlainText(msg); print(f"[wt3-v2] {msg}")

    def current_compatible_ammo():
        vid = selected_vehicle_id["id"]
        if wo_group.isChecked():
            cannon = wo_weapon.currentText().strip()
            if cannon and cannon in cannon_ammo_index:
                return cannon_ammo_index[cannon]
        if vid:
            v = find_vehicle(vehicles, vid)
            if v:
                limits = v.get("ammoLimits", {})
                out = []
                for a in v.get("ammo", []):
                    pool = a.get("pool", "")
                    enriched = enrich_ammo(
                        {"id": a.get("id"), "name": a.get("name", a.get("id")),
                         "pool": pool, "limit": limits.get(pool, 30)},
                        fallback_nation=v.get("nation"))
                    out.append(enriched)
                return out
        return []

    def current_cannon_label():
        if wo_group.isChecked():
            c = wo_weapon.currentText().strip()
            if c: return c.split("/")[-1]
        vid = selected_vehicle_id["id"]
        if vid:
            v = find_vehicle(vehicles, vid)
            if v:
                for w in v.get("weapons", []):
                    blk = w.get("blk", "")
                    if blk and "cannon" in blk.lower():
                        return blk.split("/")[-1]
        return "(default)"

    def refresh_slot_btn(i):
        s = slot_state[i]
        btn = slot_buttons[i]
        a = s["ammo"]
        if a:
            display = f"{a.get('nation','?')}  ·  {a.get('caliber','?')}  ·  {a.get('type','?')}  ·  {a.get('name','?')}"
            if len(display) > 90:
                display = display[:87] + "…"
            btn.setText(display)
            btn.setProperty("filled", "true")
            btn.setToolTip(
                f"<b>{a.get('name','?')}</b><br>"
                f"Nation: {a.get('nation','?')}<br>"
                f"Type: {a.get('type','?')}<br>"
                f"Caliber: {a.get('caliber','?')}<br>"
                f"Velocity: {a.get('velocity') or '—'}<br>"
                f"Penetration: {a.get('penetration') or '—'}<br>"
                f"id: {a.get('id','?')}"
            )
        else:
            btn.setText("(empty)  —  click to pick")
            btn.setProperty("filled", "false")
            btn.setToolTip("")
        btn.style().unpolish(btn); btn.style().polish(btn)

    def clear_slot(i):
        slot_state[i]["ammo"] = None
        slot_counts[i].setValue(0)
        refresh_slot_btn(i)

    def clear_all_slots():
        for i in range(4):
            clear_slot(i)

    def auto_fill_slot_zero():
        compatible = current_compatible_ammo()
        if not compatible:
            return
        first = compatible[0]
        slot_state[0]["ammo"] = first
        slot_counts[0].setValue(first.get("limit", 30))
        refresh_slot_btn(0)

    def pick_vehicle():
        dlg = make_vehicle_picker_dialog(vehicles, nations, classes,
                                         title="Select Player Vehicle")
        if dlg.exec():
            sel = dlg.selected()
            if sel:
                selected_vehicle_id["id"] = sel[0]
                selected_vehicle_id["name"] = sel[1]
                vehicle_btn.setText(f"{sel[1]}   ·   [{sel[0]}]")
                clear_all_slots()
                auto_fill_slot_zero()

    vehicle_btn.clicked.connect(pick_vehicle)

    def pick_shell(i):
        compatible = current_compatible_ammo()
        if not compatible and not global_ammo_index:
            QMessageBox.information(win, "No ammo", "No ammo data available.")
            return
        current_id = slot_state[i]["ammo"]["id"] if slot_state[i]["ammo"] else None
        dlg = make_shell_picker_dialog(
            compatible, global_ammo_index, current_id, current_cannon_label())
        if dlg.exec():
            sel = dlg.selected()
            if sel:
                slot_state[i]["ammo"] = sel[1]
                refresh_slot_btn(i)
                if slot_counts[i].value() == 0:
                    slot_counts[i].setValue(sel[1].get("limit", 30))

    for i, btn in enumerate(slot_buttons):
        btn.clicked.connect(lambda _=False, idx=i: pick_shell(idx))
    for i, btn in enumerate(slot_clears):
        btn.clicked.connect(lambda _=False, idx=i: clear_slot(idx))

    def on_cannon_changed(*_):
        cannon = wo_weapon.currentText().strip()
        users = cannon_map.get(cannon, set())
        if users:
            wo_users_label.setText(
                f"Used by: {', '.join(sorted(users)[:6])}"
                + (f" +{len(users)-6}" if len(users) > 6 else ""))
        else:
            wo_users_label.setText("Used by: (unknown)")
        clear_all_slots()
        auto_fill_slot_zero()

    wo_weapon.currentTextChanged.connect(on_cannon_changed)

    def on_wo_toggled(*_):
        clear_all_slots()
        auto_fill_slot_zero()

    wo_group.toggled.connect(on_wo_toggled)

    def do_generate():
        if not selected_vehicle_id["id"]:
            QMessageBox.warning(win, "No vehicle", "Pick a player vehicle first."); return
        player_id = selected_vehicle_id["id"]

        player_ammo = {}
        for i in range(4):
            a = slot_state[i]["ammo"]
            c = slot_counts[i].value()
            if a and c > 0:
                player_ammo[i] = (a["id"], c)

        features = {}
        preset_override = None

        if wo_group.isChecked():
            weapon_blk = wo_weapon.currentText().strip()
            if not weapon_blk:
                QMessageBox.warning(win, "Missing weapon", "Pick a weapon blk."); return
            preset_name = wo_preset.text().strip() or f"{player_id}_default"
            preset_override = preset_name
            features["weapon_override"] = {
                "preset_name": preset_name,
                "preset_blk": wo_preset_blk.text().strip(),
                "weapon_blk": weapon_blk,
            }

        needs_weapon_stub = (
            wo_group.isChecked() or norecoil_group.isChecked()
            or rf_group.isChecked() or sh_group.isChecked()
        )
        if needs_weapon_stub and "weapon_override" not in features:
            features["weapon_override"] = {
                "preset_name": f"{player_id}_default",
                "preset_blk": "", "weapon_blk": "",
            }

        if eo_group.isChecked():
            features["engine_override"] = {
                "hp": hp.value(), "mass": mass.value(),
                "max_rpm": maxrpm.value(), "min_rpm": minrpm.value(),
            }

        weapon_overrides = []
        if rf_group.isChecked():
            weapon_overrides.append(("rapid_fire", {"freq": freq.value()}))
        if norecoil_group.isChecked():
            weapon_overrides.append(("no_recoil", {}))
        if sh_group.isChecked():
            weapon_overrides += [
                ("bullet_speed", {"speed": speed.value()}),
                ("caliber", {"caliber": caliber.value()}),
                ("mass", {"mass": shell_mass.value()}),
                ("explosive", {"mass": explosive.value()}),
            ]

        if weapon_overrides:
            base_weapon = wo_weapon.currentText().strip() or \
                          "gamedata/Weapons/groundModels_weapons/120mm_GIAT_CN120_26_F1_user_cannon.blk"
            base_weapon = base_weapon.replace("#/develop/gameBase/", "")
            stub_name = f"wt3_custom_{player_id}"
            stub_content = build_weapon_stub(stub_name, base_weapon, weapon_overrides)
            stub_path = ASK3LAD_WEAPONS / f"{stub_name}.blk"
            stub_path.parent.mkdir(parents=True, exist_ok=True)
            stub_path.write_text(stub_content, encoding="utf-8")
            log(f"WROTE WEAPON STUB: {stub_path}")
            features.setdefault("weapon_override", {})
            features["weapon_override"]["weapon_blk"] = f"gameData/weapons/ask3lad/{stub_name}.blk"
            if not features["weapon_override"].get("preset_name"):
                features["weapon_override"]["preset_name"] = f"{player_id}_default"
            preset_override = features["weapon_override"]["preset_name"]

        wo_feat = features.get("weapon_override")
        if wo_feat:
            preset_name = wo_feat.get("preset_name") or f"{player_id}_default"
            preset_path = WEAPON_PRESETS / f"{preset_name}.blk"
            preset_path.parent.mkdir(parents=True, exist_ok=True)
            if not preset_path.exists():
                preset_path.write_text("", encoding="utf-8")
                log(f"WROTE EMPTY PRESET: {preset_path}")

        stub_content = build_vehicle_stub(player_id, features)
        stub_path = USER_VEHICLES / f"{BASE_STUB}.blk"
        stub_path.parent.mkdir(parents=True, exist_ok=True)
        stub_path.write_text(stub_content, encoding="utf-8")
        log(f"WROTE VEHICLE STUB: {stub_path}")

        targets = {}
        for i, (state, _) in enumerate(ground_pickers, 1):
            if state["id"]: targets[f"ground{i}"] = state["id"]
        if mover_state["id"]: targets["mover"] = mover_state["id"]
        if air_state["id"]:   targets["air"]   = air_state["id"]
        if heli_state["id"]:  targets["heli"]  = heli_state["id"]
        if ship_state["id"]:  targets["ship"]  = ship_state["id"]

        respawn_flags = {}
        for i, (_, cb) in enumerate(ground_pickers, 1):
            if cb.isChecked():
                respawn_flags[f"ground{i}"] = True
        if mover_respawn.isChecked(): respawn_flags["mover"] = True
        if air_respawn.isChecked():   respawn_flags["air"]   = True
        if heli_respawn.isChecked():  respawn_flags["heli"]  = True
        if ship_respawn.isChecked():  respawn_flags["ship"]  = True

        respawn = {"time": respawn_delay.value(), "flags": respawn_flags}
        weather = {"environment": env_box.currentData() or None,
                   "weather": weather_box.currentData() or None}
        gameplay = {
            "player_immortal": immortal_check.isChecked(),
            "ignore_player": ignore_check.isChecked(),
            "ai_skill": ai_skill.value() if ai_skill.value() > 0 else None,
            "enemy_accuracy": enemy_acc.value() if enemy_acc.value() > 0 else None,
        }

        try:
            report = patch_mission(player_id, targets, vehicles,
                                    player_ammo=player_ammo,
                                    player_preset_override=preset_override,
                                    aced=aced_check.isChecked(),
                                    modules=modules_check.isChecked(),
                                    respawn=respawn, weather=weather,
                                    gameplay=gameplay,
                                    heli_altitude=heli_altitude.value())
            for line in report: log(f"  {line}")
            log(f"PATCHED MISSION: {BASE_MISSION}")
            log("DONE. Hangar -> User Missions -> Ask3lad -> Test Drive 3.0 - Ground")
        except Exception as e:
            log(f"ERROR: {e}")
            QMessageBox.critical(win, "Error", str(e))

    gen_btn = QPushButton("GENERATE MISSION")
    gen_btn.setObjectName("generateBtn")
    gen_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    gen_btn.clicked.connect(do_generate)
    gl.addWidget(gen_btn)
    tabs.addTab(gen_tab, "  Generate  ")

    win.setCentralWidget(central)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()