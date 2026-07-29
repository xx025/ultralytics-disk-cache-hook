"""Force Ultralytics dataset constructors to use disk image caching."""

from __future__ import annotations

import inspect
from typing import Any


def _call_with_disk_cache(original_init: Any, *args: Any, **kwargs: Any) -> None:
    """Call a dataset constructor after replacing its cache argument with disk."""
    signature = inspect.signature(original_init)
    if "cache" not in signature.parameters:
        return original_init(*args, **kwargs)

    print(
        "[ultralytics-disk-cache-hook] "
        f"raw {args[0].__class__.__name__ if args else 'dataset'} init args={args[1:]!r}, kwargs={kwargs!r}"
    )
    bound = signature.bind_partial(*args, **kwargs)
    original_cache = bound.arguments.get("cache", signature.parameters["cache"].default)
    dataset_name = args[0].__class__.__name__ if args else "dataset"
    if original_cache == "disk":
        print(f"[ultralytics-disk-cache-hook] disk cache already selected for {dataset_name}")
    else:
        print(
            "[ultralytics-disk-cache-hook] "
            f"force disk cache for {dataset_name}: {original_cache!r} -> 'disk'"
        )
    bound.arguments["cache"] = "disk"
    return original_init(*bound.args, **bound.kwargs)


def is_enabled() -> bool:
    """Return whether the force-disk-cache patch has been installed."""
    try:
        from ultralytics.data.base import BaseDataset
    except ModuleNotFoundError:
        return False
    return bool(getattr(BaseDataset, "_ultralytics_force_disk_cache_enabled", False))


def enable(base_dataset_cls: Any) -> None:
    """Patch the shared Ultralytics base dataset constructor to use disk caching."""
    if getattr(base_dataset_cls, "_ultralytics_force_disk_cache_enabled", False):
        return

    original_base_init = base_dataset_cls.__init__
    def patched_base_init(self, *args: Any, **kwargs: Any) -> None:
        return _call_with_disk_cache(original_base_init, self, *args, **kwargs)

    base_dataset_cls.__init__ = patched_base_init

    base_dataset_cls._ultralytics_force_disk_cache_enabled = True
    base_dataset_cls._ultralytics_force_disk_cache_original_init = original_base_init
