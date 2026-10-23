#!/usr/bin/env python3
"""test_validate_cad_rules.py — Unit test suite untuk validate_cad_rules.py.

Menguji deteksi kegagalan aturan drafting CAD perusahaan secara otomatis:
  (a) Nozzle melayang (LINE vertikal 10 mm di ruang kosong, REF-EQUIP) -> Dangling Endpoint.
  (b) Sinyal REF-SIG menembus REF-PROC tanpa break -> Signal Crossing Error.
  (c) TEXT single-line terlarang -> Forbidden Entity Error.
  (d) MTEXT h=4.5 mm (melebihi batas 3.0 mm) -> MTEXT Height Error.
  (e) Persilangan REF-PROC tanpa break -> Unbroken Process Crossing Error.
  (f) Teks menabrak garis REF-SYM -> Text-Line Collision Error.
  (g) Dua teks bertumpuk (>0.3 mm) -> Text-Text Collision Error.
  (h) Uji realistis: pid_v101.dxf asli <= 5 warning (0 error), dan suntikan stub 10 mm
      terdeteksi presisi di koordinatnya sebagai ERROR.
  Kasus POSITIF:
    - Sinyal REF-SIG dengan break gap 3.0 mm sah -> PASS (0 error).
    - Teks dalam bubble instrumen lingkaran yang sah -> PASS (0 error).
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import ezdxf
except ImportError:
    sys.exit("Error: pustaka 'ezdxf' tidak ditemukan.")

# Import validator module under test
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from validate_cad_rules import CADValidator, COMPANY_LINEWEIGHTS


def create_clean_doc() -> ezdxf.document.Drawing:
    """Buat dokumen DXF bersih R2010 lengkap dengan standard layer lineweights dan style ARIAL."""
    doc = ezdxf.new("R2010")
    for name, lw in COMPANY_LINEWEIGHTS.items():
        doc.layers.add(name=name, lineweight=lw)
    doc.styles.new("ARIAL", dxfattribs={"font": "Arial.ttf"})
    return doc


class TestCADRulesValidation(unittest.TestCase):
    """Test suite untuk verifikasi linter CAD rules perusahaan."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _save_dxf_and_json(self, doc, texts=None):
        dxf_file = self.temp_path / "test_drawing.dxf"
        doc.saveas(str(dxf_file))
        if texts is not None:
            json_file = self.temp_path / "test_drawing.texts.json"
            json_file.write_text(json.dumps({"texts": texts}, indent=2), encoding="utf-8")
        return str(dxf_file)

    # -------------------------------------------------------------------------
    # (a) Nozzle melayang (LINE vertikal 10 mm di ruang kosong, REF-EQUIP)
    # -------------------------------------------------------------------------
    def test_case_a_dangling_nozzle_melayang(self):
        """(a) Deteksi nozzle melayang: LINE vertikal 10 mm di ruang kosong (REF-EQUIP)."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        # Nozzle 10 mm menggantung di ruang kosong
        msp.add_line((100.0, 100.0), (100.0, 110.0), dxfattribs={"layer": "REF-EQUIP"})
        dxf_path = self._save_dxf_and_json(doc)

        # Uji mode auto (default: >= 8mm adalah ERROR)
        val = CADValidator(dxf_path)
        errs, warns = val.run_all_checks()
        self.assertGreater(len(val.dangling_endpoints), 0, "Harus mendeteksi dangling endpoints")
        coords = [pt for _, pt, _ in val.dangling_endpoints]
        self.assertIn((100.0, 100.0), coords)
        self.assertIn((100.0, 110.0), coords)
        self.assertGreater(errs, 0, "LINE 10 mm melayang harus menghasilkan ERROR default")
        self.assertTrue(any("Check 6" in e for e in val.errors))
        print("\n  [PASS] Test (a): Nozzle melayang (REF-EQUIP 10 mm) berhasil terdeteksi sebagai ERROR di Check 6.")

    # -------------------------------------------------------------------------
    # (b) Sinyal REF-SIG menembus REF-PROC tanpa break
    # -------------------------------------------------------------------------
    def test_case_b_signal_crossing_unbroken(self):
        """(b) Deteksi sinyal REF-SIG menembus interior REF-PROC tanpa break gap 3 mm."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        # Garis pipa proses vertikal
        msp.add_line((100.0, 50.0), (100.0, 150.0), dxfattribs={"layer": "REF-PROC"})
        # Garis sinyal horizontal menembus langsung di y=100
        msp.add_line((50.0, 100.0), (150.0, 100.0), dxfattribs={"layer": "REF-SIG"})
        dxf_path = self._save_dxf_and_json(doc)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertGreater(errs, 0)
        self.assertGreater(len(val.signal_crossings), 0)
        self.assertTrue(any("Check 7" in e for e in val.errors))
        print("\n  [PASS] Test (b): Sinyal menembus REF-PROC tanpa break berhasil terdeteksi di Check 7.")

    # -------------------------------------------------------------------------
    # (c) TEXT single-line
    # -------------------------------------------------------------------------
    def test_case_c_forbidden_single_line_text(self):
        """(c) Deteksi entitas terlarang TEXT (single-line; wajib MTEXT)."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        msp.add_text("TAG-101", dxfattribs={"layer": "REF-TEXT", "insert": (50.0, 50.0)})
        dxf_path = self._save_dxf_and_json(doc)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertGreater(errs, 0)
        self.assertTrue(any("Check 1" in e for e in val.errors))
        self.assertTrue(any("TEXT" in e for e in val.errors))
        print("\n  [PASS] Test (c): Single-line TEXT terlarang berhasil terdeteksi di Check 1.")

    # -------------------------------------------------------------------------
    # (d) MTEXT h=4.5 (melebihi batas 3.0 mm)
    # -------------------------------------------------------------------------
    def test_case_d_mtext_font_height_exceeded(self):
        """(d) Deteksi MTEXT dengan char_height 4.5 mm (melebihi rentang standar 0.5-3.0 mm)."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        msp.add_mtext("OVERSIZED TEXT", dxfattribs={
            "layer": "REF-TEXT",
            "style": "ARIAL",
            "char_height": 4.5,
            "insert": (50.0, 50.0),
        })
        dxf_path = self._save_dxf_and_json(doc)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertGreater(errs, 0)
        self.assertTrue(any("Check 2" in e for e in val.errors))
        self.assertTrue(any("char_height" in e for e in val.errors))
        print("\n  [PASS] Test (d): MTEXT h=4.5 mm berhasil terdeteksi di Check 2.")

    # -------------------------------------------------------------------------
    # (e) Crossing REF-PROC tanpa break
    # -------------------------------------------------------------------------
    def test_case_e_proc_crossing_unbroken(self):
        """(e) Deteksi dua pipa proses (REF-PROC) bersilangan tanpa break gap 3 mm."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        # Dua pipa proses ortogonal saling memotong di interior
        msp.add_line((50.0, 100.0), (150.0, 100.0), dxfattribs={"layer": "REF-PROC"})
        msp.add_line((100.0, 50.0), (100.0, 150.0), dxfattribs={"layer": "REF-PROC"})
        dxf_path = self._save_dxf_and_json(doc)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertGreater(errs, 0)
        self.assertTrue(any("Check 4" in e for e in val.errors))
        print("\n  [PASS] Test (e): Persilangan REF-PROC tanpa break berhasil terdeteksi di Check 4.")

    # -------------------------------------------------------------------------
    # (f) Teks menabrak garis REF-SYM
    # -------------------------------------------------------------------------
    def test_case_f_text_colliding_with_ref_sym(self):
        """(f) Deteksi teks menabrak garis pada layer simbol proses (REF-SYM)."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        # Garis simbol melintang menembus lokasi teks
        msp.add_line((50.0, 100.0), (150.0, 100.0), dxfattribs={"layer": "REF-SYM"})
        texts = [
            {"t": "VALVE-TAG", "x": 100.0, "y": 100.0, "h": 2.0, "rot": 0.0, "att": 5}
        ]
        dxf_path = self._save_dxf_and_json(doc, texts=texts)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertGreater(errs, 0)
        self.assertTrue(any("Check 5" in e for e in val.errors))
        self.assertTrue(any(c[3] == "REF-SYM" for c in val.text_collisions))
        print("\n  [PASS] Test (f): Teks menabrak garis REF-SYM berhasil terdeteksi di Check 5.")

    # -------------------------------------------------------------------------
    # (g) Dua teks bertumpuk (>0.3 mm)
    # -------------------------------------------------------------------------
    def test_case_g_two_texts_overlapping(self):
        """(g) Deteksi dua teks dengan bounding box tumpang tindih > 0.3 mm."""
        doc = create_clean_doc()
        texts = [
            {"t": "TAG-ALPHA", "x": 100.0, "y": 100.0, "h": 2.0, "rot": 0.0, "att": 5},
            {"t": "TAG-BETA", "x": 100.5, "y": 100.0, "h": 2.0, "rot": 0.0, "att": 5},
        ]
        dxf_path = self._save_dxf_and_json(doc, texts=texts)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertGreater(errs, 0)
        self.assertTrue(any("Check 5" in e for e in val.errors))
        self.assertTrue(any(c[0] == "TEXT" for c in val.text_collisions))
        print("\n  [PASS] Test (g): Dua teks bertumpuk berhasil terdeteksi di Check 5.")

    # -------------------------------------------------------------------------
    # (h) Uji realistis: pid_v101.dxf asli <= 5 warning, suntikan stub 10 mm -> ERROR
    # -------------------------------------------------------------------------
    def test_case_h_realistic_pid_injected_nozzle_melayang(self):
        """(h) DXF realistis: pid_v101.dxf asli HARUS <= 5 warning (0 error),
        dan salinan dengan stub nozzle 10 mm HARUS menghasilkan ERROR di koordinat stub."""
        candidates = [
            Path("/home/arienugraha-rei/gas-prod-facility/cad/pid_v101.dxf"),
            SCRIPT_DIR.parent.parent / "gas-prod-facility/cad/pid_v101.dxf",
        ]
        pid_file = None
        for cand in candidates:
            if cand.exists():
                pid_file = cand
                break

        self.assertIsNotNone(pid_file, "File pid_v101.dxf harus ada untuk uji realistis")

        # 1. Audit baseline pid_v101.dxf asli (HARUS 0 error dan <= 5 warning)
        val_orig = CADValidator(str(pid_file))
        orig_errs, orig_warns = val_orig.run_all_checks()
        self.assertEqual(orig_errs, 0, f"pid_v101.dxf asli tidak boleh ada error: {val_orig.errors}")
        self.assertLessEqual(orig_warns, 5, f"pid_v101.dxf asli harus <= 5 warning: {val_orig.warnings}")

        # 2. Uji mutasi stub menempel pada weir (335, 275) dengan panjang 5, 8, dan 12 mm -> SEMUA HARUS ERROR
        pid_texts = pid_file.with_suffix(".texts.json")
        for stub_len in (5.0, 8.0, 12.0):
            doc_stub = ezdxf.readfile(str(pid_file))
            msp_stub = doc_stub.modelspace()
            msp_stub.add_line((335.0, 275.0), (335.0 + stub_len, 275.0), dxfattribs={"layer": "REF-EQUIP"})
            stub_dxf = self.temp_path / f"pid_v101_stub_{int(stub_len)}.dxf"
            doc_stub.saveas(str(stub_dxf))
            if pid_texts.exists():
                (self.temp_path / f"pid_v101_stub_{int(stub_len)}.texts.json").write_text(
                    pid_texts.read_text(encoding="utf-8")
                )

            val_stub = CADValidator(str(stub_dxf))
            stub_errs, _ = val_stub.run_all_checks()
            self.assertGreater(stub_errs, 0, f"Stub {stub_len} mm menempel pada weir harus menghasilkan ERROR")
            self.assertTrue(any("Check 6" in e for e in val_stub.errors))
            dang_pts = [pt for _, pt, _ in val_stub.dangling_endpoints]
            target_pt = (round(335.0 + stub_len, 2), 275.0)
            self.assertIn(target_pt, dang_pts, f"Ujung bebas {target_pt} harus terdeteksi di Check 6")

        # 3. Uji stub tepat 8.0 mm dua ujung bebas di ruang kosong (200, 200) -> (208, 200) -> HARUS ERROR
        doc_free8 = ezdxf.readfile(str(pid_file))
        msp_free8 = doc_free8.modelspace()
        msp_free8.add_line((200.0, 200.0), (208.0, 200.0), dxfattribs={"layer": "REF-PROC"})
        free8_dxf = self.temp_path / "pid_v101_free8.dxf"
        doc_free8.saveas(str(free8_dxf))
        if pid_texts.exists():
            (self.temp_path / "pid_v101_free8.texts.json").write_text(pid_texts.read_text(encoding="utf-8"))

        val_free8 = CADValidator(str(free8_dxf))
        free8_errs, _ = val_free8.run_all_checks()
        self.assertGreater(free8_errs, 0, "Garis tepat 8.0 mm dua ujung bebas harus menghasilkan ERROR")
        self.assertTrue(any("Check 6" in e for e in val_free8.errors))
        free8_pts = [pt for _, pt, _ in val_free8.dangling_endpoints]
        self.assertIn((200.0, 200.0), free8_pts)
        self.assertIn((208.0, 200.0), free8_pts)

        # 4. Verifikasi bahwa seluruh iso_*.dxf memiliki 0 dangling endpoints
        for isof in ("iso_go1002.dxf", "iso_co1003.dxf", "iso_co1004.dxf"):
            iso_path = pid_file.parent / isof
            if iso_path.exists():
                val_iso = CADValidator(str(iso_path))
                val_iso.run_all_checks()
                self.assertEqual(len(val_iso.dangling_endpoints), 0, f"{isof} harus 0 dangling endpoints")

        print("\n  [PASS] Test (h): Stub menempel 5/8/12 mm pada weir & garis bebas 8 mm terdeteksi sebagai ERROR; pid_v101 asli 0 temuan; iso_*.dxf 0 dangling.")

    # -------------------------------------------------------------------------
    # Kasus POSITIF 1: Break 3 mm yang sah pada sinyal
    # -------------------------------------------------------------------------
    def test_case_positive_legitimate_signal_break(self):
        """Kasus POSITIF: Sinyal dengan break gap 3 mm sah (dashed_brk) TIDAK memicu error."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        # Garis pipa proses vertikal di x=100 yang terhubung pada kedua ujungnya
        msp.add_line((100.0, 50.0), (100.0, 150.0), dxfattribs={"layer": "REF-PROC"})
        msp.add_line((50.0, 50.0), (150.0, 50.0), dxfattribs={"layer": "REF-PROC"})
        msp.add_line((50.0, 150.0), (150.0, 150.0), dxfattribs={"layer": "REF-PROC"})
        # Sinyal horizontal dengan celah 3.0 mm: segmen 1 berhenti di 98.5, segmen 2 mulai di 101.5
        msp.add_line((50.0, 100.0), (98.5, 100.0), dxfattribs={"layer": "REF-SIG"})
        msp.add_line((101.5, 100.0), (150.0, 100.0), dxfattribs={"layer": "REF-SIG"})
        dxf_path = self._save_dxf_and_json(doc)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertEqual(len(val.signal_crossings), 0, "Break 3 mm tidak boleh dianggap crossing")
        self.assertEqual(errs, 0, f"Tidak boleh ada error pada sinyal dengan break 3 mm sah: {val.errors}")
        print("\n  [PASS] Kasus Positif: Break 3.0 mm sah pada REF-SIG tidak memicu error Check 7.")

    # -------------------------------------------------------------------------
    # Kasus POSITIF 2: Teks dalam bubble instrumen
    # -------------------------------------------------------------------------
    def test_case_positive_text_inside_bubble(self):
        """Kasus POSITIF: Teks label di dalam lingkaran bubble instrumen sah TIDAK memicu collision."""
        doc = create_clean_doc()
        msp = doc.modelspace()
        # Lingkaran bubble instrumen diameter 10 mm (r=5.0) di (100, 100)
        msp.add_circle((100.0, 100.0), 5.0, dxfattribs={"layer": "REF-SYM"})
        texts = [
            {"t": "PT-101", "x": 100.0, "y": 100.0, "h": 2.0, "rot": 0.0, "att": 5}
        ]
        dxf_path = self._save_dxf_and_json(doc, texts=texts)

        val = CADValidator(dxf_path)
        errs, _ = val.run_all_checks()
        self.assertEqual(len(val.text_collisions), 0, "Teks di dalam bubble tidak boleh dianggap tabrakan")
        self.assertEqual(errs, 0, "Tidak boleh ada error pada teks label di dalam bubble instrumen")
        print("\n  [PASS] Kasus Positif: Teks dalam bubble instrumen sah tidak memicu error Check 5.")


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCADRulesValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
