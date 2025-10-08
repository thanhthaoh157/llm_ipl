from typing import Any, Dict, Iterable, List, Tuple


def safe_load(text: str) -> Any:
    lines = [line.rstrip("\n") for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    result, _ = _parse_block(lines, 0, 0)
    return result


def safe_dump(data: Any, stream: Any = None, *, sort_keys: bool = False) -> str:
    """Serialise a tiny subset of YAML used by the tests."""

    lines = _dump_block(data, 0, sort_keys=sort_keys)
    rendered = "\n".join(lines) + "\n"
    if stream is not None:
        stream.write(rendered)
    return rendered


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
                if child and isinstance(child, dict):
                    item.update(child)
                items.append(item)
            elif value_part:
                items.append(_parse_value(value_part))
                index += 1
            else:
                child, index = _parse_block(lines, index + 1, current_indent + 2)
                items.append(child)
            continue

        if stripped == "-":
            if not is_list:
                is_list = True
                items = []
            child, index = _parse_block(lines, index + 1, current_indent + 2)
            items.append(child)
            continue

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


def _dump_block(data: Any, indent: int, *, sort_keys: bool) -> List[str]:
    indent_str = " " * indent
    if isinstance(data, dict):
        keys: Iterable[str]
        keys = sorted(data) if sort_keys else data
        lines: List[str] = []
        for key in keys:
            value = data[key]
            if isinstance(value, (dict, list)):
                lines.append(f"{indent_str}{key}:")
                lines.extend(_dump_block(value, indent + 2, sort_keys=sort_keys))
            else:
                lines.append(f"{indent_str}{key}: {_format_scalar(value)}")
        return lines
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{indent_str}-")
                lines.extend(_dump_block(item, indent + 2, sort_keys=sort_keys))
            else:
                lines.append(f"{indent_str}- {_format_scalar(item)}")
        return lines
    return [f"{indent_str}{_format_scalar(data)}"]


def _parse_value(value: str) -> Any:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_coerce(part.strip()) for part in inner.split(",")]
    return _coerce(value)


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text:
        return "''"
    if any(char in text for char in [":", "#", "[", "]", "{", "}"]) or text.strip() != text or "\n" in text:
        return f"'{text}'"
    return text


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
