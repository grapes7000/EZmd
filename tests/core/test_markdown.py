"""The controlled Markdown dialect round-trips native document semantics."""

from __future__ import annotations

import pytest
from PySide6.QtGui import (
    QFont,
    QTextBlock,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
    QTextListFormat,
)

from ezmd.core.markdown import MarkdownError, parse_markdown, serialize_markdown

FONT = QFont("Sans Serif", 12)
SIZES = (12.0, 20.0, 17.0, 14.0)
QUOTE_LEVEL = QTextFormat.Property.BlockQuoteLevel


def parse(source: str) -> QTextDocument:
    return parse_markdown(source, FONT, SIZES)


def blocks(document: QTextDocument) -> list[QTextBlock]:
    result: list[QTextBlock] = []
    block = document.begin()
    while block.isValid():
        result.append(block)
        block = block.next()
    return result


def test_empty_document_is_an_empty_file() -> None:
    document = parse("")
    assert document.blockCount() == 1
    assert serialize_markdown(document) == ""


def test_intentional_empty_paragraphs_are_distinct_from_separators() -> None:
    canonical = "\\\n\nBefore\n\n\\\n\n\\\n\nAfter\n\n\\\n"
    document = parse(canonical)
    assert [block.text() for block in blocks(document)] == ["", "Before", "", "", "After", ""]
    assert serialize_markdown(document) == canonical
    separated = parse("Before\n\nAfter\n")
    assert [block.text() for block in blocks(separated)] == ["Before", "After"]


def test_one_intentional_empty_paragraph_is_not_an_empty_document() -> None:
    document = parse("\\\n")
    assert serialize_markdown(document) == "\\\n"


def test_literal_backslash_is_not_the_empty_paragraph_marker() -> None:
    document = parse("\\\\\n")
    assert document.toPlainText() == "\\"
    assert serialize_markdown(document) == "\\\\\n"


@pytest.mark.parametrize(
    ("source", "heading", "list_style", "quote"),
    [
        ("#\n", 1, None, 0),
        ("##\n", 2, None, 0),
        ("###\n", 3, None, 0),
        ("-\n", 0, QTextListFormat.Style.ListDisc, 0),
        ("1.\n", 0, QTextListFormat.Style.ListDecimal, 0),
        (">\n", 0, None, 1),
        ("- ##\n", 2, QTextListFormat.Style.ListDisc, 0),
        ("1. ###\n", 3, QTextListFormat.Style.ListDecimal, 0),
        ("> #\n", 1, None, 1),
    ],
)
def test_empty_semantic_blocks_have_stable_canonical_forms(
    source: str,
    heading: int,
    list_style: QTextListFormat.Style | None,
    quote: int,
) -> None:
    document = parse(source)
    block = document.begin()
    assert block.text() == ""
    assert block.blockFormat().headingLevel() == heading
    assert (block.textList().format().style() if block.textList() else None) == list_style
    assert block.blockFormat().intProperty(QUOTE_LEVEL) == quote
    assert serialize_markdown(document) == source


@pytest.mark.parametrize(("source", "level"), [("#\n", 1), ("##\n", 2), ("###\n", 3)])
def test_reopened_empty_heading_keeps_heading_sized_typing(source: str, level: int) -> None:
    document = parse(source)
    cursor = QTextCursor(document)
    cursor.insertText("Title")
    assert document.begin().blockFormat().headingLevel() == level
    assert document.begin().begin().fragment().charFormat().fontPointSize() == SIZES[level]


def test_numbered_lists_restart_per_distinct_contiguous_list() -> None:
    canonical = "1. First\n2. Second\n\nBody\n\n1. Third\n2. Fourth\n"
    document = parse("8. First\n4. Second\n\nBody\n\n9. Third\n20. Fourth\n")
    parsed = blocks(document)
    assert parsed[0].textList().objectIndex() == parsed[1].textList().objectIndex()
    assert parsed[3].textList().objectIndex() == parsed[4].textList().objectIndex()
    assert parsed[0].textList().objectIndex() != parsed[3].textList().objectIndex()
    assert serialize_markdown(document) == canonical
    assert serialize_markdown(parse(canonical)) == canonical


def test_supported_blocks_inline_combinations_and_alternate_spellings_normalize() -> None:
    source = (
        "# __Bold__ and _italic_ and ~~strike~~\n\n* ***all three***\n+ plain\n\n> ## **quoted**\n"
    )
    canonical = (
        "# **Bold** and *italic* and ~~strike~~\n\n- ***all three***\n- plain\n\n> ## **quoted**\n"
    )
    document = parse(source)
    assert [block.blockFormat().headingLevel() for block in blocks(document)] == [1, 0, 0, 2]
    assert serialize_markdown(document) == canonical
    assert serialize_markdown(parse(canonical)) == canonical


