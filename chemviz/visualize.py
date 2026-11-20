"""生成初中化学可视化页面（单文件 HTML + 内联 SVG）。"""

from __future__ import annotations

import html
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .elements import (
    Element,
    ElementError,
    extra_elements,
    periodic_elements,
)

ATOM_COLORS: Dict[str, str] = {
    "H": "#f4f4f4",
    "C": "#3c4043",
    "N": "#3f6fd8",
    "O": "#d94b3d",
    "Cl": "#3f9b5a",
    "Na": "#8557c9",
}

ATOM_RADII: Dict[str, int] = {
    "H": 9,
    "C": 15,
    "N": 15,
    "O": 14,
    "Cl": 18,
    "Na": 17,
}

CATEGORY_CLASS = {
    "金属": "metal",
    "非金属": "nonmetal",
    "稀有气体": "noble",
}


@dataclass(frozen=True)
class MoleculeAtom:
    element: str
    x: float
    y: float


@dataclass(frozen=True)
class Molecule:
    formula: str
    name: str
    atoms: Tuple[MoleculeAtom, ...]
    bonds: Tuple[Tuple[int, int, int], ...]
    note: str = ""
    charges: Tuple[Tuple[int, str], ...] = ()


MOLECULES: Tuple[Molecule, ...] = (
    Molecule(
        "H2",
        "氢气",
        (MoleculeAtom("H", -22, 0), MoleculeAtom("H", 22, 0)),
        ((0, 1, 1),),
    ),
    Molecule(
        "O2",
        "氧气",
        (MoleculeAtom("O", -26, 0), MoleculeAtom("O", 26, 0)),
        ((0, 1, 2),),
    ),
    Molecule(
        "N2",
        "氮气",
        (MoleculeAtom("N", -26, 0), MoleculeAtom("N", 26, 0)),
        ((0, 1, 3),),
    ),
    Molecule(
        "H2O",
        "水",
        (
            MoleculeAtom("O", 0, 0),
            MoleculeAtom("H", -28, 22),
            MoleculeAtom("H", 28, 22),
        ),
        ((0, 1, 1), (0, 2, 1)),
        "V 形结构，键角约 105°",
    ),
    Molecule(
        "CO2",
        "二氧化碳",
        (
            MoleculeAtom("C", 0, 0),
            MoleculeAtom("O", -46, 0),
            MoleculeAtom("O", 46, 0),
        ),
        ((0, 1, 2), (0, 2, 2)),
        "直线形结构",
    ),
    Molecule(
        "CH4",
        "甲烷",
        (
            MoleculeAtom("C", 0, 0),
            MoleculeAtom("H", 0, -40),
            MoleculeAtom("H", -40, 14),
            MoleculeAtom("H", 40, 14),
            MoleculeAtom("H", 0, 38),
        ),
        ((0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)),
        "正四面体结构，此处为平面示意",
    ),
    Molecule(
        "NH3",
        "氨气",
        (
            MoleculeAtom("N", 0, 0),
            MoleculeAtom("H", -34, 22),
            MoleculeAtom("H", 34, 22),
            MoleculeAtom("H", 0, -36),
        ),
        ((0, 1, 1), (0, 2, 1), (0, 3, 1)),
        "三角锥形结构",
    ),
    Molecule(
        "HCl",
        "氯化氢",
        (MoleculeAtom("H", -30, 0), MoleculeAtom("Cl", 30, 0)),
        ((0, 1, 1),),
    ),
    Molecule(
        "NaCl",
        "氯化钠",
        (MoleculeAtom("Na", -34, 0), MoleculeAtom("Cl", 34, 0)),
        (),
        "离子化合物，由 Na⁺ 和 Cl⁻ 构成",
        ((0, "+"), (1, "-")),
    ),
)

