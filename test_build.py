import io
import json
import tempfile
import unittest
import urllib.error
import zipfile
from unittest import mock
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

    def test_install_zip_strip_and_exclude(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            z = t / "a.zip"
            with zipfile.ZipFile(z, "w") as zf:
                zf.writestr("SdOut/atmosphere/x.txt", "x")
                zf.writestr("SdOut/retroarch/cores/big.nro", "big")
                zf.writestr("SdOut/retroarch/keep.txt", "k")
                zf.writestr("top.jpg", "stray")
            stage = t / "sd"
            build.install({"name": "a", "strip": 1, "exclude": ["retroarch/cores/*"]}, z, stage)
            got = sorted(p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file())
            self.assertEqual(got, ["atmosphere/x.txt", "retroarch/keep.txt"])

    def test_install_zip_slip_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            z = t / "a.zip"
            with zipfile.ZipFile(z, "w") as zf:
                zf.writestr("x/../../evil.txt", "evil")
            with self.assertRaises(build.BuildError):
                build.install({"name": "a", "strip": 1}, z, t / "sd")
            self.assertFalse((t / "evil.txt").exists())

    def test_install_empty_result_fails(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            z = t / "a.zip"
            with zipfile.ZipFile(z, "w") as zf:
                zf.writestr("only/dir/", "")
            with self.assertRaisesRegex(build.BuildError, "no files"):
                build.install({"name": "a"}, z, t / "sd")

    def test_install_bad_zip_raises(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            z = t / "a.zip"
            z.write_bytes(b"not a zip")
            with self.assertRaises(Exception):
                build.install({"name": "a"}, z, t / "sd")


class RateLimit(unittest.TestCase):
    def test_403_hints_at_github_token(self):
        def boom(url, headers=None):
            raise urllib.error.HTTPError(url, 403, "rate limit exceeded", {}, io.BytesIO())

        real, build.http = build.http, boom
        try:
            with self.assertRaisesRegex(build.BuildError, "GITHUB_TOKEN"):
                build.api("repos/x/y/releases/latest")
        finally:
            build.http = real


class Cache(unittest.TestCase):
    comp = {"name": "p", "source": "github", "repo": "o/r", "asset": "a.nro", "pin": "rolling"}

    def fetch(self, cache, stamp, body):
        rel = {"tag_name": "rolling", "assets": [
            {"name": "a.nro", "browser_download_url": "https://x/a.nro", "updated_at": stamp}]}
        with mock.patch.object(build, "api", return_value=rel), \
                mock.patch.object(build, "http", return_value=body):
            return build.fetch_verified(self.comp, cache)[2]

    def test_rolling_tag_refetched_when_asset_updated(self):
        with tempfile.TemporaryDirectory() as t:
            self.fetch(Path(t), "2026-01-01", b"v1")
            self.assertEqual(self.fetch(Path(t), "2026-02-01", b"v2").read_bytes(), b"v2")

    def test_same_asset_stamp_uses_cache(self):
        with tempfile.TemporaryDirectory() as t:
            self.fetch(Path(t), "2026-01-01", b"v1")
            self.assertEqual(self.fetch(Path(t), "2026-01-01", b"other").read_bytes(), b"v1")

    def test_empty_download_fails_and_is_not_cached(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(build.BuildError, r"^p: .*empty"):
                self.fetch(Path(t), "s", b"")
            self.assertEqual(self.fetch(Path(t), "s", b"ok").read_bytes(), b"ok")


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


def make_root(t, langs=tuple(build.LANGS)):
    root = Path(t)
    (root / "base").mkdir()
    (root / "base/hello.txt").write_text("hi")
    for l in langs:
        d = root / "lang" / l / "config/ultrahand"
        d.mkdir(parents=True)
        (d / "config.ini").write_text(f"[ultrahand]\ndefault_lang={l}\n")
    fx = root / "fix"
    fx.mkdir()
    with zipfile.ZipFile(fx / "a.zip", "w") as z:
        z.writestr("atmosphere/x.txt", "x")
    (fx / "b.nro").write_bytes(b"nro")
    (root / "manifest.toml").write_text(
        f'[[component]]\nname="a"\nsource="local"\npath="{fx/"a.zip"}"\n'
        f'[[component]]\nname="b"\nsource="local"\npath="{fx/"b.nro"}"\ndest="switch"\n'
    )
    return root


class Build(unittest.TestCase):
    def run_build(self, root, name="out.zip"):
        return build.build(root, root / "manifest.toml", root / "dist" / name, root / ".cache")

    def test_zip_contents(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            z = zipfile.ZipFile(self.run_build(root))
            names = set(z.namelist())
            for want in [
                "atmosphere/x.txt", "switch/b.nro", "hello.txt",
                "config/ultrahand/config.ini",  # en live default
                "karman/lang/en/config/ultrahand/config.ini",
                "karman/lang/ptbr/config/ultrahand/config.ini",
                "karman/lang/es/config/ultrahand/config.ini",
                "switch/.packages/Karman/package.ini", "karman/lock.json",
            ]:
                self.assertIn(want, names)
            self.assertIn("default_lang=en", z.read("config/ultrahand/config.ini").decode())
            pkg = z.read("switch/.packages/Karman/package.ini").decode()
            self.assertIn("copy /karman/lang/ptbr/config/ultrahand/config.ini /config/ultrahand/", pkg)
            self.assertEqual(set(json.loads((root / "lock.json").read_text())), {"a", "b"})

    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            a = self.run_build(root, "1.zip").read_bytes()
            b = self.run_build(root, "2.zip").read_bytes()
            self.assertEqual(a, b)

    def test_base_wins_over_live_language_default(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            d = root / "base/config/ultrahand"
            d.mkdir(parents=True)
            (d / "config.ini").write_text("[ultrahand]\nkey_combo=custom\n")
            z = zipfile.ZipFile(self.run_build(root))
            self.assertIn("key_combo=custom", z.read("config/ultrahand/config.ini").decode())
            self.assertIn("default_lang=ptbr", z.read("karman/lang/ptbr/config/ultrahand/config.ini").decode())

    def test_entries_have_file_mode(self):
        with tempfile.TemporaryDirectory() as t:
            z = zipfile.ZipFile(self.run_build(make_root(t)))
            self.assertTrue(all(i.external_attr >> 16 == 0o644 for i in z.infolist()))

    def test_failed_build_removes_stale_zip_and_keeps_lock(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            self.run_build(root)
            old_lock = (root / "lock.json").read_text()
            (root / "fix/a.zip").write_bytes(b"not a zip")
            with self.assertRaises(build.BuildError):
                self.run_build(root)
            self.assertFalse((root / "dist/out.zip").exists())
            self.assertEqual((root / "lock.json").read_text(), old_lock)

    def test_missing_lang_fails_and_leaves_no_zip(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t, langs=("en", "es"))
            with self.assertRaisesRegex(build.BuildError, "ptbr"):
                self.run_build(root)
            self.assertFalse((root / "dist/out.zip").exists())

    def test_bad_component_names_it_and_leaves_no_zip(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            (root / "fix/a.zip").write_bytes(b"not a zip")
            with self.assertRaisesRegex(build.BuildError, r"^a: "):
                self.run_build(root)
            self.assertFalse((root / "dist/out.zip").exists())


if __name__ == "__main__":
    unittest.main()
