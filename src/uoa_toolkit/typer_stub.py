"""Minimal Typer-compatible stub used when the dependency is unavailable."""
from __future__ import annotations

import sys
from inspect import signature
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, get_args, get_origin


class _TyperModule:
    class Typer:
        def __init__(self, add_completion: bool = False, help: str | None = None) -> None:
            self._commands: Dict[str, Callable[..., Any]] = {}
            self.help = help or ""

        def command(self, name: str | None = None, **_: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                command_name = name or func.__name__
                self._commands[command_name] = func
                return func

            return decorator

        def __call__(self) -> None:
            argv = sys.argv[1:]
            if not argv:
                if self.help:
                    print(self.help)
                raise SystemExit(1)

            command_name = argv[0]
            if command_name not in self._commands:
                raise SystemExit(f"Unknown command: {command_name}")

            func = self._commands[command_name]
            func_signature = signature(func)
            from typing import get_type_hints
            type_hints = get_type_hints(func)
            kwargs = _parse_arguments(argv[1:], func_signature.parameters, type_hints)
            func(**kwargs)

    @staticmethod
    def Argument(default: Any, **_: Any) -> Any:
        return default

    @staticmethod
    def Option(*args: Any, **kwargs: Any) -> Any:
        if args:
            return args[0]
        if "default" in kwargs:
            return kwargs["default"]
        return None

    @staticmethod
    def echo(message: str) -> None:
        print(message)


_BOOLEAN_TRUE = {"true", "1", "yes", "on", "y", "t"}


def _convert(value: Optional[str], annotation: Any) -> Any:
    if value is None:
        return None
    if annotation is Path:
        return Path(value)
    origin = get_origin(annotation)
    if annotation is bool:
        return str(value).lower() in _BOOLEAN_TRUE
    if origin is not None:
        args = get_args(annotation)
        if bool in args and value is not None:
            return str(value).lower() in _BOOLEAN_TRUE
        for candidate in args:
            if candidate is Path:
                return Path(value)
    return value


def _parse_arguments(argv: List[str], parameters: Dict[str, Any], hints: Dict[str, Any]) -> Dict[str, Any]:
    positionals: List[str] = []
    options: Dict[str, Optional[str]] = {}
    index = 0
    while index < len(argv):
        token = argv[index]
        if token.startswith("--"):
            key = token[2:].replace("-", "_")
            value: Optional[str] = None
            if index + 1 < len(argv) and not argv[index + 1].startswith("--"):
                index += 1
                value = argv[index]
            else:
                value = "true"
            options[key] = value
        else:
            positionals.append(token)
        index += 1

    resolved: Dict[str, Any] = {}
    for name, param in parameters.items():
        if name in options:
            resolved[name] = _convert(options[name], hints.get(name, param.annotation))
        elif positionals:
            resolved[name] = _convert(positionals.pop(0), hints.get(name, param.annotation))
        elif param.default is not param.empty:
            resolved[name] = param.default
        else:
            raise SystemExit(f"Missing argument: {name}")
    return resolved


typer = _TyperModule()
