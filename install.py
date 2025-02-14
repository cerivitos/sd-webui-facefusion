#!/usr/bin/env python3

from pathlib import Path

import launch
import pkg_resources
from typing import Optional

_REQUIREMENT_PATH = Path(__file__).absolute().parent / "requirements.txt"


def _get_comparable_version(version: str) -> tuple:
    return tuple(version.split("."))


def _get_installed_version(package: str) -> Optional[str]:
    try:
        return pkg_resources.get_distribution(package).version
    except Exception:
        return None


if not launch.is_installed("onnxruntime") and not launch.is_installed("onnxruntime-gpu"):
    import torch.cuda as cuda

    if cuda.is_available():
        launch.run_pip('install "onnxruntime-gpu>=1.16.3"')
    else:
        launch.run_pip('install "onnxruntime>=1.16.3"')


with _REQUIREMENT_PATH.open() as fp:
    for requirement in fp:
        try:
            requirement = requirement.strip()
            if "==" in requirement:
                name, version = requirement.split("==", 1)
                installed_version = _get_installed_version(name)

                if installed_version == version:
                    continue

                launch.run_pip(
                    f'install -U "{requirement}"',
                    f"sd-webui-facefusion requirement: changing {name} version from {installed_version} to {version}",
                )
                continue

            if ">=" in requirement:
                name, version = requirement.split(">=", 1)
                installed_version = _get_installed_version(name)

                if installed_version and (
                    _get_comparable_version(installed_version) >= _get_comparable_version(version)
                ):
                    continue

                launch.run_pip(
                    f'install -U "{requirement}"',
                    f"sd-webui-facefusion requirement: changing {name} version from {installed_version} to {version}",
                )
                continue

            if not launch.is_installed(requirement):
                launch.run_pip(
                    f'install "{requirement}"',
                    f"sd-webui-facefusion requirement: {requirement}",
                )
        except Exception as error:
            print(error)
            print(f"Warning: Failed to install '{requirement}', some preprocessors may not work.")