PAGE_CSS = """
  @page { size: A4 landscape; margin: 10mm; }
  * { box-sizing: border-box; }
  body {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    color: #202124;
    margin: 0;
    padding: 12mm;
    background: #f7f8fa;
  }
  h1 { font-size: 24px; margin: 0 0 4px; }
  .subtitle { color: #5f6368; font-size: 13px; margin: 0 0 20px; }
  h2 { font-size: 17px; margin: 26px 0 10px; border-left: 4px solid #1a73e8; padding-left: 8px; }
  .ptable {
    display: grid;
    grid-template-columns: repeat(18, minmax(0, 1fr));
    gap: 4px;
    min-width: 780px;
  }
  .pcell {
    border-radius: 4px;
    border: 1px solid #d0d5dd;
    padding: 4px 2px;
    display: flex;
    flex-direction: column;
    align-items: center;
    line-height: 1.15;
    min-height: 56px;
    justify-content: center;
  }
  .pcell.metal { background: #fde7c8; }
  .pcell.nonmetal { background: #dcefdc; }
  .pcell.noble { background: #dbe6f5; }
  .pcell .z { font-size: 9px; color: #5f6368; align-self: flex-start; padding-left: 3px; }
  .pcell .sym { font-size: 16px; font-weight: 700; }
  .pcell .nm { font-size: 10px; }
  .pcell .mass { font-size: 9px; color: #5f6368; }
  .legend { margin-top: 10px; font-size: 12px; color: #5f6368; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin: 0 4px 0 12px; vertical-align: middle; }
  .extra-grid, .atom-grid, .molecule-grid { display: flex; flex-wrap: wrap; gap: 10px; }
  .extra-card {
    width: 86px; border-radius: 6px; border: 1px solid #d0d5dd; background: #fde7c8;
    padding: 6px; text-align: center; line-height: 1.2;
  }
  .extra-card .sym { display: block; font-size: 18px; font-weight: 700; }
  .extra-card .nm { display: block; font-size: 12px; }
  .extra-card .mass { display: block; font-size: 10px; color: #5f6368; }
  .atom-card {
    width: 170px; background: #fff; border: 1px solid #e0e3e8; border-radius: 8px;
    padding: 6px; text-align: center;
  }
  .atom-card .caption { font-size: 12px; color: #3c4043; margin-top: 2px; }
  .molecule-card {
    width: 250px; background: #fff; border: 1px solid #e0e3e8; border-radius: 8px;
    padding: 8px 8px 10px; text-align: center;
  }
  .molecule-card .name { font-size: 14px; font-weight: 600; margin-top: 2px; }
  .molecule-card .formula { font-size: 12px; color: #5f6368; }
  .molecule-card .note { font-size: 11px; color: #80868b; margin-top: 4px; min-height: 14px; }
  .usage {
    background: #fff; border: 1px solid #e0e3e8; border-radius: 8px;
    padding: 12px 16px; font-size: 13px; line-height: 1.9;
  }
  code { background: #eef1f5; border-radius: 3px; padding: 1px 5px; font-size: 12px; }
  .note { color: #5f6368; font-size: 12px; line-height: 1.8; margin-top: 18px; }
  @media print {
    body { background: #fff; padding: 0; }
    .atom-card, .molecule-card, .usage { break-inside: avoid; }
  }
"""


def render_atom_svg(element: Element, size: int = 160) -> str:
    """画原子结构示意图：原子核 + 各层电子。"""
    if not element.shells:
        raise ElementError("元素「%s」暂无原子结构示意图" % element.name)

    center = 100.0
    radii = (30.0, 48.0, 66.0, 84.0)
    if len(element.shells) > len(radii):
        raise ElementError("元素「%s」的电子层数超出绘图范围" % element.name)

    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 200 200" role="img" aria-label="%s原子结构示意图">'
        % (size, size, html.escape(element.name)),
        '<circle cx="100" cy="100" r="15" fill="#f2a33c"/>',
        '<text x="100" y="105" text-anchor="middle" font-size="12" '
        'font-family="sans-serif" fill="#202124">+%d</text>' % element.z,
    ]
    for shell_index, count in enumerate(element.shells):
        radius = radii[shell_index]
        parts.append(
            '<circle cx="100" cy="100" r="%.0f" fill="none" stroke="#9aa0a6" '
            'stroke-width="1"/>' % radius
        )
        for electron in range(count):
            angle = -math.pi / 2 + 2 * math.pi * electron / count
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            parts.append(
                '<circle cx="%.1f" cy="%.1f" r="3.2" fill="#1a73e8"/>' % (x, y)
            )
    parts.append("</svg>")
    return "".join(parts)


def render_molecule_svg(molecule: Molecule) -> str:
    """画常见分子的球棍模型或离子示意图。"""
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="220" height="150" '
        'viewBox="0 0 200 140" role="img" aria-label="%s分子模型">'
        % html.escape(molecule.name),
        '<g transform="translate(100,70)">',
    ]
    atom_map = {index: atom for index, atom in enumerate(molecule.atoms)}

    if molecule.bonds:
        for first, second, order in molecule.bonds:
            a = atom_map[first]
            b = atom_map[second]
            dx = b.x - a.x
            dy = b.y - a.y
            length = math.hypot(dx, dy) or 1.0
            offset_x = -dy / length
            offset_y = dx / length
            offsets = (0.0,) if order == 1 else (
                (-2.6, 2.6) if order == 2 else (-4.6, 0.0, 4.6)
            )
            for shift in offsets:
                parts.append(
                    '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                    'stroke="#5f6368" stroke-width="2.4"/>'
                    % (
                        a.x + offset_x * shift,
                        a.y + offset_y * shift,
                        b.x + offset_x * shift,
                        b.y + offset_y * shift,
                    )
                )
    else:
        a = molecule.atoms[0]
        b = molecule.atoms[1]
        parts.append(
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
            'stroke="#9aa0a6" stroke-width="2" stroke-dasharray="5 4"/>'
            % (a.x, a.y, b.x, b.y)
        )

    charge_map = dict(molecule.charges)
    for index, atom in enumerate(molecule.atoms):
        radius = ATOM_RADII.get(atom.element, 12)
        fill = ATOM_COLORS.get(atom.element, "#9aa0a6")
        text_color = "#202124" if atom.element == "H" else "#ffffff"
        parts.append(
            '<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" stroke="#5f6368" '
            'stroke-width="1.2"/>'
            % (atom.x, atom.y, radius, fill)
        )
        parts.append(
            '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%d" '
            'font-family="sans-serif" fill="%s">%s</text>'
            % (
                atom.x,
                atom.y + 4,
                11 if atom.element == "H" else 13,
                text_color,
                html.escape(atom.element),
            )
        )
        if index in charge_map:
            parts.append(
                '<text x="%.1f" y="%.1f" text-anchor="middle" font-size="13" '
                'font-family="sans-serif" fill="#202124">%s</text>'
                % (
                    atom.x + radius * 0.8,
                    atom.y - radius * 0.7,
                    html.escape(charge_map[index]),
                )
            )

    parts.append("</g></svg>")
    return "".join(parts)