def test_quote_state_does_not_leak_into_following_headings_lists_or_text() -> None:
    source = (
        "### Blockquote\n\n"
        "> blockquote\n\n"
        "### Ordered List\n\n"
        "1. First item\n"
        "2. Second item\n"
        "3. Third item\n\n"
        "### Unordered List\n\n"
        "- First item\n"
        "- Second item\n"
        "- Third item\n\n"
        "### Strikethrough\n\n"
        "~~The world is flat.~~\n"
    )
    document = parse(source)
    parsed = blocks(document)

    assert [block.text() for block in parsed] == [
        "Blockquote",
        "blockquote",
        "Ordered List",
        "First item",
        "Second item",
        "Third item",
        "Unordered List",
        "First item",
        "Second item",
        "Third item",
        "Strikethrough",
        "The world is flat.",
    ]
    quote_levels = [block.blockFormat().intProperty(QUOTE_LEVEL) for block in parsed]
    assert quote_levels == [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    assert [parsed[index].blockFormat().headingLevel() for index in (0, 2, 6, 10)] == [3] * 4
    assert [parsed[index].textList().format().style() for index in (3, 4, 5)] == [
        QTextListFormat.Style.ListDecimal
    ] * 3
    assert [parsed[index].textList().format().style() for index in (7, 8, 9)] == [
        QTextListFormat.Style.ListDisc
    ] * 3
    assert parsed[11].begin().fragment().charFormat().fontStrikeOut()

    reopened = parse(serialize_markdown(document))
    assert [
        block.blockFormat().intProperty(QUOTE_LEVEL) for block in blocks(reopened)
    ] == quote_levels


def test_literal_markdown_characters_and_unmatched_delimiters_round_trip() -> None:
    document = QTextDocument()
    document.setPlainText("# literal\n- item-looking\n3. numbered\n> quote\n* unmatched")
    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    assert reopened.toPlainText() == document.toPlainText()
    assert all(block.blockFormat().headingLevel() == 0 for block in blocks(reopened))
    assert all(block.textList() is None for block in blocks(reopened))
    assert serialize_markdown(reopened) == canonical


@pytest.mark.parametrize("text", ["-", "+", "1.", "123."])
def test_bare_structural_markers_remain_literal_text(text: str) -> None:
    document = QTextDocument()
    document.setPlainText(text)
    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    assert reopened.toPlainText() == text
    assert reopened.begin().textList() is None
    assert serialize_markdown(reopened) == canonical


@pytest.mark.parametrize("text", [" - literal", "  + literal", "   1. literal"])
def test_indented_structural_markers_remain_literal_text(text: str) -> None:
    document = QTextDocument()
    document.setPlainText(text)
    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    assert reopened.toPlainText() == text
    assert serialize_markdown(reopened) == canonical


@pytest.mark.parametrize("text", ["trailing ", "trailing  "])
def test_trailing_spaces_do_not_become_hard_break_syntax(text: str) -> None:
    document = QTextDocument()
    document.setPlainText(text)
    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    assert reopened.toPlainText() == text
    assert serialize_markdown(reopened) == canonical


def test_backslashes_only_escape_supported_markdown_punctuation() -> None:
    document = parse("C:\\Users\\name and \\*literal stars\\*\n")
    assert document.toPlainText() == "C:\\Users\\name and *literal stars*"
    assert serialize_markdown(parse(serialize_markdown(document))) == serialize_markdown(document)


@pytest.mark.parametrize("source", ["2 * 3 * 4\n", "foo_bar_baz\n", "*open but not closed *\n"])
def test_ordinary_inline_punctuation_does_not_become_formatting(source: str) -> None:
    document = parse(source)
    assert document.toPlainText() == source.rstrip("\n")
    assert serialize_markdown(parse(serialize_markdown(document))) == serialize_markdown(document)


@pytest.mark.parametrize("structure", ["bullet", "numbered", "quote"])
def test_structured_blocks_can_contain_literal_list_looking_text(structure: str) -> None:
    document = QTextDocument()
    document.setPlainText("- literal marker")
    block = document.begin()
    if structure == "quote":
        block_format = block.blockFormat()
        block_format.setProperty(QUOTE_LEVEL, 1)
        QTextCursor(block).setBlockFormat(block_format)
    else:
        cursor = QTextCursor(block)
        list_format = QTextListFormat()
        list_format.setIndent(1)
        list_format.setStyle(
            QTextListFormat.Style.ListDisc
            if structure == "bullet"
            else QTextListFormat.Style.ListDecimal
        )
        cursor.createList(list_format)

    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    assert reopened.toPlainText() == "- literal marker"
    assert serialize_markdown(reopened) == canonical


def test_crossing_inline_format_boundaries_round_trip_semantically() -> None:
    document = QTextDocument()
    cursor = QTextCursor(document)
    cursor.insertText("a")
    cursor.insertText("b")
    cursor.insertText("c")
    bold = QTextCharFormat()
    bold.setFontWeight(QFont.Weight.Bold)
    cursor.setPosition(0)
    cursor.setPosition(2, QTextCursor.MoveMode.KeepAnchor)
    cursor.mergeCharFormat(bold)
    italic = QTextCharFormat()
    italic.setFontItalic(True)
    cursor.setPosition(1)
    cursor.setPosition(3, QTextCursor.MoveMode.KeepAnchor)
    cursor.mergeCharFormat(italic)

    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    formats: list[tuple[bool, bool]] = []
    for position in range(1, 4):
        cursor = QTextCursor(reopened)
        cursor.setPosition(position)
        char_format = cursor.charFormat()
        formats.append((char_format.fontWeight() >= QFont.Weight.Bold, char_format.fontItalic()))
    assert formats == [(True, False), (True, True), (False, True)]
    assert serialize_markdown(reopened) == canonical


def test_combined_to_single_inline_format_transitions_round_trip() -> None:
    document = QTextDocument()
    cursor = QTextCursor(document)
    for text, bold_enabled, italic_enabled in (
        ("a", True, True),
        ("b", True, False),
        ("c", False, True),
    ):
        char_format = QTextCharFormat()
        char_format.setFontWeight(QFont.Weight.Bold if bold_enabled else QFont.Weight.Normal)
        char_format.setFontItalic(italic_enabled)
        cursor.insertText(text, char_format)

    canonical = serialize_markdown(document)
    reopened = parse(canonical)
    formats: list[tuple[bool, bool]] = []
    for position in range(1, 4):
        cursor = QTextCursor(reopened)
        cursor.setPosition(position)
        char_format = cursor.charFormat()
        formats.append((char_format.fontWeight() >= QFont.Weight.Bold, char_format.fontItalic()))
    assert reopened.toPlainText() == "abc"
    assert formats == [(True, True), (True, False), (False, True)]
    assert serialize_markdown(reopened) == canonical


@pytest.mark.parametrize("style", ["bold", "italic", "strike"])
def test_inline_formatting_with_boundary_whitespace_keeps_text_and_words(style: str) -> None:
    document = QTextDocument()
    cursor = QTextCursor(document)
    char_format = QTextCharFormat()
    if style == "bold":
        char_format.setFontWeight(QFont.Weight.Bold)
    elif style == "italic":
        char_format.setFontItalic(True)
    else:
        char_format.setFontStrikeOut(True)
    cursor.insertText(" a ", char_format)

    reopened = parse(serialize_markdown(document))
    assert reopened.toPlainText() == " a "
    for position in range(1, 4):
        cursor = QTextCursor(reopened)
        cursor.setPosition(position)
        reopened_format = cursor.charFormat()
        assert (reopened_format.fontWeight() >= QFont.Weight.Bold) == (style == "bold")
        assert reopened_format.fontItalic() == (style == "italic")
        assert reopened_format.fontStrikeOut() == (style == "strike")


def test_formatted_text_after_leading_spaces_round_trips() -> None:
    document = QTextDocument()
    cursor = QTextCursor(document)
    cursor.insertText("  ")
    bold = QTextCharFormat()
    bold.setFontWeight(QFont.Weight.Bold)
    cursor.insertText("a", bold)

    reopened = parse(serialize_markdown(document))
    assert reopened.toPlainText() == "  a"
    cursor = QTextCursor(reopened)
    cursor.setPosition(3)
    assert cursor.charFormat().fontWeight() >= QFont.Weight.Bold


@pytest.mark.parametrize(
    "source",
    [
        "[link](target)\n",
        "[link][target]\n\n[target]: destination\n",
        "![image](target)\n",
        "```python\ncode\n```\n",
        "| A | B |\n|---|---|\n",
        "  - nested\n",
        "> - quoted list\n",
        "> > nested quote\n",
        "#### H4\n",
        "Heading\n===\n",
        "`code`\n",
        "- [ ] task\n",
        "---\n",
        "<div>html</div>\n",
        "<!-- html comment -->\n",
        "1. [ ] task\n",
        " #### H4\n",
        "   ~~~\ncode\n   ~~~\n",
        "hard break  \nnext line\n",
        "hard break\\\nnext line\n",
        "- item\nlazy continuation\n",
        "> quote\nlazy continuation\n",
        "> soft\n> wrapped\n",
    ],
)
def test_unsupported_markdown_is_refused(source: str) -> None:
    with pytest.raises(MarkdownError):
        parse(source)
