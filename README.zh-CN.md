

# ultralytics-disk-cache-hook

[English README](./README.md)

`ultralytics` 默认会把训练期产生的缓存文件直接写回数据集所在目录。

这在共享存储或网络存储训练场景下通常不够友好：

- 会往共享数据目录回写大量小文件
- 容易放大元数据压力
- 训练节点的本地磁盘无法被优先利用

这个插件通过 monkey patch `ultralytics` 的内部数据集实现，把 `disk cache` 重定向到训练节点上的本地缓存目录。



## 快速开始

```python
from ultralytics_disk_cache_hook import enable
from ultralytics import YOLO

enable()

model = YOLO("yolov8n.pt")
model.train(data="coco128.yaml", cache="disk")
```

安装后，包还会通过放在 `site-packages` 里的
`ultralytics_disk_cache_hook_auto_enable_startup.pth` 文件，为新的 Python 进程自动执行一次 `enable()`。

`enable()` 现在默认会同时开启两类 hook，也可以分别控制：

```python
from ultralytics_disk_cache_hook import enable

enable(image_disk_cache=True, dataset_meta_cache=True)
enable(image_disk_cache=True, dataset_meta_cache=False)
enable(image_disk_cache=False, dataset_meta_cache=True)
```

## 行为说明

- 默认影响 `cache="disk"` 产生的图片 `*.npy`
- 默认影响数据集元信息 `*.cache`
- 可通过 `enable(image_disk_cache=..., dataset_meta_cache=...)` 分别关闭任意一类 hook
- 不影响 `cache="ram"` 或不缓存
- 检测、分割、姿态等基于 `BaseDataset` 的任务会重写 `self.npy_files`
- 分类任务会重写 `ClassificationDataset.samples` 中的 `*.npy` 路径
- 检测 / grounding / 分类共享的 `load_dataset_cache_file()`、`save_dataset_cache_file()` 也可被重定向
- 缓存路径不会按原始目录展开，而是写入哈希桶目录

## 缓存根目录

缓存根目录优先取 `ULTRALYTICS_DISK_CACHE_TMPDIR`，否则使用 `tempfile.gettempdir()`，然后在其下追加 `ultralytics-disk-cache`。

可通过环境变量覆盖：

```bash
export ULTRALYTICS_DISK_CACHE_TMPDIR=/local_nvme/tmp
```

缓存路径示例：

```text
/mnt/shared-storage/datasets/coco/images/train2017/000000000001.jpg
-> <cache-root>/d1/3f/d13f474cca61f46ba06ecba11c1b3046.npy
```

数据集元信息缓存路径示例：

```text
/mnt/shared-storage/datasets/coco/labels/train.cache
-> <cache-root>/7a/9c/7a9c5f8af885b2f5c6c2f67066342c0a.cache
```

## 版本支持

插件内部直接 monkey patch 了 `ultralytics` 的非公开实现，因此只能声明对“已核对源码结构”的版本负责。

当前代码里已经做了强制限制：

- 最低支持版本：`8.4.0`
- 最高已验证版本：`8.4.38`
- 当前允许范围：`8.4.0 <= ultralytics <= 8.4.38`

超出范围时，`enable()` 会直接抛出 `UnsupportedUltralyticsVersionError`。

原因：

- `v8.0.x` 仍使用旧目录结构 `ultralytics/yolo/data/...`
- `v8.1.x` 到 `v8.3.x` 的内部实现与当前 patch 依赖的切点不一致
- `v8.4.0` 起，`BaseDataset` / `ClassificationDataset` 的 `disk cache` 结构与当前插件对齐

这份范围是基于 GitHub 上已检查的源码和 release/tag 结果确定的；截至 `2026-04-17`，我核对到的最新 release 是 `v8.4.38`。

查看当前环境中的 `ultralytics` 版本：

```bash
python -c "import ultralytics; print(ultralytics.__version__)"
```

## 磁盘空间说明

这个插件当前不会替你检查缓存盘空间是否足够。

启用 `cache="disk"` 时，插件会打印 warning，提示缓存目录位置，并明确要求使用者自行管理磁盘空间。

如果本地缓存盘被写满，报错会发生在实际写入 `*.npy` 文件时。

## 参考链接

- Ultralytics releases: https://github.com/ultralytics/ultralytics/releases
- Ultralytics tags: https://github.com/ultralytics/ultralytics/tags
- `v8.4.38` release: https://github.com/ultralytics/ultralytics/releases/tag/v8.4.38

## 版权声明

Copyright (c) xx025. All rights reserved.
