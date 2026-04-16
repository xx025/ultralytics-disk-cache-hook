# ultralytics-disk-cache-hook

When `ultralytics` runs with `cache="disk"`, it stores image caches as `*.npy` files next to the original images by default.

That behavior is usually unfriendly for NFS-based training:

- It writes a large number of small files back into the shared dataset directory.
- It increases metadata pressure on the shared filesystem.
- It does not take advantage of local disks on training nodes.

This plugin monkey patches the internal `ultralytics` dataset implementation and redirects disk cache files into a local temporary directory.

## Behavior

- Only affects `cache="disk"`
- Does not affect `cache="ram"` or disabled cache
- Rewrites `self.npy_files` for detection, segmentation, pose, and other tasks built on `BaseDataset`
- Rewrites `*.npy` paths inside `ClassificationDataset.samples` for classification tasks
- Writes cache files into hash buckets instead of mirroring the original dataset directory tree

Default cache root:

```text
/tmp/ultralytics-disk-cache
```

Override it with an environment variable:

```bash
export ULTRALYTICS_DISK_CACHE_TMPDIR=/local_nvme/tmp
```

Example cache path:

```text
/mnt/nfs/datasets/coco/images/train2017/000000000001.jpg
-> /tmp/ultralytics-disk-cache/d1/3f/d13f474cca61f46ba06ecba11c1b3046.npy
```

## Usage

Enable the plugin before training:

```python
from ultralytics_disk_cache_hook import enable
from ultralytics import YOLO

enable()

model = YOLO("yolov8n.pt")
model.train(data="coco128.yaml", cache="disk")
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

## Check Your Installed Version

Check the `ultralytics` version in the current environment:

```bash
python -c "import ultralytics; print(ultralytics.__version__)"
```

Or:

```bash
pip show ultralytics
```

## Disk Space

This plugin does not currently validate whether the cache disk has enough free space.

When `cache="disk"` is enabled, the plugin prints a warning with the cache root and explicitly asks the user to manage disk space manually.

If the local cache disk fills up, the error will occur when `*.npy` files are actually being written.

## Public API

```python
from ultralytics_disk_cache_hook import (
    MAX_ULTRALYTICS_VERSION,
    MIN_ULTRALYTICS_VERSION,
    UnsupportedUltralyticsVersionError,
    enable,
    get_cache_path_for_image,
    get_plugin_cache_root,
    get_plugin_tmp_root,
    is_enabled,
)
```

## Packaging and Publishing

The repository now includes two GitHub Actions workflows:

- `.github/workflows/build.yml`
  Purpose: build `sdist` and `wheel` on `push`, `pull_request`, and manual runs, then run `twine check`
- `.github/workflows/publish.yml`
  Purpose: build and publish the package to PyPI after a GitHub Release is published

### Build Locally

```bash
python -m pip install --upgrade build
python -m build
```

Artifacts will be created in:

```text
dist/
```

### Publish to PyPI Automatically

The current workflow uses PyPI Trusted Publishing, so you do not need to store a PyPI API token in GitHub Secrets.

You need to configure a Trusted Publisher in the PyPI project settings with values like:

- Owner: `xx025`
- Repository name: `ultralytics-disk-cache-hook`
- Workflow name: `publish.yml`
- Environment name: `pypi`

After that, the usual release flow is:

1. Update `__version__` in `ultralytics_disk_cache_hook/__init__.py`
2. Commit and push the changes
3. Create a GitHub Release
4. Let `publish.yml` build and publish the package to PyPI automatically

If you only want to validate packaging first, run `build.yml` manually.

## References

- Ultralytics releases: https://github.com/ultralytics/ultralytics/releases
- Ultralytics tags: https://github.com/ultralytics/ultralytics/tags
- `v8.4.38` release: https://github.com/ultralytics/ultralytics/releases/tag/v8.4.38
- PyPI Trusted Publishing: https://docs.pypi.org/trusted-publishers/
