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


def add_base(root):
    (root / "base/bootloader").mkdir(parents=True)
    (root / "base/bootloader/hekate_ipl.ini").write_text("[config]\n")


def with_release(root, text):
    m = root / "manifest.toml"
    m.write_text(text + "\n" + m.read_text())


class Update(unittest.TestCase):
    def run_build(self, root, version="9.9", name="out.zip"):
        return build.build(root, root / "manifest.toml", root / "dist" / name, root / ".cache", version)

    def test_update_zip_is_full_minus_user_owned(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            add_base(root)
            full = set(zipfile.ZipFile(self.run_build(root)).namelist())
            upd = set(zipfile.ZipFile(root / "dist/karman-update.zip").namelist())
            self.assertEqual(full - upd, set(build.USER_OWNED) & full)
            self.assertTrue({"bootloader/hekate_ipl.ini", "config/ultrahand/config.ini"} <= full - upd)
            self.assertEqual(upd - full, set())

    def test_user_edited_configs_are_user_owned(self):
        for f in ("config/sys-ftpd/config.ini", "config/Fizeau/config.ini"):
            self.assertIn(f, build.USER_OWNED)

    def test_update_zip_deterministic(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            self.run_build(root, name="1.zip")
            a = (root / "dist/karman-update.zip").read_bytes()
            self.run_build(root, name="2.zip")
            self.assertEqual(a, (root / "dist/karman-update.zip").read_bytes())

    def test_version_ini_in_both_zips_and_latest_asset(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            want = b"[karman]\nversion=1.2.3\nbuild=26101401\n"
            full = zipfile.ZipFile(build.build(root, root / "manifest.toml", root / "dist/o.zip", root / ".cache", "1.2.3", "26101401"))
            upd = zipfile.ZipFile(root / "dist/karman-update.zip")
            self.assertEqual(full.read("karman/version.ini"), want)
            self.assertEqual(upd.read("karman/version.ini"), want)
            self.assertEqual((root / "dist/karman-latest.ini").read_bytes(), want)

    def test_build_number_must_be_8_digits(self):
        for bad in ("abc", "2610140", "261014011", ""):
            with self.subTest(bad), tempfile.TemporaryDirectory() as t:
                root = make_root(t)
                with self.assertRaisesRegex(build.BuildError, "build"):
                    build.build(root, root / "manifest.toml", root / "dist/o.zip", root / ".cache", "1", bad)

    def test_bad_release_type_names_key(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            with_release(root, "[release]\nrepo = 5")
            with self.assertRaisesRegex(build.BuildError, "repo"):
                self.run_build(root)

    def test_failed_build_removes_stale_update_zip(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            self.run_build(root)
            (root / "fix/a.zip").write_bytes(b"not a zip")
            with self.assertRaises(build.BuildError):
                self.run_build(root)
            self.assertFalse((root / "dist/karman-update.zip").exists())
            self.assertFalse((root / "dist/karman-latest.ini").exists())


class Hardening(unittest.TestCase):
    def run_build(self, root, name="out.zip"):
        return build.build(root, root / "manifest.toml", root / "dist" / name, root / ".cache")

    def test_bad_release_leaves_no_stale_zips(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            self.run_build(root)
            with_release(root, "[release]\nrepo = 5")
            with self.assertRaises(build.BuildError):
                self.run_build(root)
            self.assertFalse((root / "dist/out.zip").exists())
            self.assertFalse((root / "dist/karman-update.zip").exists())

    def test_release_values_are_validated(self):
        bad = [
            ('repo = "a b/c"', "repo"), ('repo = "no-slash"', "repo"), ('repo = ""', "repo"),
            ('repo = "o/r\\nmove / /x"', "repo"),
            ('firmware_url = "http://x/f.zip"', "firmware_url"),
            ('firmware_url = "https://x/f.zip\\nmove / /x"', "firmware_url"),
            ('firmware_url = "https://x y/f.zip"', "firmware_url"),
            ('firmware_url = 5', "firmware_url"),
            ('repository = "o/r"', "repository"),
        ]
        for line, key in bad:
            with self.subTest(line):
                with tempfile.TemporaryDirectory() as t:
                    root = make_root(t)
                    with_release(root, "[release]\n" + line)
                    with self.assertRaisesRegex(build.BuildError, key):
                        self.run_build(root)

    def test_release_must_be_a_table(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            with_release(root, "release = 5")
            with self.assertRaisesRegex(build.BuildError, "release"):
                self.run_build(root)

    def test_second_zip_failure_removes_first(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            real, calls = build.write_zip, []

            def flaky(stage, out, skip=()):
                calls.append(out)
                if len(calls) == 2:
                    raise OSError("disk full")
                return real(stage, out, skip)

            with mock.patch.object(build, "write_zip", flaky):
                with self.assertRaises(OSError):
                    self.run_build(root)
            self.assertFalse((root / "dist/out.zip").exists())


DL = "/config/ultrahand/downloads"
UPD = "https://github.com/o/r/releases/latest/download/karman-update.zip"
LATEST = "https://github.com/o/r/releases/latest/download/karman-latest.ini"
D = "({ini_file(karman,build)}-26101401%s+100000000)/100000000"


def section(pkg, title):
    lines, out, on = pkg.splitlines(), [], False
    for l in lines:
        if l.startswith("["):
            on = l == f"[{title}]"
        if on:
            out.append(l)
    return out


class Package(unittest.TestCase):
    def pkg(self, release_toml="", build_no="26101401"):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            if release_toml:
                with_release(root, release_toml)
            z = zipfile.ZipFile(build.build(root, root / "manifest.toml", root / "dist/o.zip", root / ".cache", "dev", build_no))
            return z.read("switch/.packages/Karman/package.ini").decode()

    def test_update_section_gates_on_build_number(self):
        sec = section(self.pkg('[release]\nrepo = "o/r"'), "Update Karman (reboot after)")
        self.assertEqual(sec, [
            "[Update Karman (reboot after)]",
            "try:", f"delete {DL}/gate/",
            "try:", f"delete {DL}/karman-latest.ini",
            "try:", f"delete {DL}/karman-update/",
            "try:", f"delete {DL}/karman-update.zip",
            "try:",
            f"mkdir {DL}/gate/",
            f"download {LATEST} {DL}/karman-latest.ini",
            f"ini_file {DL}/karman-latest.ini",
            "touch " + DL + "/gate/p{math(" + (D % "-1") + ",true)}",
            "touch " + DL + "/gate/n{math(" + (D % "") + ",true)}",
            "try:", f"path_exists {DL}/gate/n0",
            "notify-now 'Blocked: your Karman is newer than the latest release. Use Force install latest to override, at your own risk.'",
            "try:", f"path_exists {DL}/gate/n1", f"path_exists {DL}/gate/p0",
            "notify-now 'Karman is already up to date.'",
            "try:", f"!path_exists {DL}/gate/n0", f"!path_exists {DL}/gate/n1",
            "notify-now 'Could not check for updates. Nothing was changed.'",
            "try:",
            f"path_exists {DL}/gate/p1",
            f"download {UPD} {DL}/karman-update.zip",
            f"unzip {DL}/karman-update.zip {DL}/karman-update/",
            f"move {DL}/karman-update/ /",
            f"delete {DL}/karman-update.zip",
            "notify-now 'Updated. Reboot to apply.'",
            "",
        ])

    def test_reboot_shortcuts(self):
        pkg = self.pkg()
        self.assertEqual(section(pkg, "Reboot to boot entry"), [
            "[Reboot to boot entry]",
            "ini_file_source /bootloader/hekate_ipl.ini",
            "filter config",
            "reboot boot '{ini_file_source(*)}'",
            "",
        ])
        self.assertIn("reboot HEKATE", section(pkg, "Reboot to Hekate"))
        self.assertIn("reboot UMS", section(pkg, "Reboot to USB mass storage"))
        self.assertIn("shutdown", section(pkg, "Shut down"))

    def test_install_only_after_positive_marker(self):
        sec = section(self.pkg('[release]\nrepo = "o/r"'), "Update Karman (reboot after)")
        gate = sec.index(f"path_exists {DL}/gate/p1")
        self.assertEqual([i for i, l in enumerate(sec) if l.startswith("download ") and "karman-latest.ini" not in l], [gate + 1])
        self.assertEqual(sec[gate - 1], "try:")  # fail-closed: the check heads its own block

    def test_installed_build_is_embedded(self):
        self.assertIn("-26101401", self.pkg('[release]\nrepo = "o/r"', build_no="26101401"))
        self.assertIn("-00000042", self.pkg('[release]\nrepo = "o/r"', build_no="00000042"))

    def test_force_entry_is_hold_to_confirm_and_ungated(self):
        sec = section(self.pkg('[release]\nrepo = "o/r"'), "Force install latest (may downgrade - at your own risk)")
        self.assertEqual(sec[1], ";hold=true")
        self.assertIn(f"download {UPD} {DL}/karman-update.zip", sec)
        self.assertFalse([l for l in sec if "gate" in l or "ini_file" in l])

    def test_no_update_section_without_repo(self):
        p = self.pkg()
        self.assertNotIn("Update Karman", p)
        self.assertNotIn("github.com", p)
        self.assertIn("[English]", p)  # language entries unaffected

    def test_firmware_section_only_with_url(self):
        self.assertNotIn("firmware", self.pkg('[release]\nrepo = "o/r"').lower())
        p = self.pkg('[release]\nrepo = "o/r"\nfirmware_url = "https://example.com/fw.zip"')
        self.assertIn("[Download firmware (then open Daybreak)]", p)
        self.assertIn("download https://example.com/fw.zip /config/ultrahand/downloads/firmware.zip", p)
        self.assertIn("unzip /config/ultrahand/downloads/firmware.zip /firmware/", p)

    def test_firmware_url_alone_does_not_need_repo(self):
        p = self.pkg('[release]\nfirmware_url = "https://example.com/fw.zip"')
        self.assertIn("Download firmware", p)
        self.assertNotIn("Update Karman", p)


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


class Modchip(unittest.TestCase):
    def build_with(self, *bins):
        with tempfile.TemporaryDirectory() as t:
            root = make_root(t)
            with zipfile.ZipFile(root / "fix/h.zip", "w") as z:
                for b in bins:
                    z.writestr(b, b"HEKATE")
            m = root / "manifest.toml"
            m.write_text(m.read_text() + f'[[component]]\nname="h"\nsource="local"\npath="{root/"fix/h.zip"}"\n')
            return zipfile.ZipFile(build.build(root, m, root / "dist/o.zip", root / ".cache"))

    def test_hekate_payload_copied_for_modchips_and_reboot(self):
        z = self.build_with("hekate_ctcaer_9.9.bin")
        self.assertEqual(z.read("payload.bin"), b"HEKATE")
        self.assertEqual(z.read("atmosphere/reboot_payload.bin"), b"HEKATE")

    def test_two_hekate_bins_is_an_error(self):
        with self.assertRaisesRegex(build.BuildError, "hekate_ctcaer"):
            self.build_with("hekate_ctcaer_1.bin", "hekate_ctcaer_2.bin")

    def test_no_hekate_bin_is_fine(self):
        self.assertNotIn("payload.bin", self.build_with("other.txt").namelist())


if __name__ == "__main__":
    unittest.main()
