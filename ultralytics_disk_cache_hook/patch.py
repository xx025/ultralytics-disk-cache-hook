from __future__ import annotations

from typing import Any

from packaging.version import InvalidVersion, Version

from .io import get_cache_path_for_image, get_plugin_cache_root

MIN_ULTRALYTICS_VERSION = Version("8.4.0")
MAX_ULTRALYTICS_VERSION = Version("8.4.38")
SUPPORTED_ULTRALYTICS_MAJOR_MINOR = (8, 4)


class UnsupportedUltralyticsVersionError(RuntimeError):
    """Raised when the installed ultralytics version is outside the validated range."""


def _parse_version(version: str) -> Version:
    try:
        return Version(version)
    except InvalidVersion as exc:
        raise UnsupportedUltralyticsVersionError(
            "Unable to parse ultralytics version "
            f"{version!r}. This plugin only supports validated versions from "
            f"{MIN_ULTRALYTICS_VERSION} to {MAX_ULTRALYTICS_VERSION}."
        ) from exc


def _validate_ultralytics_version(version: str) -> None:
    parsed = _parse_version(version)
    if parsed < MIN_ULTRALYTICS_VERSION:
        raise UnsupportedUltralyticsVersionError(
            f"ultralytics {version} is not supported by ultralytics-disk-cache-hook. "
            f"Validated support starts at ultralytics {MIN_ULTRALYTICS_VERSION}."
        )
    if parsed.release[:2] != SUPPORTED_ULTRALYTICS_MAJOR_MINOR:
        raise UnsupportedUltralyticsVersionError(
            f"ultralytics {version} is not supported by ultralytics-disk-cache-hook. "
            "Validated support currently covers ultralytics 8.4.x only."
        )
    if parsed > MAX_ULTRALYTICS_VERSION:
        raise UnsupportedUltralyticsVersionError(
            f"ultralytics {version} is not supported by ultralytics-disk-cache-hook. "
            f"Validated support currently covers versions up to {MAX_ULTRALYTICS_VERSION}."
        )


def _rewrite_base_dataset_npy_files(dataset: Any) -> None:
    if hasattr(dataset, "im_files"):
        dataset.npy_files = [get_cache_path_for_image(im_file) for im_file in dataset.im_files]


def _rewrite_classification_samples(dataset: Any) -> None:
    rewritten_samples = []
    for sample in dataset.samples:
        file_name, class_index, _cache_path, image = sample
        rewritten_samples.append([file_name, class_index, get_cache_path_for_image(file_name), image])
    dataset.samples = rewritten_samples


def is_enabled() -> bool:
    try:
        from ultralytics.data.base import BaseDataset
    except ModuleNotFoundError:
        return False
    return bool(getattr(BaseDataset, "_ultralytics_disk_cache_hook_enabled", False))


def enable() -> None:
    import ultralytics
    import ultralytics.data.base as base_module
    import ultralytics.data.dataset as dataset_module

    _validate_ultralytics_version(ultralytics.__version__)

    base_dataset_cls = base_module.BaseDataset
    classification_dataset_cls = dataset_module.ClassificationDataset
    if getattr(base_dataset_cls, "_ultralytics_disk_cache_hook_enabled", False):
        print(
            "[ultralytics-disk-cache-hook] already enabled, "
            f"cache root: {get_plugin_cache_root()}"
        )
        return

    original_base_init = base_dataset_cls.__init__
    original_base_load_image = base_dataset_cls.load_image
    original_base_cache_images = base_dataset_cls.cache_images
    original_base_cache_images_to_disk = base_dataset_cls.cache_images_to_disk
    original_base_check_cache_disk = base_dataset_cls.check_cache_disk
    original_classification_init = classification_dataset_cls.__init__
    original_classification_getitem = classification_dataset_cls.__getitem__

    def patched_base_init(self, *args: Any, **kwargs: Any) -> None:
        original_base_init(self, *args, **kwargs)
        if getattr(self, "cache", None) == "disk":
            _rewrite_base_dataset_npy_files(self)

    def patched_base_load_image(self, i: int, rect_mode: bool = True):
        if getattr(self, "cache", None) == "disk":
            self.npy_files[i] = get_cache_path_for_image(self.im_files[i])
        return original_base_load_image(self, i, rect_mode=rect_mode)

    def patched_base_cache_images(self) -> None:
        if getattr(self, "cache", None) == "disk":
            _rewrite_base_dataset_npy_files(self)
        return original_base_cache_images(self)

    def patched_base_cache_images_to_disk(self, i: int) -> None:
        cache_path = get_cache_path_for_image(self.im_files[i])
        self.npy_files[i] = cache_path
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        return original_base_cache_images_to_disk(self, i)

    def patched_base_check_cache_disk(self, safety_margin: float = 0.5) -> bool:
        cache_root = get_plugin_cache_root()
        base_module.LOGGER.warning(
            f"{self.prefix}Disk cache space checks are skipped by ultralytics-disk-cache-hook. "
            f"Plugin cache root is {cache_root}. Please manage available disk space yourself."
        )
        return True

    def patched_classification_init(self, *args: Any, **kwargs: Any) -> None:
        original_classification_init(self, *args, **kwargs)
        if getattr(self, "cache_disk", False):
            _rewrite_classification_samples(self)

    def patched_classification_getitem(self, i: int):
        if getattr(self, "cache_disk", False):
            file_name, class_index, _cache_path, image = self.samples[i]
            cache_path = get_cache_path_for_image(file_name)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.samples[i] = [file_name, class_index, cache_path, image]
        return original_classification_getitem(self, i)

    base_dataset_cls.__init__ = patched_base_init
    base_dataset_cls.load_image = patched_base_load_image
    base_dataset_cls.cache_images = patched_base_cache_images
    base_dataset_cls.cache_images_to_disk = patched_base_cache_images_to_disk
    base_dataset_cls.check_cache_disk = patched_base_check_cache_disk
    classification_dataset_cls.__init__ = patched_classification_init
    classification_dataset_cls.__getitem__ = patched_classification_getitem

    base_dataset_cls._ultralytics_disk_cache_hook_enabled = True
    base_dataset_cls._ultralytics_disk_cache_hook_original_init = original_base_init
    base_dataset_cls._ultralytics_disk_cache_hook_original_load_image = original_base_load_image
    base_dataset_cls._ultralytics_disk_cache_hook_original_cache_images = original_base_cache_images
    base_dataset_cls._ultralytics_disk_cache_hook_original_cache_images_to_disk = original_base_cache_images_to_disk
    base_dataset_cls._ultralytics_disk_cache_hook_original_check_cache_disk = original_base_check_cache_disk
    classification_dataset_cls._ultralytics_disk_cache_hook_original_init = original_classification_init
    classification_dataset_cls._ultralytics_disk_cache_hook_original_getitem = original_classification_getitem

    print(
        "[ultralytics-disk-cache-hook] enabled, "
        f"ultralytics={ultralytics.__version__}, "
        f"cache root: {get_plugin_cache_root()}"
    )
