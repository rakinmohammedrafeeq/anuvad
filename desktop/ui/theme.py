"""Cyber-dark styling and QSS theme for Anuvad PySide6 desktop interface."""
from __future__ import annotations

DARK_CYBER_QSS = """
/* ==========================================================================
   ANUVAD — Modern Dark Cyber Theme (PySide6 / Qt6)
   ========================================================================== */

QMainWindow, QWidget {
    background-color: #0A0E17;
    color: #F8FAFC;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    font-size: 10pt;
}

/* Header & Brand */
#headerWidget {
    background-color: #121826;
    border-bottom: 1px solid #1E293B;
    padding: 16px 20px;
}

#brandTitle {
    font-size: 20px;
    font-weight: 800;
    color: #06B6D4;
    letter-spacing: 1.5px;
}

#brandSubtitle {
    font-size: 12px;
    color: #94A3B8;
    font-weight: 500;
}

#versionBadge {
    background-color: #1E293B;
    color: #A855F7;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid #334155;
}

/* Cards & Group Boxes */
QGroupBox {
    background-color: #121826;
    border: 1px solid #1E293B;
    border-radius: 12px;
    margin-top: 14px;
    padding: 16px;
    font-weight: 700;
    font-size: 12px;
    color: #94A3B8;
    letter-spacing: 0.5px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #06B6D4;
}

/* Input Source Radio Buttons */
QRadioButton {
    color: #E2E8F0;
    font-size: 13px;
    font-weight: 600;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #475569;
    background-color: #0F172A;
}

QRadioButton::indicator:hover {
    border-color: #06B6D4;
}

QRadioButton::indicator:checked {
    border-color: #06B6D4;
    background-color: #06B6D4;
}

/* Combo Boxes (Dropdowns) */
QComboBox {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 12px;
    color: #F8FAFC;
    font-weight: 500;
    min-height: 20px;
}

QComboBox:hover {
    border-color: #6366F1;
}

QComboBox:focus {
    border-color: #06B6D4;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 28px;
    border-left: 1px solid #1E293B;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94A3B8;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #0F172A;
    border: 1px solid #334155;
    border-radius: 8px;
    selection-background-color: #6366F1;
    selection-color: #FFFFFF;
    color: #F8FAFC;
    padding: 4px;
}

/* Push Buttons */
QPushButton {
    background-color: #1E293B;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    min-height: 22px;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #64748B;
}

QPushButton:pressed {
    background-color: #0F172A;
}

/* Hero Start / Stop Button */
#heroStartBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #A855F7);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 800;
    min-height: 26px;
}

#heroStartBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #9333EA);
}

#heroStartBtn:pressed {
    background: #4338CA;
}

#heroStartBtn[recording="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #F43F5E);
}

#heroStartBtn[recording="true"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC2626, stop:1 #E11D48);
}

/* Swap Language Button */
#swapLangBtn {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 8px;
    font-size: 16px;
    max-width: 36px;
    min-width: 36px;
    min-height: 34px;
    max-height: 34px;
    padding: 0;
}

#swapLangBtn:hover {
    border-color: #06B6D4;
    color: #06B6D4;
}

/* Text Displays (Captions & Translation) */
QPlainTextEdit, QTextEdit {
    background-color: #080C14;
    border: 1px solid #1E293B;
    border-radius: 10px;
    color: #F8FAFC;
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.6;
    padding: 12px;
}

QPlainTextEdit:focus, QTextEdit:focus {
    border-color: #06B6D4;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #0A0E17;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64748B;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* Status Bar */
QStatusBar {
    background-color: #080C14;
    border-top: 1px solid #1E293B;
    color: #94A3B8;
    font-size: 11px;
    font-weight: 500;
}

/* Labels */
QLabel {
    color: #F8FAFC;
}

.secondaryLabel {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
"""
