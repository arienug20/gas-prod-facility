# Catatan eksekusi fondasi roadmap gelombang 1

**Status:** subtranche foundation selesai sebagai implementasi additive dan terisolasi. Ini bukan penyelesaian seluruh WP1/WP2/WP3, pilot P&ID, atau roadmap tooling.

## Hasil

Adapter `cad/roadmap_foundation/workflow.py` menerima basis, katalog standar, graph, dan ID deliverable secara eksplisit. Adapter menggabungkan report dari readiness data, validator katalog, dan audit graph dengan status masing-masing tetap terpisah. `engineering_review` selalu `NOT ASSESSED`; tidak ada status overall `compliant`, `approved`, atau engineering-ready. Catalog/graph yang tidak ada tetap `NOT ASSESSED`, bukan dianggap lolos. Catalog atau graph tanpa temuan error juga tetap `NOT ASSESSED` karena audit sempit ini tidak membuktikan coverage atau kecukupan engineering.

Implementasi readiness/schema, standar, registry graph, dan adapter workflow adalah fondasi baru. Workflow ini belum dihubungkan ke PID builder atau adapter model lama. Ia tidak mengubah atau menghasilkan drawing dan tidak mengubah design basis.

## Penggunaan

Input CLI berupa JSON envelope:

```json
{
  "basis": {"schema_version": "1.0", "sources": [], "basis_items": [], "authorizations": [], "deliverables": []},
  "catalog": {"schema_version": "1.0", "standards": [], "rules": [], "symbols": [], "mappings": []},
  "graph": {"schema_version": "1.0", "objects": [], "ports": [], "connections": []},
  "deliverable_id": "DEL-SYMBOL"
}
```

Semua ID di atas hanya penanda kontrak, bukan nilai/tag proses proyek. Ganti isi dengan data yang memiliki provenance dan authorization sesuai kontrak modul sebelum penggunaan proyek.

```powershell
python -m cad.roadmap_foundation.workflow package.json
python -m cad.roadmap_foundation.workflow package.json --out report.json
```

`--out` dibuat eksklusif: path yang sama dengan input, path yang sudah ada, atau parent yang belum ada ditolak. JSON rusak menampilkan lokasi parse error dan keluar nonzero (argparse code 2); section wajib yang missing/null menghasilkan package finding terstruktur dan exit code 1, sementara status komponen tetap terpisah dan `NOT ASSESSED`. Return code nol hanya berarti data readiness `ready` dan input section tersedia tanpa status invalid; itu tidak berarti catalog, graph, atau engineering review telah disetujui. Baca status per bagian pada report.

## Verifikasi yang dijalankan

- `python -m unittest cad.test_roadmap_readiness cad.test_roadmap_standards cad.test_roadmap_registry cad.test_roadmap_workflow -v`
- `python -m py_compile cad/roadmap_foundation/readiness.py cad/roadmap_foundation/standards.py cad/roadmap_foundation/registry.py cad/roadmap_foundation/workflow.py cad/test_roadmap_readiness.py cad/test_roadmap_standards.py cad/test_roadmap_registry.py cad/test_roadmap_workflow.py`

Fixture workflow menggunakan ID simbolik sintetis dan tidak memuat angka desain proses. Verifikasi hanya mencakup kontrak readiness/catalog/graph yang tersedia serta adapter, bukan engineering design review, kecukupan seluruh standards, safety, atau kelengkapan semua requirement deliverable. Runtime sandbox awal tidak dapat mengimpor `pytest`; konteks tersebut dicatat sebagai histori dan diikuti verifikasi runtime profil pengguna di bawah.

### Appendix runtime pytest — 28 Oktober 2026

Pemeriksaan ulang menggunakan Python dengan akses ke site-packages profil pengguna:

- `python -m pytest --version` → `pytest 9.1.1`
- Foundation-only: `python -m unittest cad.test_roadmap_readiness cad.test_roadmap_standards cad.test_roadmap_registry cad.test_roadmap_workflow -v` → `Ran 46 tests ... OK`.
- Bounded seven-module suite: `python -m pytest cad/test_smart_annotations.py cad/test_smart_router.py cad/test_smart_qa.py cad/test_roadmap_standards.py cad/test_roadmap_readiness.py cad/test_roadmap_registry.py cad/test_roadmap_workflow.py -q --basetemp tmp/pytest-roadmap-luna-scope` → `77 passed, 131 warnings in 3.37s` (exit code 0).
- Warning summary: all 131 are `DeprecationWarning` emitted through installed `ezdxf`/`pyparsing` calls: 7 legacy parser API call sites in `ezdxf.queryparser`, 62 `parseString` calls, and 62 deprecated `parseAll` arguments during `cad/test_smart_qa.py`.
- Pelaksana: Codex agent Luna; dijalankan pada runtime profil pengguna melalui eskalasi karena sandbox awal tidak dapat mengimpor pytest. Tidak ada paket yang dipasang dalam verifikasi ini.
- Earlier local result `75 passed, 131 warnings` is superseded by the fresh `77 passed` run after adding deliverable-scope and numeric-unit tests. The `cad/test_smart_*` modules are legacy toolkit checks outside the four-module foundation release scope; their results are supplemental, not a full-repository or roadmap pass.

Hasil ini terbatas pada tujuh modul yang disebutkan; tidak menyatakan seluruh repository, roadmap, atau engineering deliverable lulus. The standalone, reproducible foundation verification consists of the four roadmap unittest modules listed above.

## Batas integrasi dan tindak lanjut

Adapter terhubung ke API modul readiness/catalog/graph secara langsung, tetapi belum menjadi bagian dari `pid_config_builder`, pipeline gambar, atau fixture pilot FEED/DED. Pengembangan berikutnya memerlukan adapter proyek berversi, requirement matrix per deliverable/fase, source/decision register yang disetujui, profile standar dan legend yang ditetapkan, serta review ahli engineering tersendiri. Tidak ada klaim bahwa wave 1 atau keseluruhan roadmap telah selesai.
