"""Function tools for rust-analyzer-backed Rust LSP queries."""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path
from shutil import which
from typing import Any, Awaitable, Callable, TypeVar
from urllib.parse import urlparse

# REQUIRED: Adjust parents[] if the card is not stored at .fast-agent/agent-cards/.
_REPO_ROOT = Path(__file__).resolve().parents[2]

# RECOMMENDED: Narrow LSP access to the parts of the repo you actually want queried.
# Use {"."} to allow the entire repo.
_ALLOWED_DIRS = {"src", "crates", "tests", "examples", "benches"}
_ALLOWED_FILES = {"build.rs"}

_server_lock = asyncio.Lock()
_server: "RustAnalyzerClient | None" = None

_CONTENT_MODIFIED_RETRY_ATTEMPTS = 2
_CONTENT_MODIFIED_BASE_DELAY_SECONDS = 0.05

_ReturnT = TypeVar("_ReturnT")


def _resolve_rust_analyzer_cmd() -> str:
    executable = which("rust-analyzer")
    if executable is None:
        raise RuntimeError(
            "rust-analyzer is not available on PATH. "
            "Install it with: rustup component add rust-analyzer"
        )

    completed = subprocess.run(
        [executable, "--version"],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if completed.returncode != 0:
        details = (completed.stderr or completed.stdout or "").strip() or "no output"
        raise RuntimeError(
            "rust-analyzer was found on PATH but is not installed correctly.\n"
            f"Command: {executable} --version\n"
            f"Output: {details}"
        )
    return executable


def _allow_all_paths() -> bool:
    return "." in _ALLOWED_DIRS


def _allowed_path_error() -> str:
    if _allow_all_paths():
        return ""
    if _ALLOWED_DIRS and _ALLOWED_FILES:
        allowed_dirs = ", ".join(sorted(_ALLOWED_DIRS))
        allowed_files = ", ".join(sorted(_ALLOWED_FILES))
        return f"Path must live under one of: {allowed_dirs}; or be one of: {allowed_files}."
    if _ALLOWED_DIRS:
        allowed_dirs = ", ".join(sorted(_ALLOWED_DIRS))
        return f"Path must live under {allowed_dirs}."
    if _ALLOWED_FILES:
        allowed_files = ", ".join(sorted(_ALLOWED_FILES))
        return f"Path must be one of: {allowed_files}."
    return "Path is not allowed. Configure _ALLOWED_DIRS or _ALLOWED_FILES."


def _path_is_allowed(relative_path: Path) -> bool:
    if _allow_all_paths():
        return True
    if len(relative_path.parts) == 1:
        return relative_path.name in _ALLOWED_FILES
    return relative_path.parts[0] in _ALLOWED_DIRS


def _resolve_relative_path(file_path: str) -> str:
    path = Path(file_path)
    path = (_REPO_ROOT / path).resolve() if not path.is_absolute() else path.resolve()

    try:
        relative_path = path.relative_to(_REPO_ROOT)
    except ValueError as exc:
        raise ValueError("Path is outside the repository root.") from exc

    if not relative_path.parts:
        raise ValueError("Path must point to a file within the repository.")

    if not _path_is_allowed(relative_path):
        raise ValueError(_allowed_path_error())

    if not path.exists():
        raise ValueError(f"File not found: {path}")

    if path.suffix != ".rs":
        raise ValueError("Only Rust source files (.rs) are supported by this helper.")

    return str(relative_path)


def _relative_path_to_uri(relative_path: str) -> str:
    return (_REPO_ROOT / relative_path).resolve().as_uri()


def _uri_to_relative(uri: str | None) -> str:
    if not uri:
        return ""
    if uri.startswith("file:"):
        parsed = urlparse(uri)
        path = Path(parsed.path)
        try:
            return str(path.relative_to(_REPO_ROOT))
        except ValueError:
            return str(path)
    return uri


def _format_range(range_data: dict[str, Any] | None) -> str:
    if not range_data:
        return ""
    start = range_data.get("start", {})
    line = start.get("line")
    character = start.get("character")
    if line is None or character is None:
        return ""
    return f"{line + 1}:{character + 1}"


def _format_locations(locations: list[dict[str, Any]]) -> str:
    if not locations:
        return "No locations returned."

    lines = ["| path | line |", "| --- | --- |"]
    for location in locations:
        path = location.get("relativePath") or _uri_to_relative(location.get("uri"))
        line = _format_range(location.get("range"))
        lines.append(f"| {path} | {line} |")
    return "\n".join(lines)


def _format_hover_contents(contents: Any) -> str:
    if contents is None:
        return "No hover contents returned."
    if isinstance(contents, str):
        return contents
    if isinstance(contents, list):
        return "\n\n".join(_format_hover_contents(item) for item in contents)
    if isinstance(contents, dict):
        value = contents.get("value")
        if isinstance(value, str):
            return value
        return json.dumps(contents, indent=2)
    return str(contents)


def _symbol_kind_name(kind: Any) -> str:
    if not isinstance(kind, int):
        return str(kind or "")
    return {
        1: "File",
        2: "Module",
        3: "Namespace",
        4: "Package",
        5: "Class",
        6: "Method",
        7: "Property",
        8: "Field",
        9: "Constructor",
        10: "Enum",
        11: "Interface",
        12: "Function",
        13: "Variable",
        14: "Constant",
        15: "String",
        16: "Number",
        17: "Boolean",
        18: "Array",
        19: "Object",
        20: "Key",
        21: "Null",
        22: "EnumMember",
        23: "Struct",
        24: "Event",
        25: "Operator",
        26: "TypeParameter",
    }.get(kind, str(kind))


def _flatten_symbols(symbols: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []

    def visit(symbol: dict[str, Any]) -> None:
        flattened.append(symbol)
        for child in symbol.get("children", []):
            if isinstance(child, dict):
                visit(child)

    for symbol in symbols:
        visit(symbol)
    return flattened


def _format_symbols(symbols: list[dict[str, Any]], *, default_path: str = "") -> str:
    flattened = _flatten_symbols(symbols)
    if not flattened:
        return "No symbols returned."

    lines = ["| name | kind | location | detail |", "| --- | --- | --- | --- |"]
    for symbol in flattened:
        path = default_path
        if "location" in symbol:
            location = symbol.get("location", {})
            path = _uri_to_relative(location.get("uri")) or path
            range_data = location.get("range")
        else:
            range_data = symbol.get("range") or symbol.get("selectionRange")

        line = _format_range(range_data)
        location_display = f"{path} ({line})" if path and line else path
        lines.append(
            "| {name} | {kind} | {location} | {detail} |".format(
                name=symbol.get("name", ""),
                kind=_symbol_kind_name(symbol.get("kind")),
                location=location_display,
                detail=(symbol.get("detail", "") or "").replace("\n", " "),
            )
        )
    return "\n".join(lines)


def _is_content_modified_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "content modified" in message or "-32801" in message


async def _retry_on_content_modified(operation: Callable[[], Awaitable[_ReturnT]]) -> _ReturnT:
    for attempt in range(_CONTENT_MODIFIED_RETRY_ATTEMPTS + 1):
        try:
            return await operation()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if attempt == _CONTENT_MODIFIED_RETRY_ATTEMPTS or not _is_content_modified_error(exc):
                raise
            await asyncio.sleep(_CONTENT_MODIFIED_BASE_DELAY_SECONDS * (2**attempt))
    raise RuntimeError("Retry loop exhausted unexpectedly.")


class RustAnalyzerClient:
    """Tiny stdio JSON-RPC client for rust-analyzer."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.process: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._stderr_task: asyncio.Task[None] | None = None
        self._write_lock = asyncio.Lock()
        self._next_id = 1
        self._pending: dict[int, asyncio.Future[Any]] = {}
        self._diagnostics: dict[str, list[dict[str, Any]]] = {}
        self._versions: dict[str, int] = {}
        self._texts: dict[str, str] = {}

    async def start(self) -> None:
        if self.process is not None:
            return

        executable = _resolve_rust_analyzer_cmd()
        self.process = await asyncio.create_subprocess_exec(
            executable,
            cwd=str(self.repo_root),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._reader_task = asyncio.create_task(self._reader_loop())
        self._stderr_task = asyncio.create_task(self._stderr_drain_loop())

        root_uri = self.repo_root.as_uri()
        await self.request(
            "initialize",
            {
                "processId": os.getpid(),
                "rootPath": str(self.repo_root),
                "rootUri": root_uri,
                "workspaceFolders": [{"uri": root_uri, "name": self.repo_root.name}],
                "capabilities": {
                    "workspace": {"workspaceFolders": True},
                    "textDocument": {"hover": {"contentFormat": ["markdown", "plaintext"]}},
                },
            },
        )
        await self.notify("initialized", {})

    async def request(self, method: str, params: Any) -> Any:
        request_id = self._next_id
        self._next_id += 1

        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        self._pending[request_id] = future

        await self._send(
            {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params,
            }
        )
        return await future

    async def notify(self, method: str, params: Any) -> None:
        await self._send(
            {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
            }
        )

    async def sync_document(self, relative_path: str) -> None:
        absolute_path = (self.repo_root / relative_path).resolve()
        uri = absolute_path.as_uri()
        text = absolute_path.read_text(encoding="utf-8")

        previous = self._texts.get(uri)
        if previous is None:
            self._texts[uri] = text
            self._versions[uri] = 1
            await self.notify(
                "textDocument/didOpen",
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "rust",
                        "version": 1,
                        "text": text,
                    }
                },
            )
            return

        if previous == text:
            return

        version = self._versions[uri] + 1
        self._texts[uri] = text
        self._versions[uri] = version
        await self.notify(
            "textDocument/didChange",
            {
                "textDocument": {"uri": uri, "version": version},
                "contentChanges": [{"text": text}],
            },
        )

    async def hover(self, relative_path: str, line: int, character: int) -> Any:
        await self.sync_document(relative_path)
        return await self.request(
            "textDocument/hover",
            {
                "textDocument": {"uri": _relative_path_to_uri(relative_path)},
                "position": {"line": line, "character": character},
            },
        )

    async def definition(self, relative_path: str, line: int, character: int) -> Any:
        await self.sync_document(relative_path)
        return await self.request(
            "textDocument/definition",
            {
                "textDocument": {"uri": _relative_path_to_uri(relative_path)},
                "position": {"line": line, "character": character},
            },
        )

    async def references(self, relative_path: str, line: int, character: int) -> Any:
        await self.sync_document(relative_path)
        return await self.request(
            "textDocument/references",
            {
                "textDocument": {"uri": _relative_path_to_uri(relative_path)},
                "position": {"line": line, "character": character},
                "context": {"includeDeclaration": False},
            },
        )

    async def document_symbols(self, relative_path: str) -> Any:
        await self.sync_document(relative_path)
        return await self.request(
            "textDocument/documentSymbol",
            {"textDocument": {"uri": _relative_path_to_uri(relative_path)}},
        )

    async def workspace_symbols(self, query: str) -> Any:
        return await self.request("workspace/symbol", {"query": query})

    async def diagnostics(self, relative_path: str | None = None) -> Any:
        if relative_path is None:
            return {
                _uri_to_relative(uri): diagnostics
                for uri, diagnostics in sorted(self._diagnostics.items())
            }

        await self.sync_document(relative_path)
        uri = _relative_path_to_uri(relative_path)

        for _ in range(10):
            if uri in self._diagnostics:
                break
            await asyncio.sleep(0.1)

        return self._diagnostics.get(uri, [])

    async def _send(self, message: dict[str, Any]) -> None:
        if self.process is None or self.process.stdin is None:
            raise RuntimeError("rust-analyzer process is not running.")

        payload = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii")

        async with self._write_lock:
            self.process.stdin.write(header + payload)
            await self.process.stdin.drain()

    async def _reader_loop(self) -> None:
        assert self.process is not None
        assert self.process.stdout is not None

        while True:
            message = await self._read_message()
            if message is None:
                return

            if "id" in message and ("result" in message or "error" in message):
                request_id = message["id"]
                future = self._pending.pop(request_id, None)
                if future is None or future.done():
                    continue
                if "error" in message:
                    error = message["error"]
                    future.set_exception(
                        RuntimeError(
                            json.dumps(error, indent=2) if isinstance(error, dict) else str(error)
                        )
                    )
                else:
                    future.set_result(message.get("result"))
                continue

            if message.get("method") == "textDocument/publishDiagnostics":
                params = message.get("params", {})
                uri = params.get("uri")
                if uri:
                    self._diagnostics[uri] = params.get("diagnostics", [])

    async def _stderr_drain_loop(self) -> None:
        assert self.process is not None
        assert self.process.stderr is not None
        while True:
            line = await self.process.stderr.readline()
            if not line:
                return

    async def _read_message(self) -> dict[str, Any] | None:
        assert self.process is not None
        assert self.process.stdout is not None

        content_length: int | None = None

        while True:
            line = await self.process.stdout.readline()
            if not line:
                return None
            if line in (b"\r\n", b"\n"):
                break

            header = line.decode("utf-8").strip()
            name, _, value = header.partition(":")
            if name.lower() == "content-length":
                content_length = int(value.strip())

        if content_length is None:
            raise RuntimeError("Missing Content-Length header from rust-analyzer response.")

        payload = await self.process.stdout.readexactly(content_length)
        return json.loads(payload.decode("utf-8"))


async def _ensure_server() -> RustAnalyzerClient:
    global _server
    if _server is not None and _server.process is not None:
        return _server

    async with _server_lock:
        if _server is not None and _server.process is not None:
            return _server

        server = RustAnalyzerClient(_REPO_ROOT)
        await server.start()
        _server = server
        return server


async def lsp_hover(file_path: str, line: int, character: int) -> str:
    """Return hover information for a symbol at the given location."""
    try:
        relative_path = _resolve_relative_path(file_path)
        server = await _ensure_server()
        hover = await _retry_on_content_modified(
            lambda: server.hover(relative_path, line, character)
        )
        if not hover:
            return "No hover information returned."
        return _format_hover_contents(hover.get("contents"))
    except Exception as exc:
        return f"Error: {exc}"


async def lsp_definition(file_path: str, line: int, character: int) -> str:
    """Return definition locations for a symbol at the given location."""
    try:
        relative_path = _resolve_relative_path(file_path)
        server = await _ensure_server()
        result = await _retry_on_content_modified(
            lambda: server.definition(relative_path, line, character)
        )
        locations = result if isinstance(result, list) else ([result] if result else [])
        return _format_locations([dict(location) for location in locations])
    except Exception as exc:
        return f"Error: {exc}"


async def lsp_references(file_path: str, line: int, character: int) -> str:
    """Return reference locations for a symbol at the given location."""
    try:
        relative_path = _resolve_relative_path(file_path)
        server = await _ensure_server()
        result = await _retry_on_content_modified(
            lambda: server.references(relative_path, line, character)
        )
        locations = result if isinstance(result, list) else ([result] if result else [])
        return _format_locations([dict(location) for location in locations])
    except Exception as exc:
        return f"Error: {exc}"


async def lsp_document_symbols(file_path: str) -> str:
    """Return document symbols for a file."""
    try:
        relative_path = _resolve_relative_path(file_path)
        server = await _ensure_server()
        result = await _retry_on_content_modified(lambda: server.document_symbols(relative_path))
        symbols = result if isinstance(result, list) else []
        return _format_symbols([dict(symbol) for symbol in symbols], default_path=relative_path)
    except Exception as exc:
        return f"Error: {exc}"


async def lsp_workspace_symbols(query: str) -> str:
    """Return workspace symbols matching a query string."""
    try:
        server = await _ensure_server()
        result = await _retry_on_content_modified(lambda: server.workspace_symbols(query))
        symbols = result if isinstance(result, list) else []
        if not symbols:
            return "No symbols returned."
        return _format_symbols([dict(symbol) for symbol in symbols])
    except Exception as exc:
        return f"Error: {exc}"


async def lsp_diagnostics(file_path: str | None = None) -> str:
    """Return cached diagnostics from rust-analyzer."""
    try:
        server = await _ensure_server()
        relative_path = _resolve_relative_path(file_path) if file_path is not None else None
        diagnostics = await server.diagnostics(relative_path)
        return json.dumps(diagnostics, indent=2)
    except Exception as exc:
        return f"Error: {exc}"
