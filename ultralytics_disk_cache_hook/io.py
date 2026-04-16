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


def resolve_image_path(image_path: str | os.PathLike[str]) -> Path:
    path = Path(image_path).expanduser()
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def get_cache_key_for_image(image_path: str | os.PathLike[str]) -> str:
    resolved = resolve_image_path(image_path)
    return hashlib.md5(resolved.as_posix().encode("utf-8"), usedforsecurity=False).hexdigest()


def get_cache_path_for_image(image_path: str | os.PathLike[str]) -> Path:
    cache_key = get_cache_key_for_image(image_path)
    bucket_parts = [
        cache_key[i * PLUGIN_HASH_BUCKET_WIDTH : (i + 1) * PLUGIN_HASH_BUCKET_WIDTH]
        for i in range(PLUGIN_HASH_BUCKET_LEVELS)
    ]
    return get_plugin_cache_root().joinpath(*bucket_parts, f"{cache_key}.npy")
