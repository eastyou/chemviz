from __future__ import annotations

import unittest

from chemviz.formula import (
    FormulaError,
    format_mass,
    molar_mass,
    parse_formula,
)


class ParseFormulaTest(unittest.TestCase):
    def test_simple(self) -> None:
        self.assertEqual(parse_formula("H2O"), {"H": 2, "O": 1})

    def test_no_subscript(self) -> None:
        self.assertEqual(parse_formula("NaCl"), {"Na": 1, "Cl": 1})

    def test_parentheses(self) -> None:
        self.assertEqual(parse_formula("Ca(OH)2"), {"Ca": 1, "O": 2, "H": 2})

    def test_nested_parentheses(self) -> None:
        self.assertEqual(
            parse_formula("Fe2(SO4)3"),
            {"Fe": 2, "S": 3, "O": 12},
        )

    def test_whitespace_stripped(self) -> None:
        self.assertEqual(parse_formula("  CO2  "), {"C": 1, "O": 2})

    def test_empty(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("")

    def test_inner_space_rejected(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("H2 O")

    def test_unknown_element(self) -> None:
        with self.assertRaises(FormulaError) as ctx:
            parse_formula("Xx2O")
        self.assertIn("未收录", str(ctx.exception))

    def test_unbalanced_parentheses(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("Ca(OH2")
        with self.assertRaises(FormulaError):
            parse_formula("Ca(OH)2)")

    def test_empty_parentheses(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("Ca()2")

    def test_zero_subscript(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("H0O")

    def test_coefficient_not_allowed(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("2H2O")

    def test_invalid_character(self) -> None:
        with self.assertRaises(FormulaError):
            parse_formula("H2O#")


class MolarMassTest(unittest.TestCase):
    def test_water(self) -> None:
        self.assertAlmostEqual(molar_mass("H2O"), 18.0)

    def test_calcium_hydroxide(self) -> None:
        self.assertAlmostEqual(molar_mass("Ca(OH)2"), 74.0)

    def test_iron_sulfate(self) -> None:
        self.assertAlmostEqual(molar_mass("Fe2(SO4)3"), 400.0)

    def test_chlorine(self) -> None:
        self.assertAlmostEqual(molar_mass("Cl2"), 71.0)

    def test_format(self) -> None:
        self.assertEqual(format_mass(18.0), "18")
        self.assertEqual(format_mass(35.5), "35.5")
        self.assertEqual(format_mass(74.0), "74")


if __name__ == "__main__":
    unittest.main()
