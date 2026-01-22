"""Custom UI widgets for Anuvad desktop application."""
from __future__ import annotations

import math
from typing import Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QBrush, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QApplication,
)


class AudioVisualizerWidget(QWidget):
    """
    Reactive audio visualizer bar displaying simulated multi-band equalizer bars
    reacting dynamically to incoming RMS audio energy with smooth decay.
    """

    def __init__(self, bar_count: int = 24, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.bar_count = bar_count
        self.setMinimumHeight(24)
        self.setMaximumHeight(32)

        self._target_level = 0.0
        self._current_levels = [0.0] * self.bar_count

        # Decay timer running at 30 FPS
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_decay)
        self._timer.start(33)

    def set_rms_level(self, level: float) -> None:
        """Update current audio RMS energy level in [0.0, 1.0]."""
        self._target_level = min(1.0, max(0.0, level * 2.5))  # Boost for visual pop

    def _update_decay(self) -> None:
        """Smoothly decay and bounce visualizer bars."""
        needs_repaint = False
        decay = 0.12

        for i in range(self.bar_count):
            # Shape the curve (center bars bounce slightly higher)
            freq_bias = math.sin((i / (self.bar_count - 1)) * math.pi) * 0.4 + 0.6
            target = self._target_level * freq_bias

            if target > self._current_levels[i]:
                self._current_levels[i] = target
                needs_repaint = True
            elif self._current_levels[i] > 0.01:
                self._current_levels[i] = max(0.0, self._current_levels[i] - decay)
                needs_repaint = True

        # Slowly decay global target
        self._target_level = max(0.0, self._target_level - 0.15)

        if needs_repaint:
            self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        width = self.width()
        height = self.height()
        bar_width = max(2.0, (width - (self.bar_count - 1) * 3) / self.bar_count)
        spacing = 3.0

        for i in range(self.bar_count):
            x = i * (bar_width + spacing)
            level = self._current_levels[i]
            bar_height = max(3.0, level * (height - 4))
            y = height - bar_height

            # Gradient from Cyan to Purple to Pink based on height
            gradient = QLinearGradient(x, height, x, y)
            gradient.setColorAt(0.0, QColor("#06B6D4"))
            gradient.setColorAt(0.6, QColor("#8B5CF6"))
            gradient.setColorAt(1.0, QColor("#EC4899"))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 2.0, 2.0)


class StatusBadge(QFrame):
    """Glowing status indicator pill (Ready / Listening / Processing / Stopped / Error)."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet("""
            StatusBadge {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 4px 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(6)

        self._dot = QLabel("●", self)
        self._dot.setStyleSheet("color: #94A3B8; font-size: 10px;")

        self._label = QLabel("Ready", self)
        self._label.setStyleSheet("color: #F8FAFC; font-weight: 700; font-size: 11px;")

        layout.addWidget(self._dot)
        layout.addWidget(self._label)

    def set_status(self, status: str, text: Optional[str] = None) -> None:
        status_lower = status.lower()
        display_text = text or status.capitalize()

        if "listen" in status_lower or "record" in status_lower:
            dot_color = "#EF4444"
            border_color = "rgba(239, 68, 68, 0.4)"
        elif "process" in status_lower:
            dot_color = "#F59E0B"
            border_color = "rgba(245, 158, 11, 0.4)"
        elif "connect" in status_lower or "ready" in status_lower:
            dot_color = "#10B981"
            border_color = "rgba(16, 185, 129, 0.4)"
        elif "error" in status_lower or "disconnect" in status_lower:
            dot_color = "#F43F5E"
            border_color = "rgba(244, 63, 94, 0.4)"
        else:
            dot_color = "#94A3B8"
            border_color = "#334155"

        self._dot.setStyleSheet(f"color: {dot_color}; font-size: 10px;")
        self._label.setText(display_text)
        self.setStyleSheet(f"""
            StatusBadge {{
                background-color: #0F172A;
                border: 1px solid {border_color};
                border-radius: 12px;
                padding: 4px 10px;
            }}
        """)


class CaptionDisplayCard(QFrame):
    """Card container for live captions or translations with word counter and copy button."""

    def __init__(self, title: str, tag_text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet("""
            CaptionDisplayCard {
                background-color: #121826;
                border: 1px solid #1E293B;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Header bar
        header = QHBoxLayout()
        header.setSpacing(8)

        self._title_label = QLabel(title, self)
        self._title_label.setStyleSheet("font-size: 13px; font-weight: 700; color: #F8FAFC;")

        self._tag_pill = QLabel(tag_text, self)
        self._tag_pill.setStyleSheet("""
            background-color: #1E293B;
            color: #06B6D4;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid #334155;
        """)

        self._word_count = QLabel("0 words", self)
        self._word_count.setStyleSheet("color: #64748B; font-size: 11px; font-weight: 500;")

        self._copy_btn = QPushButton("📋 Copy", self)
        self._copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #94A3B8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                color: #FFFFFF;
                border-color: #06B6D4;
            }
        """)
        self._copy_btn.clicked.connect(self._copy_to_clipboard)

        header.addWidget(self._title_label)
        header.addWidget(self._tag_pill)
        header.addStretch()
        header.addWidget(self._word_count)
        header.addWidget(self._copy_btn)

        layout.addLayout(header)

        # Text display area with rich-text HTML support for instant interim word streaming
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlaceholderText("Live speech will stream here...")
        layout.addWidget(self.text_edit, stretch=1)

        self._final_text: str = ""
        self._interim_text: str = ""

    def set_tag(self, text: str) -> None:
        self._tag_pill.setText(text)

    def append_final_text(self, text: str) -> None:
        """Append finalized text segment and auto-scroll."""
        text = text.strip()
        if not text:
            return

        if self._final_text:
            self._final_text += " " + text
        else:
            self._final_text = text
        self._interim_text = ""
        self._render_text()

    def set_interim_text(self, partial_text: str) -> None:
        """Display interim/partial words with instant real-time dynamic styling."""
        self._interim_text = partial_text.strip()
        self._render_text()

    def _render_text(self) -> None:
        """Render finalized words in solid white and live interim words in glowing cyan."""
        html_parts = []
        if self._final_text:
            escaped_final = self._final_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            html_parts.append(f'<span style="color: #F8FAFC; font-size: 11pt; font-weight: 500;">{escaped_final}</span>')
        if self._interim_text:
            escaped_interim = self._interim_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            html_parts.append(f'<span style="color: #38BDF8; font-size: 11pt; font-style: italic; font-weight: 500;"> {escaped_interim}</span>')

        html = "".join(html_parts)
        self.text_edit.setHtml(html)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())
        full_text = (self._final_text + " " + self._interim_text).strip()
        self._update_word_count(full_text)

    def clear(self) -> None:
        self._final_text = ""
        self._interim_text = ""
        self.text_edit.clear()
        self._word_count.setText("0 words")

    def _update_word_count(self, text: str) -> None:
        words = len(text.split()) if text else 0
        self._word_count.setText(f"{words} words")

    def _copy_to_clipboard(self) -> None:
        text = (self._final_text or self.text_edit.toPlainText()).strip()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self._copy_btn.setText("✓ Copied!")
            QTimer.singleShot(1500, lambda: self._copy_btn.setText("📋 Copy"))
