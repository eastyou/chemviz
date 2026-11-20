"""化学方程式配平。

把方程式看成线性方程组：每种元素的原子个数在等号两边相等。
用分数做高斯消元求零空间，再化成最小正整数系数。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

from .formula import FormulaError, parse_formula

SEPARATORS = ("->", "→", "=")


class BalanceError(ValueError):
    """方程式无法解析或配平。"""


@dataclass(frozen=True)
class BalancedEquation:
    """配平后的方程式。"""

    reactants: Tuple[Tuple[int, str], ...]
    products: Tuple[Tuple[int, str], ...]

    def text(self) -> str:
        return "%s = %s" % (
            " + ".join(_term(coefficient, formula) for coefficient, formula in self.reactants),
            " + ".join(_term(coefficient, formula) for coefficient, formula in self.products),
        )


def balance_equation(equation: str) -> BalancedEquation:
    """配平形如 ``Fe + O2 = Fe3O4`` 的方程式。"""
    reactants, products = _split_equation(equation)
    species = reactants + products

    elements: List[str] = []
    for formula in species:
        for symbol in parse_formula(formula):
            if symbol not in elements:
                elements.append(symbol)

    matrix: List[List[Fraction]] = []
    for symbol in elements:
        row: List[Fraction] = []
        for formula in reactants:
            row.append(Fraction(parse_formula(formula).get(symbol, 0)))
        for formula in products:
            row.append(Fraction(-parse_formula(formula).get(symbol, 0)))
        matrix.append(row)

    basis = _null_space(matrix)
    if not basis:
        raise BalanceError("这个方程式无法配平，请检查反应物和生成物")
    if len(basis) > 1:
        raise BalanceError("这个方程式有多种配平方式，暂不支持自动配平")

    vector = basis[0]
    if all(value == 0 for value in vector):
        raise BalanceError("这个方程式无法配平")
    if all(value <= 0 for value in vector):
        vector = [-value for value in vector]
    if any(value < 0 for value in vector):
        raise BalanceError("这个方程式无法配平")
    if any(value == 0 for value in vector):
        raise BalanceError("有一种物质不需要参与反应，请检查方程式")

    coefficients = _to_integers(vector)
    split = len(reactants)
    return BalancedEquation(
        reactants=tuple(zip(coefficients[:split], reactants)),
        products=tuple(zip(coefficients[split:], products)),
    )


def _split_equation(equation: str) -> Tuple[List[str], List[str]]:
    text = equation.strip()
    if not text:
        raise BalanceError("方程式不能为空")

    counts = [(separator, text.count(separator)) for separator in SEPARATORS]
    total = sum(count for _, count in counts)
    if total != 1:
        raise BalanceError("方程式需要用「=」或「->」连接反应物和生成物")
    separator = next(separator for separator, count in counts if count)
    left, right = text.split(separator)
    if not left.strip() or not right.strip():
        raise BalanceError("方程式等号两边都不能为空")

    reactants = _split_terms(left)
    products = _split_terms(right)
    if not reactants or not products:
        raise BalanceError("方程式等号两边都需要有物质")
    return reactants, products


def _split_terms(side: str) -> List[str]:
    terms: List[str] = []
    for raw in side.split("+"):
        term = raw.strip()
        if not term:
            raise BalanceError("方程式里有空的物质项，请检查加号位置")
        if term[0].isdigit():
            raise BalanceError("不需要手动写系数，工具会自动配平: %s" % term)
        try:
            parse_formula(term)
        except FormulaError as exc:
            raise BalanceError("无法解析物质「%s」：%s" % (term, exc)) from None
        terms.append(term)
    return terms


def _null_space(matrix: Sequence[Sequence[Fraction]]) -> List[List[Fraction]]:
    rows = [list(row) for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0]) if row_count else 0
    pivot_columns: List[int] = []
    pivot_row = 0
    for column in range(column_count):
        target = None
        for index in range(pivot_row, row_count):
            if rows[index][column] != 0:
                target = index
                break
        if target is None:
            continue
        rows[pivot_row], rows[target] = rows[target], rows[pivot_row]
        pivot = rows[pivot_row][column]
        rows[pivot_row] = [value / pivot for value in rows[pivot_row]]
        for index in range(row_count):
            if index == pivot_row:
                continue
            factor = rows[index][column]
            if factor != 0:
                rows[index] = [
                    value - factor * base
                    for value, base in zip(rows[index], rows[pivot_row])
                ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break

    free_columns = [
        column for column in range(column_count) if column not in pivot_columns
    ]
    basis: List[List[Fraction]] = []
    for free in free_columns:
        vector = [Fraction(0) for _ in range(column_count)]
        vector[free] = Fraction(1)
        for index, column in enumerate(pivot_columns):
            vector[column] = -rows[index][free]
        basis.append(vector)
    return basis


def _to_integers(vector: Sequence[Fraction]) -> List[int]:
    denominator = 1
    for value in vector:
        denominator = denominator * value.denominator // math.gcd(
            denominator, value.denominator
        )
    integers = [int(value * denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    if divisor == 0:
        raise BalanceError("这个方程式无法配平")
    return [value // divisor for value in integers]


def _term(coefficient: int, formula: str) -> str:
    return formula if coefficient == 1 else "%d%s" % (coefficient, formula)


__all__ = ["BalanceError", "BalancedEquation", "balance_equation"]
