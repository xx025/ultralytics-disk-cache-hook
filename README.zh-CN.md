# ultralytics-disk-cache-hook

[English README](./README.md)

把 Ultralytics 的磁盘缓存从数据集目录重定向到训练节点的本地缓存目录。

当训练使用 cache="disk" 时，插件会把图片 .npy 缓存和数据集 .cache 元数据缓存写到本地目录，避免向共享存储或网络存储中的数据集目录写入大量缓存文件。

## 安装

    pip install ultralytics-disk-cache-hook

安装后，新的 Python 进程会自动启用 Hook。当前支持 Ultralytics 8.4.0 到 8.4.84。

## 使用

按正常方式训练；需要磁盘缓存时传入 cache="disk"：

    from ultralytics import YOLO

    YOLO("yolov8n.pt").train(data="coco128.yaml", cache="disk")

数据集原始目录不会被写入缓存文件，缓存会写到插件缓存根目录。

## 配置

| 设置 | 默认值 | 用途 |
| --- | --- | --- |
| ULTRALYTICS_DISK_CACHE_TMPDIR | 系统临时目录 | 插件缓存的父目录 |
| ULTRALYTICS_IMAGE_DISK_CACHE | 1 | 启用图片 .npy 缓存重定向 |
| ULTRALYTICS_DATASET_META_CACHE | 1 | 启用数据集 .cache 重定向 |
| ULTRALYTICS_FORCE_DISK_CACHE | 0 | 强制 BaseDataset 使用磁盘缓存 |

例如，把缓存放到本地 NVMe：

    export ULTRALYTICS_DISK_CACHE_TMPDIR=/local_nvme/tmp

强制参数默认关闭，以保留 Ultralytics 原本的缓存行为。在受控训练环境中，可在启动 Python 前启用：

    export ULTRALYTICS_FORCE_DISK_CACHE=1

启用后，BaseDataset 的 false、true 和 "ram" 等缓存值会被改为 "disk"。分类数据集不在此强制范围内。

## Slurm 作业本地临时存储

该插件可配合 Slurm 按作业生命周期管理的本地临时存储使用，例如 job_container/tmpfs，或集群通过 Prolog/Epilog 配置的等效机制。这类机制会为作业创建私有本地临时空间，并在作业结束后清理其中内容。

如果作业本地目录挂载为 /tmp，无需额外设置，因为它正是默认缓存父目录。如果集群提供了其他作业本地路径，可将插件指向该路径：

    export ULTRALYTICS_DISK_CACHE_TMPDIR=/path/to/job-local-scratch

这样每个作业都会把缓存保存在本地临时存储中，避免写入共享数据集文件系统，并随作业临时空间一起回收。

## 缓存路径

默认缓存根目录：

    <系统临时目录>/ultralytics-disk-cache

插件会根据源路径计算哈希，并使用两级哈希目录存放文件。图片缓存后缀为 .npy，数据集元数据后缀为 .cache。

## 说明

- 插件会修改 Ultralytics 内部实现，遇到不受支持的版本会拒绝启用。
- 因为缓存目录可能不在数据集文件系统中，插件不会检查磁盘空间；请自行确保缓存盘空间充足。
- Ultralytics 的原生可配置磁盘缓存路径提案：[Add cache_dir support for disk image caching](https://github.com/ultralytics/ultralytics/pull/24271)。如需官方支持，可关注该 PR 进度。
