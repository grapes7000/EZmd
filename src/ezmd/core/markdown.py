"""Conversion between the controlled EZmd Markdown dialect and QTextDocument."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Flag, auto

from PySide6.QtGui import (
    QFont,
    QTextBlock,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
    QTextListFormat,
)

QUOTE_LEVEL = QTextFormat.Property.BlockQuoteLevel
EMPTY_PARAGRAPH = QTextFormat.Property.UserProperty
_HEADING = re.compile(r"^(#{1,6})(?: (.*))?$")
_BULLET = re.compile(r"^([-+*])(?: (.*))?$")
_NUMBERED = re.compile(r"^(\d+)\.(?: (.*))?$")
_TABLE_DIVIDER = re.compile(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$")
_HORIZONTAL_RULE = re.compile(r"^\s{0,3}((\*\s*){3,}|(-\s*){3,}|(_\s*){3,})$")
_INLINE_MARKERS = (
    ("~~", "strike"),
    ("**", "bold"),
    ("__", "bold"),
    ("*", "italic"),
    ("_", "italic"),
)


class MarkdownError(ValueError):
    """The document cannot be represented safely by the controlled dialect."""


class InlineStyle(Flag):
    NONE = 0
    BOLD = auto()
    ITALIC = auto()
    STRIKE = auto()


@dataclass(frozen=True)
class _Run:
    text: str
    styles: InlineStyle = InlineStyle.NONE


@dataclass(frozen=True)
class _Block:
    runs: tuple[_Run, ...]
    heading: int = 0
    structure: str = "ordinary"
    list_group: int | None = None


def parse_markdown(
    source: str, default_font: QFont, heading_sizes: tuple[float, float, float, float]
) -> QTextDocument:
    """Parse supported Markdown into a fresh, clean native document."""
    blocks = _parse_blocks(source.replace("\r\n", "\n").replace("\r", "\n"))
    document = QTextDocument()
    document.setDefaultFont(default_font)
    document.setUndoRedoEnabled(False)
    _build_document(document, blocks, heading_sizes)
    document.setUndoRedoEnabled(True)
    document.clearUndoRedoStacks()
    document.setModified(False)
    return document


def plain_text_document(source: str, default_font: QFont) -> QTextDocument:
    """Build a fresh document for import-only plain text."""
    document = QTextDocument()
    document.setDefaultFont(default_font)
    document.setUndoRedoEnabled(False)
    document.setPlainText(source)
    document.setUndoRedoEnabled(True)
    document.clearUndoRedoStacks()
    document.setModified(True)
    return document


def serialize_markdown(document: QTextDocument) -> str:
    """Read a native document into deterministic Markdown without mutating it."""
    blocks = list(_document_blocks(document))
    if len(blocks) == 1 and _is_placeholder_empty_block(blocks[0]):
        return ""

    output: list[str] = []
    previous_list_id: int | None = None
    list_number = 0
    for block in blocks:
        text_list = block.textList()
        list_id = text_list.objectIndex() if text_list else None
        list_style = text_list.format().style() if text_list else None
        same_list = list_id is not None and list_id == previous_list_id
        if output:
            output.append("\n" if same_list else "\n\n")

        if list_id is not None:
            if list_style not in (
                QTextListFormat.Style.ListDisc,
                QTextListFormat.Style.ListDecimal,
            ):
                raise MarkdownError("The document contains an unsupported list style.")
            if text_list.format().indent() != 1 or block.blockFormat().indent() != 0:
                raise MarkdownError("Nested or indented lists are not supported.")
            list_number = list_number + 1 if same_list else 1
        else:
            list_number = 0

        output.append(_serialize_block(block, list_style, list_number))
        previous_list_id = list_id
    return "".join(output) + "\n"


def _parse_blocks(source: str) -> list[_Block]:
    if source == "":
        return []
    lines = source.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    _validate_unsupported(lines)

    blocks: list[_Block] = []
    paragraph: list[str] = []
    list_group = 0
    active_list: str | None = None
    separated = True

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            blocks.append(_Block(_parse_inline(" ".join(paragraph))))
            paragraph = []

    for line in lines:
        if line == "":
            flush_paragraph()
            active_list = None
            separated = True
            continue
        if line == "\\":
            flush_paragraph()
            blocks.append(_Block(()))
            active_list = None
            separated = False
            continue

        parsed = _parse_structural_line(line)
        if parsed is None:
            if active_list is not None:
                raise MarkdownError("List continuation lines are not supported.")
            if blocks and blocks[-1].structure == "quote" and not separated:
                raise MarkdownError("Quote continuation lines are not supported.")
            paragraph.append(line)
            separated = False
            continue

        if parsed[1] == "quote" and blocks and blocks[-1].structure == "quote" and not separated:
            raise MarkdownError("Soft-wrapped blockquotes are not supported.")

        flush_paragraph()
        heading, structure, content = parsed
        group: int | None = None
        if structure in ("bullet", "numbered"):
            if separated or active_list != structure:
                list_group += 1
            group = list_group
            active_list = structure
        else:
            active_list = None
        blocks.append(_Block(_parse_inline(content), heading, structure, group))
        separated = False
    flush_paragraph()
    return blocks


def _parse_structural_line(line: str) -> tuple[int, str, str] | None:
    quote = line == ">" or line.startswith("> ")
    if quote:
        content = "" if line == ">" else line[2:]
        if _BULLET.fullmatch(content) or _NUMBERED.fullmatch(content) or content.startswith(">"):
            raise MarkdownError("Nested quotes and quote/list combinations are not supported.")
        heading, content = _take_heading(content)
        return heading, "quote", content

    bullet = _BULLET.fullmatch(line)
    if bullet:
        content = bullet.group(2) or ""
        if _BULLET.fullmatch(content) or _NUMBERED.fullmatch(content) or content.startswith(">"):
            raise MarkdownError("Nested and quoted lists are not supported.")
        heading, content = _take_heading(content)
        return heading, "bullet", content

    numbered = _NUMBERED.fullmatch(line)
    if numbered:
        content = numbered.group(2) or ""
        if _BULLET.fullmatch(content) or _NUMBERED.fullmatch(content) or content.startswith(">"):
            raise MarkdownError("Nested and quoted lists are not supported.")
        heading, content = _take_heading(content)
        return heading, "numbered", content

    heading = _HEADING.fullmatch(line)
    if heading:
        level = len(heading.group(1))
        if level > 3:
            raise MarkdownError("Only heading levels H1 through H3 are supported.")
        return level, "ordinary", heading.group(2) or ""
    return None


def _take_heading(content: str) -> tuple[int, str]:
    heading = _HEADING.fullmatch(content)
    if not heading:
        return 0, content
    level = len(heading.group(1))
    if level > 3:
        raise MarkdownError("Only heading levels H1 through H3 are supported.")
    return level, heading.group(2) or ""


def _validate_unsupported(lines: list[str]) -> None:
    for index, line in enumerate(lines):
        if re.match(r"^\s{0,3}(?:```|~~~)", line):
            raise MarkdownError("Fenced code blocks are not supported.")
        if line.startswith(("    ", "\t")):
            raise MarkdownError("Indented code and nested structures are not supported.")
        if re.match(r"^ {1,3}(?:#{1,6}(?: |$)|[-+*](?: |$)|\d+\.(?: |$)|>(?: |$))", line):
            raise MarkdownError("Indented Markdown structures are not supported.")
        if re.match(r"^\s{0,3}#{4,6}(?: |$)", line):
            raise MarkdownError("Only heading levels H1 through H3 are supported.")
        if _HORIZONTAL_RULE.fullmatch(line):
            raise MarkdownError("Horizontal rules are not supported.")
        if _TABLE_DIVIDER.fullmatch(line) or (
            "|" in line and index + 1 < len(lines) and _TABLE_DIVIDER.fullmatch(lines[index + 1])
        ):
            raise MarkdownError("Tables are not supported.")
        if index > 0 and lines[index - 1] and re.fullmatch(r"\s{0,3}(?:=+|-+)\s*", line):
            raise MarkdownError("Setext headings are not supported.")
        if (
            _contains_unescaped(line, "![")
            or re.search(r"(?<!\\)\[[^]]+\]\([^)]*\)", line)
            or re.search(r"(?<!\\)\[[^]]+\]\[[^]]*\]", line)
        ):
            raise MarkdownError("Links and images are not supported.")
        if re.search(r"(?<!\\)<(?:https?://|mailto:|/?[A-Za-z][^>]*|!--)", line):
            raise MarkdownError("Autolinks and HTML are not supported.")
        if _contains_unescaped(line, "`"):
            raise MarkdownError("Inline code is not supported.")
        if re.match(r"^(?:[-+*]|\d+\.) \[[ xX]\] ", line):
            raise MarkdownError("Task lists are not supported.")
        if re.match(r"^\[\^[^]]+\]:", line) or re.search(r"(?<!\\)\[\^[^]]+\]", line):
            raise MarkdownError("Footnotes are not supported.")
        if re.match(r"^\[[^]]+\]:\s*\S", line) or line.startswith(": "):
            raise MarkdownError("Definitions are not supported.")
        if line.endswith("  ") or (line != "\\" and _has_odd_trailing_backslashes(line)):
            raise MarkdownError("Hard line breaks are not supported.")


def _has_odd_trailing_backslashes(text: str) -> bool:
    return (len(text) - len(text.rstrip("\\"))) % 2 == 1


def _contains_unescaped(text: str, token: str) -> bool:
    start = 0
    while (position := text.find(token, start)) >= 0:
        slashes = 0
        index = position - 1
        while index >= 0 and text[index] == "\\":
            slashes += 1
            index -= 1
        if slashes % 2 == 0:
            return True
        start = position + len(token)
    return False


def _parse_inline(text: str) -> tuple[_Run, ...]:
    runs: list[_Run] = []
    plain: list[str] = []
    stack: list[tuple[str, InlineStyle]] = []
    index = 0

    def flush() -> None:
        if plain:
            value = "".join(plain)
            styles = InlineStyle.NONE
            for _marker, style in stack:
                styles |= style
            if runs and runs[-1].styles == styles:
                previous = runs.pop()
                value = previous.text + value
            runs.append(_Run(value, styles))
            plain.clear()

    while index < len(text):
        if (
            text[index] == "\\"
            and index + 1 < len(text)
            and text[index + 1] in " \\*_~`[]<>#!|+-.>"
        ):
            plain.append(text[index + 1])
            index += 2
            continue
        marker_and_style = _inline_marker_at(text, index, stack)
        if marker_and_style is None:
            plain.append(text[index])
            index += 1
            continue
        marker, style = marker_and_style
        flush()
        if stack and stack[-1][0] == marker:
            stack.pop()
        else:
            stack.append((marker, style))
        index += len(marker)
    flush()
    return tuple(_merge_runs(runs))


def _inline_marker_at(
    text: str, index: int, stack: list[tuple[str, InlineStyle]]
) -> tuple[str, InlineStyle] | None:
    if (
        stack
        and text.startswith(stack[-1][0], index)
        and _can_close_marker(text, stack[-1][0], index)
    ):
        return stack[-1]
    for marker, name in _INLINE_MARKERS:
        if not text.startswith(marker, index):
            continue
        following = index + len(marker)
        if following >= len(text) or text[following].isspace():
            continue
        if marker.startswith("_") and index > 0:
            if text[index - 1].isalnum() and text[following].isalnum():
                continue
        if _find_unescaped(text, marker, index + len(marker)) < 0:
            continue
        style = {
            "bold": InlineStyle.BOLD,
            "italic": InlineStyle.ITALIC,
            "strike": InlineStyle.STRIKE,
        }[name]
        return marker, style
    return None


def _find_unescaped(text: str, marker: str, start: int) -> int:
    position = start
    while (position := text.find(marker, position)) >= 0:
        slashes = 0
        index = position - 1
        while index >= 0 and text[index] == "\\":
            slashes += 1
            index -= 1
        if slashes % 2 == 0 and _can_close_marker(text, marker, position):
            return position
        position += len(marker)
    return -1


def _can_close_marker(text: str, marker: str, position: int) -> bool:
    if position == 0:
        return False
    if text[position - 1].isspace():
        slashes = 0
        index = position - 2
        while index >= 0 and text[index] == "\\":
            slashes += 1
            index -= 1
        if slashes % 2 == 0:
            return False
    after = position + len(marker)
    return not (
        marker.startswith("_")
        and after < len(text)
        and text[position - 1].isalnum()
        and text[after].isalnum()
    )


def _merge_runs(runs: list[_Run]) -> list[_Run]:
    merged: list[_Run] = []
    for run in runs:
        if not run.text:
            continue
        if merged and merged[-1].styles == run.styles:
            previous = merged.pop()
            merged.append(_Run(previous.text + run.text, run.styles))
        else:
            merged.append(run)
    return merged


def _build_document(
    document: QTextDocument,
    blocks: list[_Block],
    heading_sizes: tuple[float, float, float, float],
) -> None:
    if not blocks:
        return
    cursor = QTextCursor(document)
    for index, block in enumerate(blocks):
        if index:
            cursor.insertBlock()
        block_start = cursor.block()
        block_format = QTextBlockFormat(block_start.blockFormat())
        block_format.setHeadingLevel(block.heading)
        block_format.clearProperty(QUOTE_LEVEL)
        block_format.clearProperty(EMPTY_PARAGRAPH)
        block_format.setIndent(0)
        if block.structure == "quote":
            block_format.setProperty(QUOTE_LEVEL, 1)
            block_format.setIndent(1)
        elif block.heading == 0 and not block.runs:
            block_format.setProperty(EMPTY_PARAGRAPH, True)
        cursor.setBlockFormat(block_format)

        block_char_format = QTextCharFormat()
        block_char_format.setFontPointSize(heading_sizes[block.heading])
        cursor.setBlockCharFormat(block_char_format)
        for run in block.runs:
            char_format = QTextCharFormat(block_char_format)
            char_format.setFontWeight(
                QFont.Weight.Bold if InlineStyle.BOLD in run.styles else QFont.Weight.Normal
            )
            char_format.setFontItalic(InlineStyle.ITALIC in run.styles)
            char_format.setFontStrikeOut(InlineStyle.STRIKE in run.styles)
            cursor.insertText(run.text, char_format)

    index = 0
    while index < len(blocks):
        group = blocks[index].list_group
        if group is None:
            index += 1
            continue
        end = index
        while end + 1 < len(blocks) and blocks[end + 1].list_group == group:
            end += 1
        first = document.findBlockByNumber(index)
        last = document.findBlockByNumber(end)
        list_cursor = QTextCursor(first)
        list_cursor.setPosition(
            last.position() + last.length() - 1, QTextCursor.MoveMode.KeepAnchor
        )
        list_format = QTextListFormat()
        list_format.setIndent(1)
        list_format.setStyle(
            QTextListFormat.Style.ListDisc
            if blocks[index].structure == "bullet"
            else QTextListFormat.Style.ListDecimal
        )
        list_cursor.createList(list_format)
        index = end + 1


def _document_blocks(document: QTextDocument) -> list[QTextBlock]:
    blocks: list[QTextBlock] = []
    block = document.begin()
    while block.isValid():
        blocks.append(block)
        block = block.next()
    return blocks


def _is_placeholder_empty_block(block: QTextBlock) -> bool:
    return (
        block.text() == ""
        and block.blockFormat().headingLevel() == 0
        and not block.textList()
        and not block.blockFormat().hasProperty(QUOTE_LEVEL)
        and not block.blockFormat().boolProperty(EMPTY_PARAGRAPH)
    )


def _serialize_block(
    block: QTextBlock, list_style: QTextListFormat.Style | None, list_number: int
) -> str:
    block_format = block.blockFormat()
    heading = block_format.headingLevel()
    if heading not in (0, 1, 2, 3):
        raise MarkdownError("Only heading levels H1 through H3 are supported.")
    quote_level = (
        block_format.intProperty(QUOTE_LEVEL) if block_format.hasProperty(QUOTE_LEVEL) else 0
    )
    if quote_level not in (0, 1):
        raise MarkdownError("Nested blockquotes are not supported.")
    if quote_level and list_style is not None:
        raise MarkdownError("Quote/list combinations are not supported.")

    content = _escape_block_start(_serialize_inline(block))
    if not content and heading == 0 and list_style is None and not quote_level:
        return "\\"
    heading_marker = "#" * heading
    if heading:
        content = heading_marker if not content else f"{heading_marker} {content}"
    if list_style == QTextListFormat.Style.ListDisc:
        return "-" if not content else f"- {content}"
    if list_style == QTextListFormat.Style.ListDecimal:
        marker = f"{list_number}."
        return marker if not content else f"{marker} {content}"
    if quote_level:
        return ">" if not content else f"> {content}"
    return content


def _serialize_inline(block: QTextBlock) -> str:
    output: list[str] = []
    active: tuple[InlineStyle, ...] = ()
    iterator = block.begin()
    while not iterator.atEnd():
        fragment = iterator.fragment()
        text = fragment.text()
        if "\ufffc" in text:
            raise MarkdownError("Embedded objects are not supported.")
        char_format = fragment.charFormat()
        fragment_styles = tuple(
            style
            for style, enabled in (
                (InlineStyle.BOLD, char_format.fontWeight() >= QFont.Weight.Bold),
                (InlineStyle.ITALIC, char_format.fontItalic()),
                (InlineStyle.STRIKE, char_format.fontStrikeOut()),
            )
            if enabled
        )
        boundary_parts = re.fullmatch(r"(\s*)(.*?)(\s*)", text, re.DOTALL)
        assert boundary_parts is not None
        for part, styles in (
            (boundary_parts.group(1), fragment_styles),
            (boundary_parts.group(2), fragment_styles),
            (boundary_parts.group(3), fragment_styles),
        ):
            if not part:
                continue
            common = 0
            while common < min(len(active), len(styles)) and active[common] == styles[common]:
                common += 1
            output.extend(_style_marker(style) for style in reversed(active[common:]))
            output.extend(_style_marker(style) for style in styles[common:])
            output.append(
                _escape_formatted_whitespace(part)
                if part.isspace() and styles
                else _escape_inline(part)
            )
            active = styles
        iterator += 1
    output.extend(_style_marker(style) for style in reversed(active))
    return _escape_trailing_spaces("".join(output))


def _style_marker(style: InlineStyle) -> str:
    return {
        InlineStyle.BOLD: "**",
        InlineStyle.ITALIC: "*",
        InlineStyle.STRIKE: "~~",
    }[style]


def _escape_inline(text: str) -> str:
    escaped: list[str] = []
    for character in text:
        if character in "\\*_~`[]<>#!|":
            escaped.append("\\")
        escaped.append(character)
    return "".join(escaped)


def _escape_formatted_whitespace(text: str) -> str:
    return "".join(f"\\{character}" for character in text)


def _escape_trailing_spaces(text: str) -> str:
    trailing = len(text) - len(text.rstrip(" "))
    if not trailing:
        return text
    return text[:-trailing] + "\\ " * trailing


def _escape_block_start(text: str) -> str:
    marker = re.match(r"^( {0,3})([-+])(?: |$)", text)
    if marker:
        position = len(marker.group(1))
        return f"{text[:position]}\\{text[position:]}"
    if _HORIZONTAL_RULE.fullmatch(text):
        return f"\\{text}"
    number = re.match(r"^( {0,3})\d+\.(?: |$)", text)
    if number:
        dot = text.index(".", len(number.group(1)))
        return f"{text[:dot]}\\{text[dot:]}"
    return text
