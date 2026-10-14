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


class Fetch(unittest.TestCase):
    def local(self, t, **extra):
        f = Path(t) / "b.nro"
        f.write_bytes(b"nro")
        return {"name": "b", "source": "local", "path": str(f), **extra}, f

    def test_local_roundtrip(self):
        with tempfile.TemporaryDirectory() as t:
            c, f = self.local(t)
            tag, name, p, digest = build.fetch_verified(c, Path(t) / "cache")
            self.assertEqual((tag, name, p), ("local", "b.nro", f))
            self.assertEqual(digest, build.sha256(f))

    def test_sha_mismatch_names_component(self):
        with tempfile.TemporaryDirectory() as t:
            c, _ = self.local(t, sha256="0" * 64)
            with self.assertRaisesRegex(build.BuildError, r"^b: .*sha256"):
                build.fetch_verified(c, Path(t) / "cache")

    def test_unknown_source(self):
        with self.assertRaisesRegex(build.BuildError, r"^x: "):
            build.fetch_verified({"name": "x", "source": "ftp"}, Path("."))


if __name__ == "__main__":
    unittest.main()
