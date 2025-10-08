"""Minimal YAML parser supporting the subset used in recipes."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple


def safe_load(text: str) -> Any:
    lines = [line.rstrip("\n") for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    result, _ = _parse_block(lines, 0, 0)
    return result


def _parse_block(lines: List[str], index: int, indent: int) -> Tuple[Any, int]:
    items: List[Any] = []
    mapping: Dict[str, Any] = {}
    is_list = False

    while index < len(lines):
        line = lines[index]
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)
        if current_indent < indent:
            break
        if stripped.startswith("- "):
            if not is_list:
                is_list = True
                items = []
            value_part = stripped[2:].strip()
            if value_part and ":" in value_part:
                key, remainder = value_part.split(":", 1)
                item: Dict[str, Any] = {key.strip(): _parse_value(remainder.strip())}
                index += 1
                child, index = _parse_block(lines, index, current_indent + 2)
                if child:
                    if isinstance(child, dict):
                        item.update(child)
                items.append(item)
            elif value_part:
                items.append(_parse_value(value_part))
                index += 1
            else:
                child, index = _parse_block(lines, index + 1, current_indent + 2)
                items.append(child)
        else:
            if is_list:
                break
            if ":" in stripped:
                key, remainder = stripped.split(":", 1)
                key = key.strip()
                value_str = remainder.strip()
                if value_str:
                    mapping[key] = _parse_value(value_str)
                    index += 1
                else:
                    child, index = _parse_block(lines, index + 1, current_indent + 2)
                    mapping[key] = child
            else:
                index += 1
    return (items if is_list else mapping), index


def _parse_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_coerce(part.strip()) for part in inner.split(",")]
    return _coerce(value)


def _coerce(value: str) -> Any:
    if value.startswith("\"") and value.endswith("\""):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "null":
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
