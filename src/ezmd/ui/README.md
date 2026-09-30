# UI

Reserved for PySide6 **Qt Widgets** and visual interaction code.

QML/Qt Quick is not part of the initial architecture. UI code should call narrow document
operations rather than silently owning storage rules. User-facing spacing, radii, borders,
control sizes, typography sizes, and similar visual values belong in the semantic visual-profile
system rather than being scattered through widget construction.
