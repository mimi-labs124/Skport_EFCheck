from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

VALID_MODES = {"onedir", "onefile"}


def build_layout(project_root: Path) -> dict[str, Path]:
    return {
        "project_root": project_root,
        "build_root": project_root / "build" / "pyinstaller",
        "onedir_build": project_root / "build" / "pyinstaller" / "onedir",
        "onefile_build": project_root / "build" / "pyinstaller" / "onefile",
        "onedir_dist": project_root / "dist" / "pyinstaller" / "onedir",
        "onefile_dist": project_root / "dist" / "pyinstaller" / "onefile",
        "releases_dir": project_root / "dist" / "releases",
    }


def release_manifest(mode: str) -> list[str]:
    validate_mode(mode)
    return [
        "README.md",
        "README.zh-TW.md",
        "LICENSE",
        "SECURITY.md",
        "install_efcheck.bat",
        "setup_windows.bat",
        "capture_session.bat",
        "run_signin.bat",
        "register_logon_task.bat",
        "register_logon_task.ps1",
        "config/settings.example.json",
    ]


def build_pyinstaller(mode: str, project_root: Path) -> Path:
    validate_mode(mode)
    layout = build_layout(project_root)
    spec_path = project_root / "packaging" / "efcheck.spec"
    dist_dir = layout[f"{mode}_dist"]
    work_dir = layout[f"{mode}_build"]
    dist_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["EFCHECK_PYINSTALLER_MODE"] = mode
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        str(spec_path),
    ]
    subprocess.run(command, check=True, cwd=project_root, env=env)
    return dist_dir


def create_release_tree(mode: str, project_root: Path) -> Path:
    validate_mode(mode)
    layout = build_layout(project_root)
    releases_dir = layout["releases_dir"]
    release_root = releases_dir / f"EFCheck-Windows-{mode}"
    if release_root.exists():
        shutil.rmtree(release_root)
    release_root.mkdir(parents=True, exist_ok=True)

    build_output = built_executable_root(mode, project_root)
    if mode == "onedir":
        copy_tree_contents(build_output, release_root)
    else:
        shutil.copy2(build_output / "efcheck.exe", release_root / "efcheck.exe")

    for relative_path in release_manifest(mode):
        source = project_root / relative_path
        target = release_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    return release_root


def create_release_zip(mode: str, project_root: Path) -> Path:
    release_root = create_release_tree(mode, project_root)
    archive_base = str(release_root)
    zip_path = shutil.make_archive(archive_base, "zip", release_root)
    return Path(zip_path)


def built_executable_root(mode: str, project_root: Path) -> Path:
    validate_mode(mode)
    layout = build_layout(project_root)
    dist_dir = layout[f"{mode}_dist"]
    if mode == "onedir":
        return dist_dir / "efcheck"
    return dist_dir


def copy_tree_contents(source_dir: Path, target_dir: Path) -> None:
    for item in source_dir.iterdir():
        destination = target_dir / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def validate_mode(mode: str) -> None:
    if mode not in VALID_MODES:
        raise ValueError(f"Unsupported packaging mode: {mode}")
