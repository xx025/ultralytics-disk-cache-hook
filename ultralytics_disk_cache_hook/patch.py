"""Public entry point that coordinates the cache hook modules."""

from __future__ import annotations

from packaging.version import InvalidVersion, Version

from . import cache_disk, force_disk

MIN_ULTRALYTICS_VERSION = Version("8.4.0")
MAX_ULTRALYTICS_VERSION = Version("8.4.84")
SUPPORTED_ULTRALYTICS_MAJOR_MINOR = (8, 4)
REPOSITORY_URL = "https://github.com/xx025/ultralytics-disk-cache-hook"
UPSTREAM_CACHE_PATH_PR_URL = "https://github.com/ultralytics/ultralytics/pull/24271"
_upstream_pr_announced = False


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


def _announce_upstream_pr() -> None:
    """Print the upstream native cache-path proposal once per Python process."""
    global _upstream_pr_announced
    if not _upstream_pr_announced:
        print(
            "[ultralytics-disk-cache-hook] "
            f"Repository: {REPOSITORY_URL}"
        )
        print(
            "[ultralytics-disk-cache-hook] "
            f"Native cache-path support proposal: {UPSTREAM_CACHE_PATH_PR_URL}"
        )
        _upstream_pr_announced = True


def enable(
    *,
    force_disk_cache: bool = False,
    image_disk_cache: bool = True,
    dataset_meta_cache: bool = True,
) -> None:
    """Enable the requested cache hook modules."""
    import ultralytics
    from ultralytics.data.base import BaseDataset

    _validate_ultralytics_version(ultralytics.__version__)
    _announce_upstream_pr()

    if force_disk_cache:
        force_disk.enable(BaseDataset)

    if image_disk_cache or dataset_meta_cache:
        cache_disk.enable(
            image_disk_cache=image_disk_cache,
            dataset_meta_cache=dataset_meta_cache,
        )
    elif not force_disk_cache:
        print("[ultralytics-disk-cache-hook] enable() called with all hooks disabled, nothing to do.")
