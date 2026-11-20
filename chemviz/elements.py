"""初中化学常用元素数据。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

METAL = "金属"
NONMETAL = "非金属"
NOBLE = "稀有气体"


class ElementError(ValueError):
    """元素数据查询失败。"""


@dataclass(frozen=True)
class Element:
    """一种元素。``shells`` 为各层电子数，仅前 20 号元素提供。"""

    z: int
    symbol: str
    name: str
    mass: float
    category: str
    shells: Optional[Tuple[int, ...]] = None


ELEMENTS: Tuple[Element, ...] = (
    Element(1, "H", "氢", 1.0, NONMETAL, (1,)),
    Element(2, "He", "氦", 4.0, NOBLE, (2,)),
    Element(3, "Li", "锂", 7.0, METAL, (2, 1)),
    Element(4, "Be", "铍", 9.0, METAL, (2, 2)),
    Element(5, "B", "硼", 11.0, NONMETAL, (2, 3)),
    Element(6, "C", "碳", 12.0, NONMETAL, (2, 4)),
    Element(7, "N", "氮", 14.0, NONMETAL, (2, 5)),
    Element(8, "O", "氧", 16.0, NONMETAL, (2, 6)),
    Element(9, "F", "氟", 19.0, NONMETAL, (2, 7)),
    Element(10, "Ne", "氖", 20.0, NOBLE, (2, 8)),
    Element(11, "Na", "钠", 23.0, METAL, (2, 8, 1)),
    Element(12, "Mg", "镁", 24.0, METAL, (2, 8, 2)),
    Element(13, "Al", "铝", 27.0, METAL, (2, 8, 3)),
    Element(14, "Si", "硅", 28.0, NONMETAL, (2, 8, 4)),
    Element(15, "P", "磷", 31.0, NONMETAL, (2, 8, 5)),
    Element(16, "S", "硫", 32.0, NONMETAL, (2, 8, 6)),
    Element(17, "Cl", "氯", 35.5, NONMETAL, (2, 8, 7)),
    Element(18, "Ar", "氩", 40.0, NOBLE, (2, 8, 8)),
    Element(19, "K", "钾", 39.0, METAL, (2, 8, 8, 1)),
    Element(20, "Ca", "钙", 40.0, METAL, (2, 8, 8, 2)),
    Element(25, "Mn", "锰", 55.0, METAL),
    Element(26, "Fe", "铁", 56.0, METAL),
    Element(29, "Cu", "铜", 64.0, METAL),
    Element(30, "Zn", "锌", 65.0, METAL),
    Element(47, "Ag", "银", 108.0, METAL),
    Element(53, "I", "碘", 127.0, NONMETAL),
    Element(56, "Ba", "钡", 137.0, METAL),
    Element(80, "Hg", "汞", 201.0, METAL),
)

BY_SYMBOL: Dict[str, Element] = {item.symbol: item for item in ELEMENTS}
BY_Z: Dict[int, Element] = {item.z: item for item in ELEMENTS}

# 周期表中前 20 号元素的位置：(周期, 族)
POSITIONS: Dict[str, Tuple[int, int]] = {
    "H": (1, 1),
    "He": (1, 18),
    "Li": (2, 1),
    "Be": (2, 2),
    "B": (2, 13),
    "C": (2, 14),
    "N": (2, 15),
    "O": (2, 16),
    "F": (2, 17),
    "Ne": (2, 18),
    "Na": (3, 1),
    "Mg": (3, 2),
    "Al": (3, 13),
    "Si": (3, 14),
    "P": (3, 15),
    "S": (3, 16),
    "Cl": (3, 17),
    "Ar": (3, 18),
    "K": (4, 1),
    "Ca": (4, 2),
}

EXTRA_SYMBOLS: Tuple[str, ...] = ("Mn", "Fe", "Cu", "Zn", "Ag", "I", "Ba", "Hg")


def get_element(symbol_or_z: str) -> Element:
    """按元素符号或原子序数查询元素。"""
    text = symbol_or_z.strip()
    if not text:
        raise ElementError("元素符号不能为空")
    if text.isdigit():
        element = BY_Z.get(int(text))
        if element is None:
            raise ElementError("暂无原子序数 %s 的数据" % text)
        return element
    normalized = text[0].upper() + text[1:].lower()
    element = BY_SYMBOL.get(normalized)
    if element is None:
        raise ElementError(
            "未收录元素「%s」，可用元素：%s"
            % (text, "、".join(item.symbol for item in ELEMENTS))
        )
    return element


def periodic_elements() -> List[Element]:
    """按原子序数返回周期表中的前 20 号元素。"""
    return [item for item in ELEMENTS if item.symbol in POSITIONS]


def extra_elements() -> List[Element]:
    """返回初中化学常见但不在前 20 号的元素。"""
    return [BY_SYMBOL[symbol] for symbol in EXTRA_SYMBOLS]


__all__ = [
    "BY_SYMBOL",
    "BY_Z",
    "ELEMENTS",
    "EXTRA_SYMBOLS",
    "Element",
    "ElementError",
    "METAL",
    "NONMETAL",
    "NOBLE",
    "POSITIONS",
    "extra_elements",
    "get_element",
    "periodic_elements",
]
