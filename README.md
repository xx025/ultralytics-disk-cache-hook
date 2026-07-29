# ultralytics-disk-cache-hook

Keep Ultralytics disk caches off the dataset filesystem.

When training uses cache="disk", this package redirects image .npy files and dataset .cache files into a local cache directory on the training node. This is useful when datasets live on shared or network storage.

[中文说明](./README.zh-CN.md)

## Install

    pip install ultralytics-disk-cache-hook

The hook auto-enables itself in new Python processes after installation. It supports Ultralytics 8.4.0 through 8.4.84.

## Use

Use Ultralytics normally. Set cache="disk" when you want disk caching:

    from ultralytics import YOLO

    YOLO("yolov8n.pt").train(data="coco128.yaml", cache="disk")

The original dataset directory remains unchanged. Cache files are written under the plugin cache root instead.

## Configuration

| Setting | Default | Purpose |
| --- | --- | --- |
| ULTRALYTICS_DISK_CACHE_TMPDIR | System temporary directory | Parent directory for the plugin cache |
| ULTRALYTICS_IMAGE_DISK_CACHE | 1 | Enable image .npy cache redirection |
| ULTRALYTICS_DATASET_META_CACHE | 1 | Enable dataset .cache redirection |
| ULTRALYTICS_FORCE_DISK_CACHE | 0 | Force BaseDataset cache arguments to disk |

For example, to use local NVMe storage:

    export ULTRALYTICS_DISK_CACHE_TMPDIR=/local_nvme/tmp

Parameter forcing is off by default so normal Ultralytics cache behavior is preserved. In a managed training environment, enable it before Python starts:

    export ULTRALYTICS_FORCE_DISK_CACHE=1

This changes BaseDataset cache values such as false, true, and "ram" to "disk". It does not cover classification datasets.

## Slurm job-local temporary storage

This plugin works well with Slurm job-lifecycle-managed local temporary storage, such as job_container/tmpfs or a site-specific Prolog/Epilog setup. Those mechanisms create private local scratch space for a job and remove its contents when the job ends.

If the job-local directory is mounted as /tmp, no extra setting is needed because that is the default cache parent. If your cluster exposes another job-local path, point the plugin at it:

    export ULTRALYTICS_DISK_CACHE_TMPDIR=/path/to/job-local-scratch

Each job then keeps cache files off the shared dataset filesystem and they are reclaimed with the job-local temporary storage.

## Cache layout

The default cache root is:

    <system-temp-dir>/ultralytics-disk-cache

Each source path is hashed, then stored in two hash-bucket directories. Image caches use .npy and dataset metadata uses .cache.

## Notes

- The plugin patches Ultralytics internals and rejects unsupported versions.
- Disk-space checks are skipped because the cache root may be outside the dataset filesystem. Ensure the selected cache disk has enough free space.
- The upstream proposal for native configurable disk-cache paths is [Add cache_dir support for disk image caching](https://github.com/ultralytics/ultralytics/pull/24271). Follow its progress if you need first-party support.
