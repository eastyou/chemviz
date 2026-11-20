from __future__ import annotations

import unittest

from chemviz.elements import (
    ELEMENTS,
    ElementError,
    extra_elements,
    get_element,
    periodic_elements,
)


class ElementsTest(unittest.TestCase):
    def test_symbols_unique(self) -> None:
        symbols = [item.symbol for item in ELEMENTS]
        self.assertEqual(len(symbols), len(set(symbols)))
        numbers = [item.z for item in ELEMENTS]
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_masses_positive(self) -> None:
        for element in ELEMENTS:
            self.assertGreater(element.mass, 0)
            self.assertGreater(element.z, 0)

    def test_shells_add_up_for_first_twenty(self) -> None:
        for element in periodic_elements():
            self.assertIsNotNone(element.shells)
            assert element.shells is not None
            self.assertEqual(sum(element.shells), element.z)
            self.assertLessEqual(len(element.shells), 4)
            self.assertEqual(element.shells[-1] <= 8, True)

    def test_periodic_and_extra_counts(self) -> None:
        self.assertEqual(len(periodic_elements()), 20)
        self.assertEqual(len(extra_elements()), 8)

    def test_lookup_by_symbol(self) -> None:
        self.assertEqual(get_element("Na").name, "钠")
        self.assertEqual(get_element("na").z, 11)
        self.assertEqual(get_element("CL").symbol, "Cl")

    def test_lookup_by_number(self) -> None:
        self.assertEqual(get_element("8").symbol, "O")
        with self.assertRaises(ElementError):
            get_element("99")

    def test_unknown_symbol(self) -> None:
        with self.assertRaises(ElementError) as ctx:
            get_element("Xx")
        self.assertIn("未收录", str(ctx.exception))

    def test_empty_symbol(self) -> None:
        with self.assertRaises(ElementError):
            get_element("   ")

    def test_chlorine_mass_is_half_integer(self) -> None:
        self.assertEqual(get_element("Cl").mass, 35.5)


if __name__ == "__main__":
    unittest.main()