def render_periodic_table() -> str:
    """生成元素周期表区块。"""
    from .elements import POSITIONS

    cells: List[str] = []
    for element in periodic_elements():
        row, column = POSITIONS[element.symbol]
        category = CATEGORY_CLASS.get(element.category, "nonmetal")
        cells.append(
            '<div class="pcell %s" style="grid-row:%d;grid-column:%d">'
            '<span class="z">%d</span>'
            '<span class="sym">%s</span>'
            '<span class="nm">%s</span>'
            '<span class="mass">%s</span>'
            "</div>"
            % (
                category,
                row,
                column,
                element.z,
                html.escape(element.symbol),
                html.escape(element.name),
                _format(element.mass),
            )
        )

    extra_cards = "".join(
        '<div class="extra-card">'
        '<span class="sym">%s</span>'
        '<span class="nm">%s</span>'
        '<span class="mass">%s</span>'
        "</div>"
        % (
            html.escape(element.symbol),
            html.escape(element.name),
            _format(element.mass),
        )
        for element in extra_elements()
    )

    return (
        '<div class="ptable">%s</div>'
        '<p class="legend">'
        '<span class="dot" style="background:#fde7c8"></span>金属元素'
        '<span class="dot" style="background:#dcefdc"></span>非金属元素'
        '<span class="dot" style="background:#dbe6f5"></span>稀有气体元素'
        "</p>"
        "<h2>初中常见元素</h2>"
        '<div class="extra-grid">%s</div>' % ("".join(cells), extra_cards)
    )


def render_atom_gallery() -> str:
    cards: List[str] = []
    for element in periodic_elements():
        cards.append(
            '<div class="atom-card">%s<div class="caption">%s %s（+%d）</div></div>'
            % (
                render_atom_svg(element),
                html.escape(element.symbol),
                html.escape(element.name),
                element.z,
            )
        )
    return '<div class="atom-grid">%s</div>' % "".join(cards)


def render_molecule_gallery() -> str:
    cards: List[str] = []
    for molecule in MOLECULES:
        cards.append(
            '<div class="molecule-card">%s'
            '<div class="name">%s</div>'
            '<div class="formula">%s</div>'
            '<div class="note">%s</div>'
            "</div>"
            % (
                render_molecule_svg(molecule),
                html.escape(molecule.name),
                html.escape(molecule.formula),
                html.escape(molecule.note),
            )
        )
    return '<div class="molecule-grid">%s</div>' % "".join(cards)


def render_page(title: str = "初中化学可视化") -> str:
    """生成完整的单文件 HTML。"""
    body = (
        "<h1>%s</h1>"
        '<p class="subtitle">元素周期表 · 原子结构 · 常见分子模型 · 全部数据在本地生成，不联网</p>'
        "<h2>元素周期表（前 20 号元素）</h2>"
        "%s"
        "<h2>原子结构示意图</h2>"
        "%s"
        "<h2>常见分子模型</h2>"
        "%s"
        "<h2>命令行用法</h2>"
        '<div class="usage">'
        "<div><code>chemviz html -o 化学可视化.html</code> 生成这个页面</div>"
        "<div><code>chemviz element Na</code> 查看元素资料</div>"
        "<div><code>chemviz atom 11</code> 查看原子结构</div>"
        "<div><code>chemviz mass Ca(OH)2</code> 计算相对分子质量</div>"
        '<div><code>chemviz balance "Fe + O2 = Fe3O4"</code> 自动配平</div>'
        "</div>"
        '<p class="note">相对原子质量采用初中教材常用值（如 Cl 取 35.5）。'
        "原子结构示意图只覆盖前 20 号元素；分子模型用于理解原子连接方式，"
        "不表示真实键长与空间比例。</p>"
        % (
            html.escape(title),
            render_periodic_table(),
            render_atom_gallery(),
            render_molecule_gallery(),
        )
    )
    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n</body>\n</html>\n"
        % (html.escape(title), PAGE_CSS, body)
    )


def _format(value: float) -> str:
    text = "%.1f" % value
    return text[:-2] if text.endswith(".0") else text


__all__ = [
    "MOLECULES",
    "Molecule",
    "MoleculeAtom",
    "render_atom_gallery",
    "render_atom_svg",
    "render_molecule_gallery",
    "render_molecule_svg",
    "render_page",
    "render_periodic_table",
]
