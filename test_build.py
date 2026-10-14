import tempfile
import unittest
import zipfile
from pathlib import Path

import build


class Core(unittest.TestCase):
    def test_pick_asset_exactly_one(self):
        self.assertEqual(build.pick_asset(["a.zip", "b.nro"], "*.nro"), "b.nro")

    def test_pick_asset_zero_or_many_fails(self):
        with self.assertRaises(build.BuildError):
            build.pick_asset(["a.zip"], "*.nro")
        with self.assertRaises(build.BuildError):
            build.pick_asset(["a.zip", "b.zip"], "*.zip")

    def test_install_zip_and_file(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            z = t / "a.zip"
            with zipfile.ZipFile(z, "w") as zf:
                zf.writestr("atmosphere/x.txt", "x")
            n = t / "b.nro"
            n.write_bytes(b"nro")
            stage = t / "sd"
            build.install({"name": "a"}, z, stage)
            build.install({"name": "b", "dest": "switch/b"}, n, stage)
            self.assertTrue((stage / "atmosphere/x.txt").is_file())
            self.assertTrue((stage / "switch/b/b.nro").is_file())

    def test_install_bad_zip_raises(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            z = t / "a.zip"
            z.write_bytes(b"not a zip")
            with self.assertRaises(Exception):
                build.install({"name": "a"}, z, t / "sd")


if __name__ == "__main__":
    unittest.main()
