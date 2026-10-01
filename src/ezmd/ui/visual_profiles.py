"""Geometry/interaction profiles and shared presentation values."""

from dataclasses import dataclass

from PySide6.QtGui import QFont, QFontDatabase, QFontInfo, QPalette
from PySide6.QtWidgets import QApplication, QComboBox, QTextEdit, QToolBar, QVBoxLayout

from ezmd.ui.quote_editor import QuoteTextEdit


@dataclass(frozen=True)
class VisualProfile:
    toolbar_gap: int
    toolbar_padding: int
    content_margin: int
    control_height: int
    control_padding: int
    control_radius: int
    editor_radius: int
    editor_padding: int
    border_width: int
    quiet_buttons_at_rest: bool


PROFILES = {
    "Lab": VisualProfile(2, 2, 8, 25, 6, 3, 3, 6, 1, False),
    "QTemp": VisualProfile(8, 6, 20, 30, 8, 8, 6, 12, 1, False),
    "Focus": VisualProfile(4, 4, 8, 28, 6, 4, 4, 10, 1, True),
}
DEFAULT_PROFILE = "Focus"
HEADING_SCALES = (1.0, 1.6, 1.35, 1.15)
HISTORY_GLYPH_SCALE = 1.5
FALLBACK_POINT_SIZE = 12.0


def _font_point_size(font: QFont | QFontInfo, dpi: int) -> float | None:
    size = font.pointSizeF()
    if size > 0:
        return size
    pixels = font.pixelSize()
    return pixels * 72 / dpi if pixels > 0 and dpi > 0 else None


def resolve_base_point_size(fonts: tuple[QFont | QFontInfo, ...], dpi: int) -> float:
    system_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont)
    for font in (*fonts, QApplication.font(), system_font):
        size = _font_point_size(font, dpi)
        if size is not None:
            return size
    return FALLBACK_POINT_SIZE


def _base_point_size(editor: QTextEdit) -> float:
    return resolve_base_point_size((editor.fontInfo(), editor.font()), editor.logicalDpiY())


def heading_point_size(editor: QTextEdit, level: int) -> float:
    return _base_point_size(editor) * HEADING_SCALES[level]


@dataclass(frozen=True)
class Colors:
    surface: str
    editor: str
    text: str
    border: str
    hover: str
    focus: str
    disabled: str


def system_colors(palette: QPalette) -> Colors:
    # Keep native system colors and typography so all three profiles compare geometry alone.
    role = QPalette.ColorRole
    return Colors(
        surface=palette.color(role.Window).name(),
        editor=palette.color(role.Base).name(),
        text=palette.color(role.Text).name(),
        border=palette.color(role.Mid).name(),
        hover=palette.color(role.AlternateBase).name(),
        focus=palette.color(role.Highlight).name(),
        disabled=palette.color(QPalette.ColorGroup.Disabled, role.Text).name(),
    )


def apply_profile(
    toolbar: QToolBar,
    editor: QuoteTextEdit,
    content_layout: QVBoxLayout,
    selector: QComboBox,
    name: str,
    colors: Colors,
) -> None:
    profile = PROFILES[name]
    margin = profile.content_margin
    content_layout.setContentsMargins(margin, margin, margin, margin)
    resting_border = "transparent" if profile.quiet_buttons_at_rest else colors.border
    history_size = _base_point_size(editor) * HISTORY_GLYPH_SCALE
    toolbar.setStyleSheet(
        f"QToolBar {{ spacing: {profile.toolbar_gap}px; padding: {profile.toolbar_padding}px; "
        f"background: {colors.surface}; border-bottom: {profile.border_width}px solid "
        f"{colors.border}; }}"
        f"QToolBar QToolButton {{ min-height: {profile.control_height}px; "
        f"padding: 0 {profile.control_padding}px; border-radius: {profile.control_radius}px; "
        f"border: {profile.border_width}px solid {resting_border}; color: {colors.text}; }}"
        f"QToolBar QToolButton:hover {{ background: {colors.hover}; "
        f"border-color: {colors.border}; }}"
        f"QToolBar QToolButton:focus {{ border-color: {colors.focus}; }}"
        f"QToolBar QToolButton:pressed {{ background: {colors.hover}; "
        f"border-color: {colors.focus}; }}"
        f"QToolBar QToolButton:checked {{ background: {colors.hover}; "
        f"border-color: {colors.focus}; }}"
        f"QToolBar QToolButton:disabled {{ color: {colors.disabled}; }}"
        f"QToolBar QToolButton#historyButton {{ font-size: {history_size}pt; }}"
    )
    selector.setStyleSheet(
        f"QComboBox {{ min-height: {profile.control_height}px; "
        f"padding: 0 {profile.control_padding}px; border: {profile.border_width}px solid "
        f"{colors.border}; border-radius: {profile.control_radius}px; }}"
        f"QComboBox:focus {{ border-color: {colors.focus}; }}"
    )
    # Document margins add undo commands in Qt; widget padding leaves editing history intact.
    editor.setStyleSheet(
        f"QTextEdit {{ background: {colors.editor}; color: {colors.text}; "
        f"border: {profile.border_width}px solid {colors.border}; "
        f"border-radius: {profile.editor_radius}px; padding: {profile.editor_padding}px; }}"
    )
    editor.set_quote_rail(colors.border, profile.border_width, profile.control_padding)
