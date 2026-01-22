"""Main window for Anuvad PySide6 desktop application."""
from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ..audio.loopback_capture import SystemAudioCapture
from ..audio.mic_capture import MicrophoneCapture
from ..app.client import WebSocketClientThread
from .theme import DARK_CYBER_QSS
from .widgets import AudioVisualizerWidget, CaptionDisplayCard, StatusBadge

logger = logging.getLogger("anuvad.desktop.ui")

# Supported language codes and names (aligned with backend config)
LANGUAGE_OPTIONS = [
    ("auto", "Auto Detect"),
    ("en", "English"),
    ("es", "Spanish (Español)"),
    ("fr", "French (Français)"),
    ("de", "German (Deutsch)"),
    ("hi", "Hindi (हिन्दी)"),
    ("it", "Italian (Italiano)"),
    ("pt", "Portuguese (Português)"),
    ("ja", "Japanese (日本語)"),
    ("ko", "Korean (한국어)"),
    ("zh", "Chinese (中文)"),
    ("ar", "Arabic (العربية)"),
    ("ru", "Russian (Русский)"),
    ("nl", "Dutch (Nederlands)"),
    ("tr", "Turkish (Türkçe)"),
    ("pl", "Polish (Polski)"),
]


class MainWindow(QMainWindow):
    """
    Primary desktop user interface for Anuvad.
    Provides Microphone and System Audio (WASAPI loopback) capture modes,
    real-time dual-pane captions and translation.
    """

    def __init__(self, backend_url: str = "ws://127.0.0.1:8000/ws"):
        super().__init__()
        self.setWindowTitle("ANUVAD — Real-Time Multilingual Speech Captioning")
        self.resize(1000, 780)
        self.setMinimumSize(800, 600)

        self.backend_url = backend_url
        self.is_recording = False
        self.is_connected = False

        # Audio capture engines
        self.mic_capture: Optional[MicrophoneCapture] = None
        self.loopback_capture: Optional[SystemAudioCapture] = None

        # Backend WebSocket worker
        self.client_thread = WebSocketClientThread(server_url=self.backend_url)

        self._init_window_icon()
        self._init_ui()
        self._apply_theme()
        self._bind_client_signals()

        # Start backend WebSocket client thread
        self.client_thread.start()

        # Initial device scan
        self._refresh_device_list()

    def _init_window_icon(self) -> None:
        """Load window icon from assets if available."""
        possible_paths = [
            Path(__file__).resolve().parent.parent.parent / "web" / "favicon.ico",
            Path(__file__).resolve().parent.parent.parent / "web" / "assets" / "logo.png",
        ]
        for p in possible_paths:
            if p.exists():
                self.setWindowIcon(QIcon(str(p)))
                break

    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # 1. Header Bar
        header = QFrame(self)
        header.setObjectName("headerWidget")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        # Logo / Avatar icon
        logo_label = QLabel(self)
        icon_path = Path(__file__).resolve().parent.parent.parent / "web" / "assets" / "favicon-32x32.png"
        if icon_path.exists():
            pix = QPixmap(str(icon_path))
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("⚡")
            logo_label.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(logo_label)

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title_lbl = QLabel("ANUVAD", self)
        title_lbl.setObjectName("brandTitle")
        version_lbl = QLabel("LOCAL ASR v2.0", self)
        version_lbl.setObjectName("versionBadge")
        title_row.addWidget(title_lbl)
        title_row.addWidget(version_lbl)
        title_row.addStretch()

        subtitle_lbl = QLabel("Real-Time Multilingual Speech Captioning & Translation", self)
        subtitle_lbl.setObjectName("brandSubtitle")
        title_vbox.addLayout(title_row)
        title_vbox.addWidget(subtitle_lbl)
        header_layout.addLayout(title_vbox)

        header_layout.addStretch()

        # Status badge
        self.status_badge = StatusBadge(self)
        header_layout.addWidget(self.status_badge)

        main_layout.addWidget(header)

        # 2. Control Bento Card: Input Source & Languages
        controls_group = QGroupBox("AUDIO SOURCE & LANGUAGE CONTROLS", self)
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(12)

        # Row A: Input Source Selector
        source_row = QHBoxLayout()
        source_row.setSpacing(16)

        source_label = QLabel("INPUT SOURCE:", self)
        source_label.setStyleSheet("font-weight: 700; color: #94A3B8; font-size: 11px;")
        source_row.addWidget(source_label)

        self.source_btn_group = QButtonGroup(self)
        self.radio_mic = QRadioButton("Microphone", self)
        self.radio_mic.setChecked(True)
        self.radio_loopback = QRadioButton("System Audio (Loopback)", self)
        self.source_btn_group.addButton(self.radio_mic)
        self.source_btn_group.addButton(self.radio_loopback)

        source_row.addWidget(self.radio_mic)
        source_row.addWidget(self.radio_loopback)

        # Device selector combo box
        self.device_combo = QComboBox(self)
        self.device_combo.setMinimumWidth(260)
        source_row.addWidget(self.device_combo)

        refresh_dev_btn = QPushButton("🔄", self)
        refresh_dev_btn.setToolTip("Refresh audio device list")
        refresh_dev_btn.setMaximumWidth(36)
        refresh_dev_btn.clicked.connect(self._refresh_device_list)
        source_row.addWidget(refresh_dev_btn)

        source_row.addStretch()
        controls_layout.addLayout(source_row)

        # Row B: Languages & Action Buttons
        lang_action_row = QHBoxLayout()
        lang_action_row.setSpacing(12)

        # Source Language
        src_vbox = QVBoxLayout()
        src_vbox.setSpacing(4)
        src_lbl = QLabel("SPEAK IN", self)
        src_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #94A3B8;")
        self.src_lang_combo = QComboBox(self)
        for code, name in LANGUAGE_OPTIONS:
            self.src_lang_combo.addItem(name, code)
        self.src_lang_combo.setCurrentIndex(1)  # English default
        src_vbox.addWidget(src_lbl)
        src_vbox.addWidget(self.src_lang_combo)
        lang_action_row.addLayout(src_vbox)

        # Swap button
        swap_vbox = QVBoxLayout()
        swap_vbox.setSpacing(4)
        swap_vbox.addWidget(QLabel("", self))  # Spacer
        self.swap_btn = QPushButton("⇄", self)
        self.swap_btn.setObjectName("swapLangBtn")
        self.swap_btn.setToolTip("Swap source and target languages")
        self.swap_btn.clicked.connect(self._swap_languages)
        swap_vbox.addWidget(self.swap_btn)
        lang_action_row.addLayout(swap_vbox)

        # Target Language
        tgt_vbox = QVBoxLayout()
        tgt_vbox.setSpacing(4)
        tgt_lbl = QLabel("TRANSLATE TO", self)
        tgt_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #94A3B8;")
        self.tgt_lang_combo = QComboBox(self)
        for code, name in LANGUAGE_OPTIONS:
            if code != "auto":
                self.tgt_lang_combo.addItem(name, code)
        self.tgt_lang_combo.setCurrentIndex(1)  # Spanish default
        tgt_vbox.addWidget(tgt_lbl)
        tgt_vbox.addWidget(self.tgt_lang_combo)
        lang_action_row.addLayout(tgt_vbox)

        lang_action_row.addSpacing(16)

        # Action Buttons
        btn_vbox = QVBoxLayout()
        btn_vbox.setSpacing(4)
        btn_vbox.addWidget(QLabel("", self))  # Spacer
        actions_hbox = QHBoxLayout()
        actions_hbox.setSpacing(8)

        self.start_btn = QPushButton("🎙️ START CAPTIONING", self)
        self.start_btn.setObjectName("heroStartBtn")
        self.start_btn.clicked.connect(self._toggle_captioning)
        actions_hbox.addWidget(self.start_btn)

        self.clear_btn = QPushButton("🗑️ Clear", self)
        self.clear_btn.clicked.connect(self._clear_captions)
        actions_hbox.addWidget(self.clear_btn)

        self.export_btn = QPushButton("📥 Export", self)
        self.export_btn.clicked.connect(self._export_session)
        actions_hbox.addWidget(self.export_btn)

        btn_vbox.addLayout(actions_hbox)
        lang_action_row.addLayout(btn_vbox)

        controls_layout.addLayout(lang_action_row)

        # Row C: Audio Level Visualizer
        vis_row = QHBoxLayout()
        vis_row.setSpacing(10)
        vis_label = QLabel("AUDIO ENERGY:", self)
        vis_label.setStyleSheet("font-size: 11px; font-weight: 700; color: #94A3B8;")
        self.visualizer = AudioVisualizerWidget(bar_count=28, parent=self)
        vis_row.addWidget(vis_label)
        vis_row.addWidget(self.visualizer, stretch=1)
        controls_layout.addLayout(vis_row)

        main_layout.addWidget(controls_group)

        # 3. Dual Live Caption Panels (Splitter for resizable views)
        splitter = QSplitter(Qt.Vertical, self)
        splitter.setHandleWidth(6)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1E293B;
                border-radius: 3px;
            }
            QSplitter::handle:hover {
                background-color: #06B6D4;
            }
        """)

        # Panel 1: Original Speech
        self.card_source = CaptionDisplayCard(title="🎙️ LIVE CAPTIONS (Original Speech)", tag_text="English", parent=self)
        splitter.addWidget(self.card_source)

        # Panel 2: Live Translation
        self.card_target = CaptionDisplayCard(title="🌍 TRANSLATION (Live Synchronized)", tag_text="Spanish", parent=self)
        splitter.addWidget(self.card_target)

        splitter.setSizes([320, 320])
        main_layout.addWidget(splitter, stretch=1)

        # 4. Status Bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select input source and click 'Start Captioning'.")

        # Connect UI events
        self.radio_mic.toggled.connect(self._on_source_mode_changed)
        self.radio_loopback.toggled.connect(self._on_source_mode_changed)
        self.src_lang_combo.currentIndexChanged.connect(self._on_language_changed)
        self.tgt_lang_combo.currentIndexChanged.connect(self._on_language_changed)

    def _apply_theme(self) -> None:
        self.setStyleSheet(DARK_CYBER_QSS)

    def _bind_client_signals(self) -> None:
        """Connect WebSocket client signals to UI slots."""
        self.client_thread.connection_changed.connect(self._on_connection_changed)
        self.client_thread.transcription_received.connect(self._on_transcription_received)
        self.client_thread.translation_received.connect(self._on_translation_received)
        self.client_thread.status_received.connect(self._on_status_received)
        self.client_thread.error_received.connect(self._on_error_received)
        self.client_thread.audio_level_received.connect(self.visualizer.set_rms_level)

    # --------------------------------------------------------------------------
    # Audio Devices & Mode Switching
    # --------------------------------------------------------------------------

    def _refresh_device_list(self) -> None:
        """Scan and populate the device selector based on current source mode."""
        self.device_combo.clear()
        default_combo_idx = 0
        if self.radio_mic.isChecked():
            devices = MicrophoneCapture.list_input_devices()
            if not devices:
                self.device_combo.addItem("No microphone detected", None)
            for idx, dev in enumerate(devices):
                label = f"{dev['name']}"
                if dev.get("is_default"):
                    label += " (Default)"
                    default_combo_idx = idx
                self.device_combo.addItem(label, dev["index"])
        else:
            devices = SystemAudioCapture.list_loopback_devices()
            if not devices:
                self.device_combo.addItem("No playback device found", None)
            for idx, dev in enumerate(devices):
                label = f"{dev['name']}"
                if dev.get("is_default"):
                    label += " (Default Output)"
                    default_combo_idx = idx
                self.device_combo.addItem(label, dev["index"])

        if self.device_combo.count() > 0:
            self.device_combo.setCurrentIndex(default_combo_idx)

    def _on_source_mode_changed(self) -> None:
        """Handle toggle between Microphone and System Audio modes."""
        if self.is_recording:
            # Stop current recording before switching
            self._stop_captioning()
        self._refresh_device_list()
        mode_str = "Microphone" if self.radio_mic.isChecked() else "System Audio (Loopback)"
        self.status_bar.showMessage(f"Input source changed to: {mode_str}")

    def _on_language_changed(self) -> None:
        """Update language tags and notify backend."""
        src_code = self.src_lang_combo.currentData()
        tgt_code = self.tgt_lang_combo.currentData()
        src_name = self.src_lang_combo.currentText().split("(")[0].strip()
        tgt_name = self.tgt_lang_combo.currentText().split("(")[0].strip()

        self.card_source.set_tag(src_name)
        self.card_target.set_tag(tgt_name)

        # Clear interim text and mark language transition in target card if changed mid-session
        if self.is_recording:
            self.card_target.append_final_text(f" [→ {tgt_name}]")

        if self.client_thread.isRunning():
            self.client_thread.set_languages(src_code, tgt_code)

    def _swap_languages(self) -> None:
        """Swap source and target languages."""
        src_code = self.src_lang_combo.currentData()
        tgt_code = self.tgt_lang_combo.currentData()

        # Cannot target 'auto'
        if src_code == "auto":
            target_idx = self.tgt_lang_combo.findData(src_code)
            if target_idx < 0:
                src_code = "en"

        src_idx = self.src_lang_combo.findData(tgt_code)
        tgt_idx = self.tgt_lang_combo.findData(src_code)

        if src_idx >= 0:
            self.src_lang_combo.setCurrentIndex(src_idx)
        if tgt_idx >= 0:
            self.tgt_lang_combo.setCurrentIndex(tgt_idx)

    # --------------------------------------------------------------------------
    # Start / Stop Captioning Session
    # --------------------------------------------------------------------------

    def _toggle_captioning(self) -> None:
        if self.is_recording:
            self._stop_captioning()
        else:
            self._start_captioning()

    def _start_captioning(self) -> None:
        if not self.is_connected and not (self.client_thread and self.client_thread.is_connected):
            QMessageBox.warning(
                self,
                "Backend Connecting...",
                "The Anuvad local speech backend is still initializing or offline.\n\n"
                "Please allow a few seconds for the status badge to show 'Connected' before starting audio capture.",
            )
            return

        selected_dev = self.device_combo.currentData()
        src_code = self.src_lang_combo.currentData()
        tgt_code = self.tgt_lang_combo.currentData()

        is_mic = self.radio_mic.isChecked()

        try:
            if is_mic:
                self.mic_capture = MicrophoneCapture(
                    on_audio_chunk=self.client_thread.queue_audio_chunk,
                    device_index=selected_dev,
                )
                self.mic_capture.start()
                mode_desc = "Microphone"
            else:
                self.loopback_capture = SystemAudioCapture(
                    on_audio_chunk=self.client_thread.queue_audio_chunk,
                    device_index=selected_dev,
                )
                self.loopback_capture.start()
                mode_desc = "System Audio"

            # Notify backend WebSocket client
            self.client_thread.start_session(source_lang=src_code, target_lang=tgt_code)

            self.is_recording = True
            self.start_btn.setText("⏹️ STOP CAPTIONING")
            self.start_btn.setProperty("recording", "true")
            self.start_btn.setStyle(self.start_btn.style())
            self.status_badge.set_status("listening", f"Listening ({mode_desc})")
            self.status_bar.showMessage(f"Streaming {mode_desc} audio to Anuvad backend...")

            # Disable controls during session
            self.radio_mic.setEnabled(False)
            self.radio_loopback.setEnabled(False)
            self.device_combo.setEnabled(False)

        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Audio Capture Error",
                f"Could not start {('Microphone' if is_mic else 'System Audio')} capture:\n\n{e}\n\n"
                "Please verify your audio device settings.",
            )
            self.status_badge.set_status("error", "Device Error")

    def _stop_captioning(self) -> None:
        self.is_recording = False

        if self.mic_capture:
            self.mic_capture.stop()
            self.mic_capture = None

        if self.loopback_capture:
            self.loopback_capture.stop()
            self.loopback_capture = None

        self.client_thread.stop_session()
        self.visualizer.set_rms_level(0.0)

        self.start_btn.setText("🎙️ START CAPTIONING")
        self.start_btn.setProperty("recording", "false")
        self.start_btn.setStyle(self.start_btn.style())

        self.status_badge.set_status("ready", "Ready")
        self.status_bar.showMessage("Captioning session stopped.")

        self.radio_mic.setEnabled(True)
        self.radio_loopback.setEnabled(True)
        self.device_combo.setEnabled(True)

    # --------------------------------------------------------------------------
    # Live Caption Events & Backend Slots
    # --------------------------------------------------------------------------

    @Slot(bool, str)
    def _on_connection_changed(self, is_connected: bool, status_text: str) -> None:
        self.is_connected = is_connected
        if is_connected:
            if not self.is_recording:
                self.status_badge.set_status("ready", "Connected")
            self.status_bar.showMessage(f"Connected to backend ({self.backend_url})")
        else:
            self.status_badge.set_status("error", status_text)
            self.status_bar.showMessage(f"Backend: {status_text}")

    @Slot(str, bool)
    def _on_transcription_received(self, text: str, is_final: bool) -> None:
        if is_final:
            self.card_source.append_final_text(text)
            self.status_badge.set_status("processing", "Transcribing...")
            QTimer.singleShot(300, lambda: self._restore_listening_status())
        else:
            self.card_source.set_interim_text(text)

    @Slot(str, str, str, bool)
    def _on_translation_received(self, text: str, source_text: str, target_lang: str, is_final: bool = True) -> None:
        if not text:
            return
        if is_final:
            self.card_target.append_final_text(text)
        else:
            self.card_target.set_interim_text(text)

    def _restore_listening_status(self) -> None:
        if self.is_recording:
            mode = "Microphone" if self.radio_mic.isChecked() else "System Audio"
            self.status_badge.set_status("listening", f"Listening ({mode})")

    @Slot(str, str)
    def _on_status_received(self, status_type: str, message: str) -> None:
        self.status_bar.showMessage(f"Backend status: {message}")

    @Slot(str)
    def _on_error_received(self, error_message: str) -> None:
        logger.warning(f"Backend error: {error_message}")
        self.status_bar.showMessage(f"Error: {error_message}")

    # --------------------------------------------------------------------------
    # Clear & Export
    # --------------------------------------------------------------------------

    def _clear_captions(self) -> None:
        self.card_source.clear()
        self.card_target.clear()
        self.status_bar.showMessage("Captions and translations cleared.")

    def _export_session(self) -> None:
        source_text = self.card_source.text_edit.toPlainText().strip()
        target_text = self.card_target.text_edit.toPlainText().strip()

        if not source_text and not target_text:
            QMessageBox.information(self, "Export", "No captions or translations to export.")
            return

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"anuvad_session_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Session Transcript",
            default_filename,
            "Text Files (*.txt);;All Files (*)",
        )
        if not file_path:
            return

        src_name = self.src_lang_combo.currentText()
        tgt_name = self.tgt_lang_combo.currentText()

        content = [
            "=" * 50,
            "ANUVAD SPEECH CAPTIONING & TRANSLATION SESSION",
            f"Recorded: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Source Language: {src_name} | Target Language: {tgt_name}",
            "=" * 50 + "\n",
            f"[ORIGINAL SPEECH ({src_name})]",
            source_text or "(No speech recorded)",
            "\n" + "-" * 50 + "\n",
            f"[TRANSLATION ({tgt_name})]",
            target_text or "(No translation recorded)",
            "\n" + "=" * 50,
        ]

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(content))
            self.status_bar.showMessage(f"Session transcript exported to {Path(file_path).name}")
            QMessageBox.information(self, "Export Complete", f"Saved successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")

    def closeEvent(self, event) -> None:
        """Clean shutdown of audio captures and WebSocket thread on window close."""
        self._stop_captioning()
        self.client_thread.stop_client()
        self.client_thread.wait(2000)
        event.accept()
