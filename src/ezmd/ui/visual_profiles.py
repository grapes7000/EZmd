"""Geometry profiles and the built-in light and dark presentation colors."""

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QFontDatabase, QFontInfo, QPalette
from PySide6.QtWidgets import QApplication, QComboBox, QTextEdit, QToolBar, QVBoxLayout

from ezmd.ui.quote_editor import QuoteTextEdit

SPACE_4 = 4
SPACE_6 = 6
SPACE_8 = 8
SPACE_12 = 12
SPACE_20 = 20
RADIUS_4 = 4
RADIUS_6 = 6
RADIUS_8 = 8
RADIUS_10 = 10
CONTROL_HEIGHT = 30
BORDER_WIDTH = 1


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
    # Lab and Focus retain their experimental dimensions; these are deliberate exceptions.
    "Lab": VisualProfile(2, 2, SPACE_8, 25, SPACE_6, 3, 3, SPACE_6, BORDER_WIDTH, False),
    "QTemp": VisualProfile(
        SPACE_8,
        SPACE_6,
        SPACE_20,
        CONTROL_HEIGHT,
        SPACE_8,
        RADIUS_8,
        RADIUS_6,
        SPACE_12,
        BORDER_WIDTH,
        False,
    ),
    "Focus": VisualProfile(
        SPACE_4,
        SPACE_4,
        SPACE_8,
        28,
        SPACE_6,
        RADIUS_4,
        RADIUS_4,
        RADIUS_10,
        BORDER_WIDTH,
        True,
    ),
    "Compact": VisualProfile(
        SPACE_6,
        SPACE_6,
        SPACE_20,
        CONTROL_HEIGHT,
        SPACE_8,
        RADIUS_4,
        RADIUS_6,
        SPACE_12,
        BORDER_WIDTH,
        True,
    ),
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
    background: str
    background_elevated: str
    surface: str
    surface_alternate: str
    surface_hover: str
    surface_active: str
    border: str
    border_strong: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent: str
    focus_ring: str
    selection: str
    on_accent: str


# Exact built-in light/dark values from qt-app-template/qml/theme/Theme.qml.
THEMES = {
    "Light": Colors(
        background="#F5F5F6",
        background_elevated="#F0F0F2",
        surface="#FFFFFF",
        surface_alternate="#F4F4F5",
        surface_hover="#EDEDEF",
        surface_active="#E5E5E8",
        border="#DEDFE2",
        border_strong="#C7C8CC",
        text_primary="#222326",
        text_secondary="#666970",
        text_muted="#91949B",
        accent="#6C5CE7",
        focus_ring="#6C5CE7",
        selection="#6C5CE7",
        on_accent="#FFFFFF",
    ),
    "Dark": Colors(
        background="#18191B",
        background_elevated="#1C1D1F",
        surface="#1F2023",
        surface_alternate="#232428",
        surface_hover="#292A2E",
        surface_active="#303136",
        border="#2B2C30",
        border_strong="#3A3C42",
        text_primary="#D9DADD",
        text_secondary="#9B9DA3",
        text_muted="#676A72",
        accent="#8B7CF8",
        focus_ring="#A294FB",
        selection="#8B7CF8",
        on_accent="#151519",
    ),
}
DEFAULT_THEME = "Dark"


def theme_palette(palette: QPalette, colors: Colors) -> QPalette:
    """Set native widget and selection roles alongside the explicit control styles."""
    palette = QPalette(palette)
    role = QPalette.ColorRole
    for color_role, value in (
        (role.Window, colors.background),
        (role.WindowText, colors.text_primary),
        (role.Base, colors.surface),
        (role.AlternateBase, colors.surface_alternate),
        (role.Text, colors.text_primary),
        (role.Button, colors.background_elevated),
        (role.ButtonText, colors.text_primary),
        (role.Highlight, colors.selection),
        (role.HighlightedText, colors.on_accent),
        (role.Mid, colors.border),
        (role.Dark, colors.border_strong),
        (role.Light, colors.surface_hover),
        (role.PlaceholderText, colors.text_secondary),
        (role.Link, colors.accent),
        (role.ToolTipBase, colors.surface),
        (role.ToolTipText, colors.text_primary),
    ):
        palette.setColor(color_role, QColor(value))
    for color_role in (role.WindowText, role.Text, role.ButtonText, role.PlaceholderText):
        palette.setColor(QPalette.ColorGroup.Disabled, color_role, QColor(colors.text_muted))
    return palette


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
        f"background: {colors.background_elevated}; border-bottom: {profile.border_width}px solid "
        f"{colors.border}; }}"
        f"QToolBar QToolButton {{ min-height: {profile.control_height}px; "
        f"padding: 0 {profile.control_padding}px; border-radius: {profile.control_radius}px; "
        f"border: {profile.border_width}px solid {resting_border}; color: {colors.text_primary}; }}"
        f"QToolBar QToolButton:hover {{ background: {colors.surface_hover}; "
        f"border-color: {colors.border}; }}"
        f"QToolBar QToolButton:focus {{ border-color: {colors.focus_ring}; }}"
        f"QToolBar QToolButton:pressed {{ background: {colors.surface_active}; "
        f"border-color: {colors.focus_ring}; }}"
        f"QToolBar QToolButton:checked {{ background: {colors.surface_active}; "
        f"border-color: {colors.focus_ring}; }}"
        f"QToolBar QToolButton:disabled {{ color: {colors.text_muted}; }}"
        f"QToolBar QToolButton#historyButton {{ font-size: {history_size}pt; }}"
    )
    selector.setStyleSheet(
        f"QComboBox {{ min-height: {profile.control_height}px; "
        f"padding: 0 {profile.control_padding}px; border: {profile.border_width}px solid "
        f"{colors.border}; border-radius: {profile.control_radius}px; "
        f"background: {colors.surface_alternate}; color: {colors.text_primary}; }}"
        f"QComboBox:focus {{ border-color: {colors.focus_ring}; }}"
        f"QComboBox QAbstractItemView {{ background: {colors.surface}; "
        f"color: {colors.text_primary}; selection-background-color: {colors.selection}; "
        f"selection-color: {colors.on_accent}; }}"
    )
    # Document margins add undo commands in Qt; widget padding leaves editing history intact.
    editor.setStyleSheet(
        f"QTextEdit {{ background: {colors.surface}; color: {colors.text_primary}; "
        f"border: {profile.border_width}px solid {colors.border}; "
        f"border-radius: {profile.editor_radius}px; padding: {profile.editor_padding}px; "
        f"selection-background-color: {colors.selection}; "
        f"selection-color: {colors.on_accent}; }}"
    )
    editor.set_quote_rail(colors.border_strong, profile.border_width, profile.control_padding)
