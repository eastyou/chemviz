"""命令行入口：元素查询、化学式计算、方程式配平与可视化页面。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .balance import BalanceError, balance_equation
from .elements import ElementError, get_element
from .formula import FormulaError, composition_text, format_mass, molar_mass, parse_formula
from .visualize import render_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chemviz",
        description="初中化学可视化：元素周期表、原子结构、分子模型、化学式与方程式配平",
    )
    parser.add_argument("--version", action="version", version="chemviz 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    html_parser = subparsers.add_parser("html", help="生成可视化页面")
    html_parser.add_argument(
        "-o", "--output", default="chemviz.html", help="输出 HTML 路径"
    )
    html_parser.add_argument("--title", default="初中化学可视化", help="页面标题")

    element_parser = subparsers.add_parser("element", help="查看元素资料")
    element_parser.add_argument("symbol", help="元素符号或原子序数，例如 Na 或 11")

    atom_parser = subparsers.add_parser("atom", help="查看原子结构示意图信息")
    atom_parser.add_argument("symbol", help="元素符号或原子序数，例如 Na 或 11")

    mass_parser = subparsers.add_parser("mass", help="计算相对分子质量")
    mass_parser.add_argument("formula", help="化学式，例如 Ca(OH)2")

    balance_parser = subparsers.add_parser("balance", help="配平化学方程式")
    balance_parser.add_argument(
        "equation",
        nargs="+",
        help='方程式，例如 "Fe + O2 = Fe3O4"',
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "html":
            return _run_html(args)
        if args.command == "element":
            return _run_element(args.symbol)
        if args.command == "atom":
            return _run_atom(args.symbol)
        if args.command == "mass":
            return _run_mass(args.formula)
        if args.command == "balance":
            return _run_balance(" ".join(args.equation))
    except (ElementError, FormulaError, BalanceError) as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2
    return 2


def _run_html(args: argparse.Namespace) -> int:
    if not args.title.strip():
        print("错误: 页面标题不能为空", file=sys.stderr)
        return 2
    page = render_page(args.title)
    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1
    print("已生成 %s" % args.output)
    return 0


def _run_element(symbol: str) -> int:
    element = get_element(symbol)
    print(
        "%s %s：原子序数 %d，相对原子质量 %s，%s元素"
        % (
            element.symbol,
            element.name,
            element.z,
            format_mass(element.mass),
            element.category,
        )
    )
    if element.shells:
        print("电子排布：" + "、".join(str(count) for count in element.shells))
    return 0


def _run_atom(symbol: str) -> int:
    element = get_element(symbol)
    if not element.shells:
        raise ElementError(
            "元素「%s」暂无原子结构示意图，目前只提供前 20 号元素" % element.name
        )
    print(
        "%s %s 的原子结构：核电荷数 +%d，各层电子数 %s"
        % (
            element.symbol,
            element.name,
            element.z,
            "、".join(str(count) for count in element.shells),
        )
    )
    return 0


def _run_mass(formula: str) -> int:
    counts = parse_formula(formula)
    mass = molar_mass(formula)
    print("%s 的相对分子质量 = %s" % (formula.strip(), format_mass(mass)))
    print("元素组成：" + composition_text(counts))
    return 0


def _run_balance(equation: str) -> int:
    result = balance_equation(equation)
    print(result.text())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
