# Fondasi: identitas graph dan registry tag

**Status:** fondasi implementasi; bukan persetujuan semantik engineering, otorisasi desain, atau bukti bahwa graph telah lengkap.

`cad/roadmap_foundation/registry.py` menyediakan registry tag persisten berbasis standard library Python dan adapter konservatif ke graph schema `1.0`.

## API registry

Buat instance dengan `NamespaceTagRegistry(path, namespace, allocation)`. Record alokasi wajib menyediakan `id`, `approved_by`, `namespace`, `pattern`, `start`, dan `scope`; namespace-nya harus sama dengan namespace registry. `scope` wajib berisi daftar `prefixes` dan/atau `object_ids` yang tidak kosong. Alokasi dibatasi pada prefix/object ID tersebut. Reservasi memeriksa tag yang diberikan terhadap pola dan prefix yang disetujui serta cakupan object ID. Constructor gagal bila record alokasi tidak diberikan.

Namespace adalah batas administratif; namespace berbeda tidak membuktikan bahwa suatu tag unik secara global. `reserve(tag, object_id)` mempertahankan identitas yang diberikan dan menolak benturan maupun tag di luar cakupan. `allocate(prefix, object_id)` menghasilkan alokasi deterministik berdasarkan registry tersimpan. `save()` mengambil lock eksklusif pada file pendamping sebelum memeriksa hash di disk dan mengganti file secara atomik. Bila lock tetap tertahan melewati waktu tunggu, penulisan dibatalkan. Instance yang memakai salinan lama tidak dapat menimpa registry yang lebih baru. Proses yang berhenti mendadak dapat meninggalkan file lock; file itu hanya boleh ditangani setelah dipastikan tidak ada penulis yang masih berjalan. `NamespaceTagRegistry.reopen(path, namespace, allocation)` memuat ulang dan memvalidasi schema; data rusak atau versi yang tidak didukung ditolak. `to_dict()` menyediakan representasi untuk audit.

Contoh berikut hanya berlaku jika record alokasi yang benar-benar disetujui tersedia:

```python
from roadmap_foundation.registry import NamespaceTagRegistry
registry = NamespaceTagRegistry("registry.json", "approved-namespace", approved_allocation_record)
registry.reserve(existing_tag, object_id)
new_tag = registry.allocate(prefix, another_object_id)
registry.save()
```

Jangan gunakan identifier ilustratif pada tes sebagai bukti alokasi proyek. Jika otorisasi alokasi belum tersedia, biarkan tag belum terselesaikan; jangan mengalokasikan atau mengganti nomor.

## Adapter dan audit graph

`adapt_legacy_model(model)` mengembalikan `{"model": ..., "findings": ...}` tanpa mengubah input. Adapter mendukung bentuk `smart_qa` fase 1 dengan port tingkat atas (`owner`, `point`, `dn`, `spec`) serta koneksi (`from`, `to`, `dn`, `spec`). Field yang dikenal dipetakan dan metadata DN/spec/point dipertahankan. Bagian model kanonis adalah `objects` (`id`, `kind`, `tag` opsional), `ports` (`id`, `owner_id`, `port_kind`, `direction`, `service_ref` nullable), dan `connections` (`id`, `from_port`, `to_port`, `kind`). Port tingkat atas dan port bersarang dengan ID duplikat tetap disertakan dan dilaporkan secara eksplisit.

Port atau koneksi internal yang hilang tetap menghasilkan finding; assembly eksplisit tanpa koneksi internal yang dimodelkan mendapat status `NOT ASSESSED`. Bagian graph yang kosong dilaporkan sebagai tidak lengkap. Adapter tidak menyimpulkan nozzle, internals valve, koneksi dari geometri garis, atau junction dari persilangan. `audit_graph(model)` memeriksa ID, tag, referensi pemilik dan endpoint, serta kecocokan jenis koneksi yang dinyatakan eksplisit. Service/media yang belum diketahui berstatus `NOT ASSESSED`, bukan mismatch maupun pass. Field DN/spec yang null tidak otomatis menjadi error. Jenis proses dan sinyal dibedakan jika dinyatakan secara eksplisit. Tidak ada klaim tentang SIL, fungsi keselamatan, atau kelengkapan engineering secara keseluruhan.

Jalankan pemeriksaan terfokus dari root repository:

```powershell
python -m unittest cad.test_roadmap_registry -v
```

Tes mencakup otorisasi, tag duplikat, penyimpanan dan pemuatan ulang, deteksi penulisan dari salinan lama, kegagalan penggantian atomik, schema yang tidak didukung, input legacy tanpa mutasi, topologi internal yang belum diketahui, serta larangan mengubah persilangan menjadi koneksi.
