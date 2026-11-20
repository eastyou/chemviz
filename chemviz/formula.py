"""化学式解析与相对分子质量计算。"""

from __future__ import annotations

from typing import Dict, Tuple

from .elements import BY_SYMBOL

MAX_DEPTH = 12


class FormulaError(ValueError):
    """化学式不合法。"""


def parse_formula(formula: str) -> Dict[str, int]:
    """解析化学式，返回各元素原子个数。

    支持元素符号、下标数字和括号，例如 ``H2O``、``Ca(OH)2``、
    ``Fe2(SO4)3``。
    """
    text = formula.strip()
    if not text:
        raise FormulaError("化学式不能为空")
    if any(character.isspace() for character in text):
        raise FormulaError("化学式中不能包含空格: %s" % formula)

    counts, index = _parse_block(text, 0, 0)
    if index != len(text):
        raise FormulaError("化学式括号不匹配: %s" % formula)
    if not counts:
        raise FormulaError("化学式中没有任何元素: %s" % formula)
    return counts


def molar_mass(formula: str) -> float:
    """计算相对分子质量。"""
    counts = parse_formula(formula)
    return sum(BY_SYMBOL[symbol].mass * count for symbol, count in counts.items())


def format_mass(value: float) -> str:
    """按初中习惯输出质量：整数不带小数点，半整数保留一位。"""
    text = "%.1f" % value
    if text.endswith(".0"):
        return text[:-2]
    return text


def composition_text(counts: Dict[str, int]) -> str:
    """把元素组成整理成「H:2、O:1」这样的文本。"""
    return "、".join(
        "%s:%d" % (symbol, count) for symbol, count in sorted(counts.items())
    )


def _parse_block(
    text: str, index: int, depth: int
) -> Tuple[Dict[str, int], int]:
    if depth > MAX_DEPTH:
        raise FormulaError("化学式括号嵌套过深")
    counts: Dict[str, int] = {}
    while index < len(text) and text[index] != ")":
        character = text[index]
        if character == "(":
            inner, index = _parse_block(text, index + 1, depth + 1)
            if index >= len(text) or text[index] != ")":
                raise FormulaError("化学式缺少右括号: %s" % text)
            index += 1
            if not inner:
                raise FormulaError("括号里没有元素: %s" % text)
            multiplier, index = _read_multiplier(text, index)
            for symbol, count in inner.items():
                counts[symbol] = counts.get(symbol, 0) + count * multiplier
        elif character.isupper():
            symbol = character
            index += 1
            if index < len(text) and text[index].islower():
                symbol += text[index]
                index += 1
            if symbol not in BY_SYMBOL:
                raise FormulaError(
                    "未收录元素符号「%s」，请检查化学式: %s" % (symbol, text)
                )
            multiplier, index = _read_multiplier(text, index)
            counts[symbol] = counts.get(symbol, 0) + multiplier
        else:
            raise FormulaError(
                "化学式中无法识别的字符「%s」: %s" % (character, text)
            )
    return counts, index


def _read_multiplier(text: str, index: int) -> Tuple[int, int]:
    start = index
    while index < len(text) and text[index].isdigit():
        index += 1
    if start == index:
        return 1, index
    value = int(text[start:index])
    if value <= 0:
        raise FormulaError("化学式下标必须是正整数: %s" % text)
    return value, index


__all__ = [
    "FormulaError",
    "composition_text",
    "format_mass",
    "molar_mass",
    "parse_formula",
]
