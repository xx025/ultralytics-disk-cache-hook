import hashlib
import os
import tempfile
from pathlib import Path

PLUGIN_TMP_ENV = "ULTRALYTICS_DISK_CACHE_TMPDIR"
PLUGIN_CACHE_DIRNAME = "ultralytics-disk-cache"
PLUGIN_HASH_BUCKET_LEVELS = 2
PLUGIN_HASH_BUCKET_WIDTH = 2


def get_plugin_tmp_root() -> Path:
    override = os.environ.get(PLUGIN_TMP_ENV)
    if override:
        return Path(override).expanduser()
    return Path(tempfile.gettempdir())


def get_plugin_cache_root() -> Path:
    return get_plugin_tmp_root() / PLUGIN_CACHE_DIRNAME

def _resolve_source_path(source_path: str | os.PathLike[str]) -> Path:
    path = Path(source_path).expanduser()
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def _get_cache_key(kind: str, source_path: str | os.PathLike[str]) -> str:
    resolved = _resolve_source_path(source_path)
    cache_input = f"{kind}:{resolved.as_posix()}"
    return hashlib.md5(cache_input.encode("utf-8"), usedforsecurity=False).hexdigest()


def _get_bucketed_cache_path(
    kind: str,
    source_path: str | os.PathLike[str],
    suffix: str,
) -> Path:
    cache_key = _get_cache_key(kind, source_path)
    bucket_parts = [
        cache_key[i * PLUGIN_HASH_BUCKET_WIDTH : (i + 1) * PLUGIN_HASH_BUCKET_WIDTH]
        for i in range(PLUGIN_HASH_BUCKET_LEVELS)
    ]
    return get_plugin_cache_root().joinpath(*bucket_parts, f"{cache_key}{suffix}")


def get_cache_key_for_image(image_path: str | os.PathLike[str]) -> str:
    return _get_cache_key("image-npy", image_path)


def get_cache_path_for_image(image_path: str | os.PathLike[str]) -> Path:
    return _get_bucketed_cache_path("image-npy", image_path, ".npy")


def get_cache_path_for_dataset_cache(cache_path: str | os.PathLike[str]) -> Path:
    return _get_bucketed_cache_path("dataset-meta", cache_path, ".cache")
