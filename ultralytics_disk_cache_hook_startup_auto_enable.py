import os


def _env_enabled(name: str, default: str = "1") -> bool:
    return os.getenv(name, default).strip().lower() not in {"0", "false", "no", "off"}


try:
    from ultralytics_disk_cache_hook.patch import enable

    enable(
        force_disk_cache=_env_enabled("ULTRALYTICS_FORCE_DISK_CACHE", "0"),
        image_disk_cache=_env_enabled("ULTRALYTICS_IMAGE_DISK_CACHE", "1"),
        dataset_meta_cache=_env_enabled("ULTRALYTICS_DATASET_META_CACHE", "1"),
    )
except Exception:
    pass
