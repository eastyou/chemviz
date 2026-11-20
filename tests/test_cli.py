from __future__ import annotations

import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from chemviz.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.output = os.path.join(self._tmp.name, "chemviz.html")

    def run_cli(self, args):
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_html(self) -> None:
        code, output, _ = self.run_cli(["html", "-o", self.output])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(self.output))
        self.assertIn("已生成", output)
        with open(self.output, encoding="utf-8") as handle:
            content = handle.read()
        self.assertIn("元素周期表", content)

    def test_html_write_failure(self) -> None:
        bad = os.path.join(self._tmp.name, "missing", "page.html")
        code, _, stderr = self.run_cli(["html", "-o", bad])
        self.assertEqual(code, 1)
        self.assertIn("写入文件失败", stderr)

    def test_element(self) -> None:
        code, output, _ = self.run_cli(["element", "na"])
        self.assertEqual(code, 0)
        self.assertIn("钠", output)
        self.assertIn("23", output)

    def test_element_unknown(self) -> None:
        code, _, stderr = self.run_cli(["element", "Xx"])
        self.assertEqual(code, 2)
        self.assertIn("未收录", stderr)

    def test_atom(self) -> None:
        code, output, _ = self.run_cli(["atom", "11"])
        self.assertEqual(code, 0)
        self.assertIn("2、8、1", output)

    def test_atom_without_diagram(self) -> None:
        code, _, stderr = self.run_cli(["atom", "Fe"])
        self.assertEqual(code, 2)
        self.assertIn("前 20 号元素", stderr)

    def test_mass(self) -> None:
        code, output, _ = self.run_cli(["mass", "Ca(OH)2"])
        self.assertEqual(code, 0)
        self.assertIn("74", output)
        self.assertIn("Ca:1", output)

    def test_mass_invalid(self) -> None:
        code, _, stderr = self.run_cli(["mass", "Ca(OH"])
        self.assertEqual(code, 2)

    def test_balance(self) -> None:
        code, output, _ = self.run_cli(
            ["balance", "Fe", "+", "O2", "=", "Fe3O4"]
        )
        self.assertEqual(code, 0)
        self.assertIn("3Fe", output)
        self.assertIn("2O2", output)

    def test_balance_invalid(self) -> None:
        code, _, stderr = self.run_cli(["balance", "H2", "+", "O2"])
        self.assertEqual(code, 2)
        self.assertIn("错误", stderr)


if __name__ == "__main__":
    unittest.main()
