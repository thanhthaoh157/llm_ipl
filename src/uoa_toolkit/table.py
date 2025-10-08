"""Lightweight in-repo table utilities to avoid external dependencies during tests."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


def _to_key(row: Dict[str, object], keys: Sequence[str]) -> Tuple[object, ...]:
    return tuple(row.get(key) for key in keys)


def _column_letter(index: int) -> str:
    result = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result or "A"


@dataclass
class Table:
    columns: List[str]
    rows: List[Dict[str, object]]

    @classmethod
    def from_rows(cls, rows: Iterable[Dict[str, object]], columns: Optional[Sequence[str]] = None) -> "Table":
        rows_list = [dict(row) for row in rows]
        if columns is None:
            columns = list(rows_list[0].keys()) if rows_list else []
        return cls(list(columns), rows_list)

    @classmethod
    def read_csv(
        cls,
        path: Path,
        has_header: bool = True,
        delimiter: str = ",",
    ) -> "Table":
        with path.open("r", encoding="utf-8") as handle:
            if has_header:
                reader = csv.DictReader(handle, delimiter=delimiter)
                rows = [dict(row) for row in reader]
                columns = reader.fieldnames or []
            else:
                reader = csv.reader(handle, delimiter=delimiter)
                rows = [
                    {f"column_{idx}": value for idx, value in enumerate(record, start=1)}
                    for record in reader
                ]
                columns = list(rows[0].keys()) if rows else []
        return cls(columns, rows)

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return len(self.columns)

    @property
    def schema(self) -> Dict[str, str]:
        schema: Dict[str, str] = {}
        for column in self.columns:
            value = next((row[column] for row in self.rows if column in row and row[column] is not None), None)
            schema[column] = type(value).__name__ if value is not None else "str"
        return schema

    def select(self, columns: Sequence[str]) -> "Table":
        return Table.from_rows([{column: row.get(column) for column in columns} for row in self.rows], columns)

    def rename(self, mapping: Dict[str, str]) -> "Table":
        columns = [mapping.get(column, column) for column in self.columns]
        rows = []
        for row in self.rows:
            new_row = {mapping.get(column, column): value for column, value in row.items()}
            rows.append(new_row)
        return Table(columns, rows)

    def sort(self, columns: Sequence[str]) -> "Table":
        def sort_key(row: Dict[str, object]) -> Tuple:
            return tuple(row.get(column) for column in columns)

        rows = sorted(self.rows, key=sort_key)
        return Table(self.columns, rows)
    def join_left(self, other: "Table", on: Sequence[str]) -> "Table":
        other_only_columns = [column for column in other.columns if column not in on]
        other_index: Dict[Tuple[object, ...], List[Dict[str, object]]] = {}
        for row in other.rows:
            key = _to_key(row, on)
            other_index.setdefault(key, []).append(row)

        joined_rows: List[Dict[str, object]] = []
        for left_row in self.rows:
            key = _to_key(left_row, on)
            matches = other_index.get(key)
            if not matches:
                new_row = dict(left_row)
                for column in other_only_columns:
                    new_row[column] = None
                joined_rows.append(new_row)
                continue

            for match in matches:
                new_row = dict(left_row)
                for column in other_only_columns:
                    new_row[column] = match.get(column)
                joined_rows.append(new_row)

        columns = list(self.columns) + [column for column in other_only_columns if column not in self.columns]
        return Table(columns, joined_rows)

    def join_asof(self, other: "Table", timestamp: str, by: Optional[Sequence[str]] = None) -> "Table":
        if by is None:
            by = []
        by = list(by)

        other_sorted = other.sort(by + [timestamp])
        other_index: Dict[Tuple[object, ...], List[Dict[str, object]]] = {}
        for row in other_sorted.rows:
            key = _to_key(row, by)
            other_index.setdefault(key, []).append(row)

        other_only_columns = [column for column in other.columns if column not in by and column != timestamp]

        joined_rows: List[Dict[str, object]] = []
        for left_row in self.rows:
            key = _to_key(left_row, by)
            candidates = other_index.get(key, [])
            target_ts_raw = left_row.get(timestamp)
            target_ts = _parse_timestamp(target_ts_raw)
            best_match: Optional[Dict[str, object]] = None
            best_ts: Optional[datetime] = None
            for candidate in candidates:
                candidate_ts = _parse_timestamp(candidate.get(timestamp))
                if candidate_ts is None or target_ts is None:
                    continue
                if candidate_ts > target_ts:
                    break
                if best_ts is None or candidate_ts >= best_ts:
                    best_match = candidate
                    best_ts = candidate_ts

            new_row = dict(left_row)
            if best_match:
                for column in other_only_columns:
                    new_row[column] = best_match.get(column)
            else:
                for column in other_only_columns:
                    new_row[column] = None
            joined_rows.append(new_row)

        columns = list(self.columns) + [column for column in other_only_columns if column not in self.columns]
        return Table(columns, joined_rows)

    def write_csv(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.columns)
            writer.writeheader()
            for row in self.rows:
                writer.writerow({column: row.get(column) for column in self.columns})

    def write_parquet(self, path: Path) -> None:
        # Minimal placeholder implementation writes CSV-formatted data with parquet extension.
        self.write_csv(path)

    def iter_rows(self) -> Iterator[List[object]]:
        for row in self.rows:
            yield [row.get(column) for column in self.columns]


def _parse_timestamp(value: object) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None

def write_xlsx(path: Path, sheets: Dict[str, Table]) -> None:
    """Write a minimal XLSX workbook containing the provided sheets."""

    import zipfile

    path.parent.mkdir(parents=True, exist_ok=True)

    sheet_names = list(sheets.keys())
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Content types
        content_types = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">",
            "  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>",
            "  <Default Extension=\"xml\" ContentType=\"application/xml\"/>",
            "  <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>",
            "  <Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>",
        ]
        for idx, _ in enumerate(sheet_names, start=1):
            content_types.append(
                "  <Override PartName=\"/xl/worksheets/sheet{idx}.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>".format(
                    idx=idx
                )
            )
        content_types.append("</Types>")
        zf.writestr("[Content_Types].xml", "\n".join(content_types))

        # Root relationships
        zf.writestr(
            "_rels/.rels",
            """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>""",
        )

        # Workbook relationships
        workbook_rels = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">",
        ]
        for idx, _ in enumerate(sheet_names, start=1):
            workbook_rels.append(
                "  <Relationship Id=\"rId{idx}\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet{idx}.xml\"/>".format(
                    idx=idx
                )
            )
        workbook_rels.append("</Relationships>")
        zf.writestr("xl/_rels/workbook.xml.rels", "\n".join(workbook_rels))

        # Styles (minimal)
        zf.writestr(
            "xl/styles.xml",
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?><styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"/>",
        )

        # Workbook
        workbook_xml = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">",
            "  <sheets>",
        ]
        for idx, name in enumerate(sheet_names, start=1):
            workbook_xml.append(
                "    <sheet name=\"{name}\" sheetId=\"{idx}\" r:id=\"rId{idx}\"/>".format(name=name.replace("\"", "'"), idx=idx)
            )
        workbook_xml.extend(["  </sheets>", "</workbook>"])
        zf.writestr("xl/workbook.xml", "\n".join(workbook_xml))

        # Sheets
        for idx, name in enumerate(sheet_names, start=1):
            table = sheets[name]
            sheet_lines = [
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">",
                "  <sheetData>",
            ]
            header = Table.from_rows([dict(zip(table.columns, table.columns))], table.columns)
            for row_idx, row in enumerate(header.iter_rows(), start=1):
                sheet_lines.append(f"    <row r=\"{row_idx}\">")
                for col_idx, value in enumerate(row, start=1):
                    sheet_lines.append(_cell_xml(row_idx, col_idx, value))
                sheet_lines.append("    </row>")
            for offset, row in enumerate(table.iter_rows(), start=2):
                sheet_lines.append(f"    <row r=\"{offset}\">")
                for col_idx, value in enumerate(row, start=1):
                    sheet_lines.append(_cell_xml(offset, col_idx, value))
                sheet_lines.append("    </row>")
            sheet_lines.extend(["  </sheetData>", "</worksheet>"])
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", "\n".join(sheet_lines))


def _cell_xml(row_idx: int, col_idx: int, value: object) -> str:
    column_letter = _column_letter(col_idx)
    cell_ref = f"{column_letter}{row_idx}"
    cell_value = "" if value is None else _escape_xml(str(value))
    return f"      <c r=\"{cell_ref}\" t=\"inlineStr\"><is><t>{cell_value}</t></is></c>"


def _escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\"", "&quot;")
        .replace("'", "&apos;")
    )
