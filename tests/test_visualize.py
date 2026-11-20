from __future__ import annotations

import unittest

from chemviz.elements import get_element
from chemviz.visualize import (
    ATOM_RADII,
    MOLECULES,
    render_atom_svg,
    render_molecule_svg,
    render_page,
)


class AtomSvgTest(unittest.TestCase):
    def test_sodium_has_eleven_electrons(self) -> None:
        svg = render_atom_svg(get_element("Na"))
        self.assertIn("+11", svg)
        self.assertEqual(svg.count('fill="#1a73e8"'), 11)
        self.assertEqual(svg.count("<circle"), 15)  # 原子核 + 3 层 + 11 个电子

    def test_hydrogen(self) -> None:
        svg = render_atom_svg(get_element("H"))
        self.assertEqual(svg.count('fill="#1a73e8"'), 1)
        self.assertTrue(svg.startswith("<svg"))

    def test_element_without_shells(self) -> None:
        with self.assertRaises(Exception):
            render_atom_svg(get_element("Fe"))


class MoleculeSvgTest(unittest.TestCase):
    def test_all_bonds_reference_existing_atoms(self) -> None:
        for molecule in MOLECULES:
            for first, second, order in molecule.bonds:
                self.assertLess(first, len(molecule.atoms))
                self.assertLess(second, len(molecule.atoms))
                self.assertIn(order, (1, 2, 3))
            for atom in molecule.atoms:
                self.assertIn(atom.element, ATOM_RADII)

    def test_water(self) -> None:
        water = next(item for item in MOLECULES if item.formula == "H2O")
        svg = render_molecule_svg(water)
        self.assertEqual(svg.count("<circle"), 3)
        self.assertEqual(svg.count("<line"), 2)

    def test_double_bond_draws_four_lines(self) -> None:
        carbon_dioxide = next(item for item in MOLECULES if item.formula == "CO2")
        svg = render_molecule_svg(carbon_dioxide)
        self.assertEqual(svg.count("<line"), 4)

    def test_ionic_compound_uses_dashed_line(self) -> None:
        salt = next(item for item in MOLECULES if item.formula == "NaCl")
        svg = render_molecule_svg(salt)
        self.assertIn("stroke-dasharray", svg)
        self.assertIn("+", svg)
        self.assertIn("-", svg)


class PageTest(unittest.TestCase):
    def test_sections_present(self) -> None:
        page = render_page("化学可视化")
        self.assertIn("元素周期表（前 20 号元素）", page)
        self.assertIn("原子结构示意图", page)
        self.assertIn("常见分子模型", page)
        self.assertIn("chemviz balance", page)
        self.assertIn("化学可视化", page)
        self.assertEqual(page.count('class="atom-card"'), 20)
        self.assertEqual(page.count('class="molecule-card"'), len(MOLECULES))

    def test_title_escaped(self) -> None:
        page = render_page("<script>x</script>")
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_standalone_html(self) -> None:
        page = render_page()
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn("<style>", page)
        self.assertNotIn("<link", page)
        self.assertNotIn("<script src", page)


if __name__ == "__main__":
    unittest.main()
