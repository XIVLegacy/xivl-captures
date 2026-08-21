# Cold Storage Config

Tracked manifests and catalog entries use logical storage IDs, not
machine-specific absolute paths. This indirection lets the same
`storage_path: archives/<id>/...` resolve to a repo-relative location by
default and to a per-machine override when needed.

## Files

- `cold-storage.example.yaml` is the committed template. Both `repo-lfs` and
  `local-cold-storage` resolve relative to the repo root by default.
- `cold-storage.local.yaml` is the gitignored, optional override. Use it when
  `archives/` should live somewhere other than the repo root (separate drive,
  removable media, network share). When present, it takes precedence over the
  example.

## Storage IDs

- `repo-lfs` - original committed to the repo under
  `sources/<id>/objects/` via Git LFS. Used when the file is `<=25 MB`.
- `local-cold-storage` - original lives in the gitignored `archives/<id>/`
  folder at the repo root. Used when the file is `>25 MB` and is moved to cold
  storage after distillation. Source gameplay videos are usually NOT archived
  at all (record the title/URL in the manifest `notes`). This only applies when
  a video file is deliberately kept.
- `XIVLegacy/xivl-retail-client-inputs` - the restricted private archive named
  by the `pcap-1.23b` manifest. Its local `objects/` and `archives/` copies are
  caches and are not a second evidence authority.

## Restore Flow

1. Read the source's `manifest.yaml` retention block (`storage.original_state`,
   `storage.storage_id`, `storage.path`).
2. Look up `storage_id` in this config (default -> `cold-storage.example.yaml`;
   override -> `cold-storage.local.yaml`).
3. Combine the storage `base_path` with `manifest.yaml`'s `storage.path` to get
   the absolute file location.
4. Validate the restored file against the paired study's
   `derived/checksums.sha256` before re-extracting.
