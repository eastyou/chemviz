from __future__ import annotations

import unittest

from chemviz.balance import BalanceError, balance_equation


class BalanceTest(unittest.TestCase):
    def test_water(self) -> None:
        result = balance_equation("H2 + O2 = H2O")
        self.assertEqual(result.text(), "2H2 + O2 = 2H2O")

    def test_magnetite(self) -> None:
        result = balance_equation("Fe + O2 = Fe3O4")
        self.assertEqual(result.text(), "3Fe + 2O2 = Fe3O4")

    def test_methane(self) -> None:
        result = balance_equation("CH4 + O2 = CO2 + H2O")
        self.assertEqual(result.text(), "CH4 + 2O2 = CO2 + 2H2O")

    def test_already_balanced(self) -> None:
        result = balance_equation("NaOH + HCl = NaCl + H2O")
        self.assertEqual(result.text(), "NaOH + HCl = NaCl + H2O")

    def test_three_products(self) -> None:
        result = balance_equation("Na2CO3 + HCl = NaCl + H2O + CO2")
        self.assertEqual(
            result.text(), "Na2CO3 + 2HCl = 2NaCl + H2O + CO2"
        )

    def test_arrow_separator(self) -> None:
        result = balance_equation("Ca(OH)2 + CO2 -> CaCO3 + H2O")
        self.assertEqual(
            result.text(), "Ca(OH)2 + CO2 = CaCO3 + H2O"
        )

    def test_unicode_arrow(self) -> None:
        result = balance_equation("H2 + Cl2 → HCl")
        self.assertEqual(result.text(), "H2 + Cl2 = 2HCl")

    def test_empty(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("")

    def test_missing_separator(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + O2")

    def test_two_separators(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + O2 = H2O = H2O")

    def test_empty_side(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + O2 =")

    def test_coefficient_rejected(self) -> None:
        with self.assertRaises(BalanceError) as ctx:
            balance_equation("2H2 + O2 = 2H2O")
        self.assertIn("不需要手动写系数", str(ctx.exception))

    def test_unknown_substance(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + Xx = H2Xx")

    def test_impossible(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + O2 = Fe2O3")

    def test_unused_substance(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + O2 + Fe = H2O")

    def test_ambiguous(self) -> None:
        with self.assertRaises(BalanceError) as ctx:
            balance_equation("H2 + O2 = H2O + H2O2")
        self.assertIn("多种配平", str(ctx.exception))

    def test_repeated_substance_is_ambiguous(self) -> None:
        with self.assertRaises(BalanceError):
            balance_equation("H2 + H2 + O2 = H2O")


if __name__ == "__main__":
    unittest.main()
