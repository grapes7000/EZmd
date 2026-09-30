"""Only the Build 01 non-negotiable import boundaries."""

import ast
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "src" / "ezmd"
FORBIDDEN_QT_PREFIXES = (
    "PySide6.QtWebEngine",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtNetwork",
)
FORBIDDEN_NETWORK_MODULES = (
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "socket",
)


def is_forbidden_import(module: str) -> bool:
    return any(module.startswith(prefix) for prefix in FORBIDDEN_QT_PREFIXES) or any(
        module == name or module.startswith(f"{name}.") for name in FORBIDDEN_NETWORK_MODULES
    )


@pytest.mark.parametrize(
    ("module", "forbidden"),
    [
        ("PySide6.QtWebEngineWidgets", True),
        ("PySide6.QtWebEngineCore", True),
        ("PySide6.QtQuickWidgets", True),
        ("PySide6.QtQml", True),
        ("PySide6.QtNetwork", True),
        ("PySide6.QtWidgets", False),
        ("requests.sessions", True),
        ("httpx", True),
        ("aiohttp.client", True),
        ("urllib.request", True),
        ("socket.socket", True),
        ("socketserver", False),
        ("requests_extra", False),
    ],
)
def test_forbidden_import_families(module: str, forbidden: bool) -> None:
    assert is_forbidden_import(module) == forbidden


def test_production_does_not_import_browser_qml_or_network_clients() -> None:
    for path in SOURCE.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module, *(f"{node.module}.{alias.name}" for alias in node.names)]
            for module in modules:
                assert not is_forbidden_import(module), (
                    f"{path.relative_to(SOURCE)} imports {module}"
                )


def test_document_io_does_not_depend_on_visual_profiles() -> None:
    for path in (SOURCE / "core").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ]
        imports.extend(
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        )
        assert not any(name.startswith("ezmd.ui") for name in imports), path
