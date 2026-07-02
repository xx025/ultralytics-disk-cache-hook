# ultralytics-disk-cache-hook

Redirect `ultralytics` cache files away from the dataset directory and into a local cache root on the training node.

[中文说明](./README.zh-CN.md)

## Quick Start

```bash
pip install ultralytics-disk-cache-hook
```

Install by your existing `ultralytics` version:

| Installed `ultralytics` | Recommended `ultralytics-disk-cache-hook` | Install command |
| --- | --- | --- |
| `8.4.39 <= ultralytics <= 8.4.84` | `0.2.1` | `pip install "ultralytics-disk-cache-hook==0.2.1"` |
| `8.4.0 <= ultralytics <= 8.4.38` | `0.2.1` | `pip install "ultralytics-disk-cache-hook==0.2.1"` |
| Reproduce an older environment pinned to `<= 8.4.38` | `0.2.0` | `pip install "ultralytics-disk-cache-hook==0.2.0"` |
| `ultralytics < 8.4.0` | Not supported | Do not install this plugin version |
| `ultralytics > 8.4.84` | Not yet validated | Wait for a newer hook release or verify source compatibility first |

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(data="coco128.yaml", cache="disk")
```

After installation, the package auto-enables itself for new Python processes via the
`ultralytics_disk_cache_hook_auto_enable_startup.pth` file in `site-packages`.

## Configuration

You can control the startup defaults and cache root with environment variables:

```bash
export ULTRALYTICS_IMAGE_DISK_CACHE=1
export ULTRALYTICS_DATASET_META_CACHE=0
export ULTRALYTICS_DISK_CACHE_TMPDIR=/local_nvme/tmp
```

Supported false values are `0`, `false`, `no`, and `off`.

The cache root defaults to `tempfile.gettempdir() / "ultralytics-disk-cache"` when `ULTRALYTICS_DISK_CACHE_TMPDIR` is not set.

If you disable or bypass the startup defaults and want to control the hooks explicitly in code:

```python
from ultralytics_disk_cache_hook import enable

enable(image_disk_cache=True, dataset_meta_cache=False)
enable(image_disk_cache=False, dataset_meta_cache=True)
```

## What It Does

When `ultralytics` runs with `cache="disk"`, it writes `*.npy` cache files next to the original images by default.

It also writes dataset metadata `*.cache` files such as `labels/train.cache`, `annotations.cache`, or `dataset_root.cache` next to the dataset source paths.

This plugin monkey patches the internal dataset implementation and redirects those cache files into a local temporary cache root instead.

- By default affects `cache="disk"` image caches
- By default affects dataset metadata `*.cache` files
- Lets you disable either hook independently via environment variables or `enable(...)`
- Does not affect `cache="ram"` or disabled cache
- Rewrites `self.npy_files` for detection, segmentation, pose, and other tasks built on `BaseDataset`
- Rewrites `*.npy` paths inside `ClassificationDataset.samples` for classification tasks
- Can redirect dataset metadata cache helpers shared by detection, grounding, and classification datasets
- Writes cache files into hash buckets instead of mirroring the original dataset directory tree

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

Validated range: `8.4.0 <= ultralytics <= 8.4.84`.

Use `ultralytics-disk-cache-hook==0.2.1` for the whole validated range. Use `0.2.0` only to reproduce an older environment pinned to `<= 8.4.38`.

Outside that range, `enable()` raises `UnsupportedUltralyticsVersionError`.

Why:

- `v8.0.x` still uses the old `ultralytics/yolo/data/...` layout
- `v8.1.x` through `v8.3.x` do not match the internal hook points used by this patch
- Starting from `v8.4.0`, the `disk cache` structure in `BaseDataset` and `ClassificationDataset` matches this plugin

As of `2026-07-02`, I checked the hook points against `v8.4.84`, and those patched code paths still match `main`.

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
- `v8.4.84` release: https://github.com/ultralytics/ultralytics/releases/tag/v8.4.84

## Copyright

Copyright (c) xx025. All rights reserved.
