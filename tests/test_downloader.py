from __future__ import annotations

import contextlib
import http.server
import socket
import threading
from pathlib import Path

import pytest

import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from uoa_toolkit import cli
from uoa_toolkit.downloader import (
    DownloadError,
    RemoteDataset,
    download_dataset,
    download_datasets,
    generate_python_snippet,
)


@contextlib.contextmanager
def http_server(root: Path):
    """Serve files from ``root`` using a background HTTP server."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root), **kwargs)

        def log_message(self, format, *args):  # pragma: no cover - noisy logging
            return

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        host, port = sock.getsockname()

    server = http.server.ThreadingHTTPServer((host, port), Handler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        thread.join()


@pytest.fixture
def patched_datasets(monkeypatch, tmp_path):
    sample_file = tmp_path / "source" / "dataset.csv"
    sample_file.parent.mkdir()
    sample_file.write_text("alpha,beta\n1,2\n", encoding="utf-8")

    with http_server(sample_file.parent) as base_url:
        dataset = RemoteDataset(
            slug="sample_dataset",
            title="Sample Dataset",
            description="Tiny CSV for tests.",
            landing_page="https://example.com/sample",
            download_url=f"{base_url}/{sample_file.name}",
            filename="dataset.csv",
        )

        monkeypatch.setattr(cli, "list_datasets", lambda: (dataset,))
        monkeypatch.setattr(cli, "download_multiple", download_datasets)
        monkeypatch.setattr(cli, "generate_python_snippet", generate_python_snippet)
        monkeypatch.setattr(cli, "DownloadError", DownloadError)

        from uoa_toolkit import downloader

        monkeypatch.setattr(downloader, "REMOTE_DATASETS", (dataset,))
        monkeypatch.setattr(downloader, "_dataset_index", lambda: {dataset.slug: dataset})
        yield dataset


def test_download_dataset(tmp_path, patched_datasets):
    target = tmp_path / "downloads"
    path = download_dataset("sample_dataset", target)
    assert path.exists()
    assert path.read_text(encoding="utf-8").splitlines() == ["alpha,beta", "1,2"]


def test_download_snippet_generation(tmp_path):
    snippet = generate_python_snippet(["foo", "bar"], tmp_path)
    assert "download_datasets" in snippet
    assert "'foo'" in snippet and "'bar'" in snippet
    assert str(tmp_path) in snippet


def test_cli_downloads_dataset(tmp_path, patched_datasets, capsys):
    cli.download_datasets(slugs=[patched_datasets.slug], data_root=tmp_path)
    captured = capsys.readouterr()
    assert "saved to" in captured.out
    downloaded = tmp_path / "sample_dataset" / "dataset.csv"
    assert downloaded.exists()


def test_cli_emit_code(tmp_path, patched_datasets, capsys):
    cli.download_datasets(
        slugs=[patched_datasets.slug],
        data_root=tmp_path,
        emit_code=True,
        dry_run=True,
    )
    captured = capsys.readouterr()
    assert "download_datasets" in captured.out

