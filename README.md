# ultralytics-disk-cache-hook

Redirect `ultralytics` cache files away from the dataset directory and into a local cache root on the training node.

[中文说明](./README.zh-CN.md)

## Quick Start

```python
from ultralytics_disk_cache_hook import enable
from ultralytics import YOLO

enable()

model = YOLO("yolov8n.pt")
model.train(data="coco128.yaml", cache="disk")
```

After installation, the package also auto-enables itself for new Python processes via the
`ultralytics_disk_cache_hook_auto_enable_startup.pth` file in `site-packages`.

`enable()` now turns on both cache hooks by default. You can still control them independently:

```python
from ultralytics_disk_cache_hook import enable

enable(image_disk_cache=True, dataset_meta_cache=True)
enable(image_disk_cache=True, dataset_meta_cache=False)
enable(image_disk_cache=False, dataset_meta_cache=True)
```

## What It Does

When `ultralytics` runs with `cache="disk"`, it writes `*.npy` cache files next to the original images by default.

It also writes dataset metadata `*.cache` files such as `labels/train.cache`, `annotations.cache`, or `dataset_root.cache` next to the dataset source paths.

This plugin monkey patches the internal dataset implementation and redirects those cache files into a local temporary cache root instead.

- By default affects `cache="disk"` image caches
- By default affects dataset metadata `*.cache` files
- Lets you disable either hook independently via `enable(image_disk_cache=..., dataset_meta_cache=...)`
- Does not affect `cache="ram"` or disabled cache
- Rewrites `self.npy_files` for detection, segmentation, pose, and other tasks built on `BaseDataset`
- Rewrites `*.npy` paths inside `ClassificationDataset.samples` for classification tasks
- Can redirect dataset metadata cache helpers shared by detection, grounding, and classification datasets
- Writes cache files into hash buckets instead of mirroring the original dataset directory tree

## Cache Root

The cache root is derived from `ULTRALYTICS_DISK_CACHE_TMPDIR` when set, otherwise from `tempfile.gettempdir()`, with `ultralytics-disk-cache` appended to it.

Override it with an environment variable:

```bash
export ULTRALYTICS_DISK_CACHE_TMPDIR=/local_nvme/tmp
```

Example cache path:

```text
/mnt/shared-storage/datasets/coco/images/train2017/000000000001.jpg
-> <cache-root>/d1/3f/d13f474cca61f46ba06ecba11c1b3046.npy
```

Dataset metadata cache example:

```text
/mnt/shared-storage/datasets/coco/labels/train.cache
-> <cache-root>/7a/9c/7a9c5f8af885b2f5c6c2f67066342c0a.cache
```

## Version Support

This plugin monkey patches non-public `ultralytics` internals, so it only claims support for versions whose source layout has been checked.

The current code enforces the following validated range:

- Minimum supported version: `8.4.0`
- Maximum validated version: `8.4.38`
- Allowed range: `8.4.0 <= ultralytics <= 8.4.38`

If the installed version is outside that range, `enable()` raises `UnsupportedUltralyticsVersionError`.

Why:

- `v8.0.x` still uses the old `ultralytics/yolo/data/...` layout
- `v8.1.x` through `v8.3.x` do not match the internal hook points used by this patch
- Starting from `v8.4.0`, the `disk cache` structure in `BaseDataset` and `ClassificationDataset` matches this plugin

This range is based on checked GitHub source files and release/tag history. As of `2026-04-17`, the latest verified release I checked is `v8.4.38`.

Check the installed version with:

```bash
python -c "import ultralytics; print(ultralytics.__version__)"
```

## Disk Space

This plugin does not currently validate whether the cache disk has enough free space.

When `cache="disk"` is enabled, the plugin prints a warning with the cache root and asks the user to manage disk space manually.

If the local cache disk fills up, the error will occur when `*.npy` files are actually being written.

## References

- Ultralytics releases: https://github.com/ultralytics/ultralytics/releases
- Ultralytics tags: https://github.com/ultralytics/ultralytics/tags
- `v8.4.38` release: https://github.com/ultralytics/ultralytics/releases/tag/v8.4.38

## Copyright

Copyright (c) xx025. All rights reserved.
