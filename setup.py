from pathlib import Path
from shutil import copy2

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        super().run()
        root = Path(__file__).parent
        for name in (
            "ultralytics_disk_cache_hook_auto_enable_startup.pth",
            "ultralytics_disk_cache_hook_startup_auto_enable.py",
        ):
            source = root / name
            target = Path(self.build_lib) / source.name
            copy2(source, target)


setup(cmdclass={"build_py": build_py})
