<div align="center">

```text
     █████╗ ███╗   ██╗██╗   ██╗██╗   ██╗ █████╗ ██████╗ 
    ██╔══██╗████╗  ██║██║   ██║██║   ██║██╔══██╗██╔══██╗
    ███████║██╔██╗ ██║██║   ██║██║   ██║███████║██║  ██║
    ██╔══██║██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║██║  ██║
    ██║  ██║██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║██████╔╝
    ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═════╝ 
```

# ANUVAD — Real-Time Multilingual Speech Captioning System

**Unified Local-First Application Suite • Zero Cloud ASR Lock-In • Sub-Second Streaming Latency**

[![Platform: Windows Desktop](https://img.shields.io/badge/Platform-Windows%20Desktop%20(.exe)-0078D6?logo=windows&logoColor=white)](#4-desktop-application-primary)
[![Interface: PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52?logo=qt&logoColor=white)](#4-desktop-application-primary)
[![Secondary: Web App](https://img.shields.io/badge/Interface-Web%20Application-06B6D4?logo=googlechrome&logoColor=white)](#7-web-application-secondary)
[![Extension: Chrome MV3](https://img.shields.io/badge/Extension-Chrome%20Manifest%20V3-4285F4?logo=googlechrome&logoColor=white)](#8-chrome-extension-additional)
[![Engine: Faster-Whisper](https://img.shields.io/badge/ASR-Faster--Whisper%20(CTranslate2)-FF6F00)](#9-tech-stack)
[![Audio: WASAPI Loopback](https://img.shields.io/badge/Audio-WASAPI%20Loopback%20(pyaudiowpatch)-blueviolet)](#6-system-audio-mode-wasapi-loopback)
[![Tests](https://img.shields.io/badge/Tests-25%20Passing-brightgreen)](#20-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[![Portfolio](https://img.shields.io/badge/Portfolio-rakinmohammedrafeeq.vercel.app-10B981?logo=vercel&logoColor=white)](https://rakinmohammedrafeeq.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-rakinmohammedrafeeq-181717?logo=github&logoColor=white)](https://github.com/rakinmohammedrafeeq)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rakin%20Mohammed%20Rafeeq-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/rakinmohammedrafeeq)

</div>

---

> 📖 **"Anuvad" (अनुवाद)** is the ancient Sanskrit and Hindi noun for **Translation** and **Interpretation**.  
> **Anuvad** is a unified, local-first speech recognition and real-time captioning suite. Powered by an on-device Faster-Whisper transformer engine, Anuvad captures live audio from your microphone or system sound (YouTube, video calls, media), transcribes words with sub-second latency, and delivers synchronized live translations — **with 100% on-device speech processing, no subscriptions, and complete data privacy.**

---

## 📑 Table of Contents

1. [Overview](#1-overview)
2. [Key Features](#2-key-features)
3. [Architecture](#3-architecture)
4. [Desktop Application (Primary)](#4-desktop-application-primary)
5. [Microphone Mode](#5-microphone-mode)
6. [System Audio Mode (WASAPI Loopback)](#6-system-audio-mode-wasapi-loopback)
7. [Web Application (Secondary)](#7-web-application-secondary)
8. [Chrome Extension (Additional)](#8-chrome-extension-additional)
9. [Tech Stack](#9-tech-stack)
10. [Requirements](#10-requirements)
11. [Installation](#11-installation)
12. [Configuration](#12-configuration)
13. [Running the Backend](#13-running-the-backend)
14. [Running the Desktop Application](#14-running-the-desktop-application)
15. [Building Anuvad.exe](#15-building-anuvadexe)
16. [Running the Web Application](#16-running-the-web-application)
17. [Installing the Chrome Extension](#17-installing-the-chrome-extension)
18. [Usage](#18-usage)
19. [Project Structure](#19-project-structure)
20. [Testing](#20-testing)
21. [Privacy](#21-privacy)
22. [Limitations](#22-limitations)
23. [Future Improvements](#23-future-improvements)
24. [Contributing, License & Author](#24-contributing-license--author)

---

## 1. Overview

Spoken language should connect people, not divide them. Yet across higher education, remote work, accessibility, and international media:
- **Language Barriers**: Millions of students, engineers, and researchers consume lectures, webinars, and meetings conducted in non-native languages, struggling with fast speech, heavy accents, and complex technical terminology.
- **Hearing Accessibility**: Individuals who are deaf, deafened, or hard-of-hearing encounter live streams, calls, and videos that have zero real-time captioning available.
- **The SaaS Subscription Trap**: Cloud meeting transcription services (such as Otter.ai, Zoom AI Companion, and Teams Premium) charge $10 to $30/month per user, lock your data in proprietary silos, and fail entirely when offline.
- **The Privacy Dilemma**: Streaming your raw voice and proprietary boardroom debates to third-party cloud ASR servers creates severe compliance, regulatory, and corporate confidentiality risks.

### The Solution: Anuvad Unified Application Suite
Anuvad solves this by providing a complete, local-first speech captioning and translation environment. Instead of maintaining three disconnected tools, Anuvad is engineered as a **unified software suite**:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                          ANUVAD APPLICATION SUITE                       │
├───────────────────────────┬──────────────────────────┬──────────────────┤
│ 1. Windows Desktop App    │ 2. Web Application       │ 3. Chrome Ext    │
│    (PRIMARY INTERFACE)    │    (SECONDARY INTERFACE) │    (ADDITIONAL)  │
│    • Standalone .exe / GUI│    • Browser client      │    • Side panel  │
│    • Mic & System Audio   │    • Browser mic capture │    • Tab capture │
├───────────────────────────┴──────────────────────────┴──────────────────┤
│                     SHARED PYTHON SPEECH CORE BACKEND                   │
│             FastAPI • Faster-Whisper • Silero VAD • Translation         │
└─────────────────────────────────────────────────────────────────────────┘
```

The core speech-processing intelligence is shared across all three interfaces:
1. **Windows Desktop Application (`Anuvad.exe`) [PRIMARY]**: The flagship interface built with PySide6 (Qt6). Runs natively on Windows, offering physical microphone input and Windows WASAPI Loopback capture to transcribe and translate whatever sound is playing through your computer speakers.
2. **Browser Web Application [SECONDARY]**: Accessible at `http://127.0.0.1:8000` from any modern web browser, offering a zero-install browser interface for microphone captioning.
3. **Chrome Extension (Manifest V3) [ADDITIONAL]**: Operates as a companion side panel directly inside Chromium browsers, capturing internal tab audio (YouTube, Coursera, Google Meet) via `chrome.tabCapture`.

---

## 2. Key Features

- 🎙️ **Dual-Mode Desktop Audio Capture**:
  - **Microphone Mode**: Real-time voice capture from any selected USB or built-in microphone via `sounddevice`.
  - **System Audio Mode (WASAPI Loopback)**: Captures audio output directly from Windows speakers/headphones using `pyaudiowpatch`, enabling live captions of YouTube videos, video calls, games, or podcasts without physical microphone bleed.
- ⚡ **Local-First Transformer ASR**: Powered by `faster-whisper` (CTranslate2 INT8 quantized models) running directly on your CPU or GPU. Delivers transcription with sub-second response times.
- 🌐 **Synchronized Dual-Pane Translation**: Real-time side-by-side display with the original speech transcript on the left pane and translated text on the right pane.
- 🎛️ **Live Audio Visualizer**: 28-segment reactive equalizer responding dynamically to audio input amplitude.
- 🔄 **One-Click Language Swap**: Quickly flip source and target languages with the `⇄` button.
- 📥 **Session Transcript Export**: Export timestamped bilingual conversations directly to structured `.txt` files.
- 📦 **Standalone Windows Executable**: Bundled with PyInstaller into a clean `Anuvad.exe` binary with all GUI and audio dependencies included.
- 🔒 **Absolute Speech Privacy**: Speech recognition runs 100% locally on your computer. Your raw voice audio never leaves your RAM and is never written to disk or sent to cloud servers.

---

## 3. Architecture

All client interfaces connect to the unified Python speech backend using a standard bi-directional WebSocket protocol (`ws://127.0.0.1:8000/ws`), transmitting raw 16kHz mono 16-bit PCM binary frames.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT INTERFACES                                    │
│                                                                                        │
│   ┌────────────────────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │
│   │    WINDOWS DESKTOP (PRIMARY)   │  │  WEB APPLICATION │  │   CHROME EXTENSION   │   │
│   │         PySide6 / Qt6          │  │   (SECONDARY)    │  │     (ADDITIONAL)     │   │
│   │ ┌────────────┐ ┌─────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────────┐ │   │
│   │ │ Microphone │ │   System    │ │  │ │  Web Audio   │ │  │ │ chrome.tabCapture│ │   │
│   │ │  Capture   │ │ Audio Loop  │ │  │ │  AudioWorklet│ │  │ │  Offscreen Audio │ │   │
│   │ └──────┬─────┘ └──────┬──────┘ │  │ └──────┬───────┘ │  │ └──────────┬───────┘ │   │
│   │        └───────┬──────┘        │  │        │         │  │            │         │   │
│   │         QThread Audio Queue    │  │        │         │  │            │         │   │
│   └────────────────┬───────────────┘  └────────┼─────────┘  └────────────┼─────────┘   │
│                    │                           │                         │             │
│                    └─────────────────────┬─────┴─────────────────────────┘             │
│                                          │ 16kHz Mono PCM16 Frames                     │
│                                          ▼ (WebSocket: ws://127.0.0.1:8000/ws)         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                       SHARED PYTHON BACKEND CORE (FastAPI)                             │
│                                                                                        │
│      ┌────────────────────────────────────────────────────────────────────────┐        │
│      │                      WebSocket Handler & Session State                 │        │
│      └───────────────────────────────────┬────────────────────────────────────┘        │
│                                          │                                             │
│                                          ▼                                             │
│      ┌────────────────────────────────────────────────────────────────────────┐        │
│      │                   Acoustic Energy & Silero VAD Gate                    │        │
│      │             (Discards silence; prevents Whisper hallucinations)        │        │
│      └───────────────────────────────────┬────────────────────────────────────┘        │
│                                          │ Speech Segments                             │
│                                          ▼                                             │
│      ┌────────────────────────────────────────────────────────────────────────┐        │
│      │                Faster-Whisper Model Manager (CTranslate2)               │        │
│      │          • In-Memory Preloaded Singleton (tiny / base / small)          │        │
│      │          • Local Agreement Streaming Prefix-Locking Buffer             │        │
│      └───────────────────────────────────┬────────────────────────────────────┘        │
│                                          │ Final & Interim Text                        │
│                                          ▼                                             │
│      ┌────────────────────────────────────────────────────────────────────────┐        │
│      │                      Resilient Translation Service                     │        │
│      │         • In-Memory LRU Cache • Google / MyMemory Cascading Fallback   │        │
│      └───────────────────────────────────┬────────────────────────────────────┘        │
│                                          │                                             │
│                                          ▼ JSON Protocol Payload                       │
│                        {"type": "transcription", "text": "...", "is_final": true}      │
│                        {"type": "translation", "translated_text": "..."}              │
│                                          │                                             │
└──────────────────────────────────────────┴─────────────────────────────────────────────┘
                                           │ Dispatches updates back to
                                           ▼ active client (Desktop / Web / Extension)
```

---

## 4. Desktop Application (Primary)

The Windows Desktop Application is the **primary** user interface for Anuvad. Built with **PySide6 (Qt6)** and customized with a modern dark cyber aesthetic, it runs as a native Windows process with direct hardware access.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎙️ ANUVAD — Real-Time Multilingual Speech Captioning                       [—] [口] [X]│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT SOURCE                                                  STATUS: ● Ready          │
│ (•) Microphone   ( ) System Audio (Loopback)                                           │
│ Device: [ Speakers (Realtek(R) Audio) [Loopback]                                   ▼] 🔄│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ LANGUAGE CONFIGURATION                                                                 │
│ Speak In: [ English                        ▼]   ⇄   Translate To: [ Spanish        ▼]  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [                     🎙️  START CAPTIONING (SPACEBAR)                                ]  │
│ Audio Level: [ ▇▇▇▇▇▇▇▇▇▇▇▇▇▇░░░░░░░░░░░░░░░░ ] -18 dB                                │
├────────────────────────────────────────────────────┬───────────────────────────────────┤
│ 📝 LIVE CAPTIONS (ORIGINAL SPEECH)   [📋] [142 w]  │ 🌐 LIVE TRANSLATION   [📋] [139 w]│
│                                                    │                                   │
│ Welcome everyone to today's technical briefing.    │ Bienvenidos a todos a la sesión   │
│ We are reviewing the local speech recognition      │ técnica de hoy. Estamos revisando │
│ pipeline and system audio loopback capture.        │ el pipeline de reconocimiento de  │
│ The audio is processed entirely on this machine.   │ voz local y captura de audio.     │
│                                                    │                                   │
├────────────────────────────────────────────────────┴───────────────────────────────────┤
│ ● Server: ws://127.0.0.1:8000/ws   |   Device: WASAPI Loopback   |   [📥 Export Session]│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Capabilities
- **Direct Hardware Access**: Select physical input microphones or active loopback output devices from dynamic dropdown menus.
- **Dedicated Threading**: Audio capture and WebSocket networking run on background `QThread` workers, guaranteeing that the user interface never stutters or drops frames.
- **Reactive UI**: Displays real-time audio volume via a custom 28-bar visualizer, status pills (`Ready`, `Connected`, `Listening`, `Processing`, `Error`), and word count statistics.
- **Keyboard Shortcuts**: Start and stop captioning instantly with the `Spacebar` or `Ctrl+S`.

---

## 5. Microphone Mode

In **Microphone Mode**, Anuvad captures live audio directly from any microphone connected to your computer:
1. **Device Enumeration**: Uses `sounddevice` to query the host operating system for available audio input channels.
2. **Audio Streaming**: Opens a non-blocking `RawInputStream` configured for **16,000 Hz, 1-channel (mono), 16-bit signed integer PCM**.
3. **Queue Buffering**: Audio chunks are pushed into a thread-safe `queue.Queue`, decoupling hardware audio collection from network transmission.
4. **Volume Analysis**: The application computes Root Mean Square (RMS) energy in real time to drive the on-screen visualizer:
   $$\text{RMS} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} x_i^2}$$

Microphone mode is ideal for dictation, live lectures, personal note-taking, meetings where you are speaking, and conversational practice.

---

## 6. System Audio Mode (WASAPI Loopback)

In **System Audio Mode**, Anuvad captures internal sound playing through your computer speakers or headphones without requiring a physical microphone.

```text
┌───────────────────────┐
│ System Audio Playback │  (YouTube, Zoom, Coursera, VLC, Games)
└──────────┬────────────┘
           │ Windows Audio Session API (WASAPI)
           ▼
┌───────────────────────┐
│ Default Output Device │  (e.g., Speakers - Realtek High Definition Audio)
└──────────┬────────────┘
           │ Loopback Stream Tap (pyaudiowpatch)
           ▼
┌───────────────────────┐
│ pyaudiowpatch Worker  │  (Captures 48,000 Hz, 2-Channel Stereo Float32/Int16)
└──────────┬────────────┘
           │ 1. Downmix to Mono: data.mean(axis=1)
           ▼
┌───────────────────────┐
│ scipy.signal Resampler│  (Polyphase Resampling: 48,000 Hz ➔ 16,000 Hz)
└──────────┬────────────┘
           │ 2. Convert to PCM16: np.int16(mono * 32767.0)
           ▼
┌───────────────────────┐
│ WebSocket Dispatcher  │  (Pushes 16kHz Mono PCM16 to ws://127.0.0.1:8000/ws)
└───────────────────────┘
```

### How Windows WASAPI Loopback Works
- **Windows Audio Session API (WASAPI)** provides a loopback capture mode. In loopback mode, a client can capture the audio stream that is being sent to the rendering endpoint device.
- Standard Python audio libraries (`pyaudio`, `sounddevice`) often cannot tap into Windows loopback endpoints directly. Anuvad utilizes **`pyaudiowpatch`**, an enhanced WASAPI-aware audio library compiled specifically for Windows loopback devices.
- **Automatic Format Normalization**: System audio typically renders at 48,000 Hz or 44,100 Hz in stereo (2 channels). Anuvad automatically:
  1. Downmixes stereo channels to single-channel mono: $\text{mono}[t] = \frac{L[t] + R[t]}{2}$.
  2. Applies polyphase rational resampling via `scipy.signal.resample_poly` to convert the stream to precisely 16,000 Hz.
  3. Converts normalized float32 samples into 16-bit signed little-endian PCM bytes.
- This allows you to generate live subtitles for **YouTube videos, foreign films, online webinars, podcasts, and Google Meet/Zoom calls** where you do not have permission or ability to record microphone input.

---

## 7. Web Application (Secondary)

The Web Application provides a lightweight, zero-install browser interface running on `http://127.0.0.1:8000`.

- **Frontend Architecture**: Built using clean semantic HTML5, cyber-glassmorphic CSS3, and vanilla ES6+ JavaScript.
- **Audio Capture**: Captures microphone audio using the browser's native `navigator.mediaDevices.getUserMedia()` API and processes samples into 16,000 Hz mono PCM using Web Audio API nodes.
- **Zero Framework Bloat**: No React, Angular, or Vue build steps required. Instant page load under 100ms.
- **Cross-Platform**: Operates in any Chromium, Firefox, or Safari browser on Windows, macOS, or Linux.

---

## 8. Chrome Extension (Additional)

The Chrome Extension is a Manifest V3 browser companion that integrates Anuvad directly into your web browsing workflow.

- **Manifest V3 Architecture**: Adheres strictly to modern Chrome security standards.
- **Side Panel Interface**: Opens natively in Chrome's side panel using the `chrome.sidePanel` API, allowing you to view captions side by side with your active browser tab.
- **Tab Audio Capture**: Uses `chrome.tabCapture` combined with an `offscreen` document to capture the audio playing in any tab without routing through an external microphone.
- **Shared Gateway**: Streams captured audio directly to the local backend at `ws://127.0.0.1:8000/ws`.

---

## 9. Tech Stack

| Layer | Technologies & Libraries | Role |
| :--- | :--- | :--- |
| **Desktop GUI (Primary)** | `PySide6` (Qt 6.11), `QtCore`, `QtWidgets` | Native Windows GUI application, high-DPI scaling, QSS dark cyber styling |
| **Desktop Audio Capture** | `pyaudiowpatch`, `sounddevice`, `numpy`, `scipy` | Windows WASAPI Loopback system audio capture, microphone streaming, polyphase resampling |
| **Backend Framework** | `FastAPI`, `Starlette`, `Uvicorn` | Asynchronous ASGI server, HTTP static hosting, WebSocket protocol handling |
| **Speech Recognition** | `faster-whisper`, `CTranslate2`, `torch` | Fast transformer inference, 8-bit quantization (INT8), multi-threaded CPU/GPU processing |
| **Voice Activity Gate** | `Silero VAD v5`, RMS energy fallback | Deep neural speech/silence classification, prevents transcription drift and hallucination |
| **Translation Engine** | `deep-translator`, `urllib`, in-memory LRU cache | Resilient multi-tier translation cascading across supported language pairs |
| **Packaging & Build** | `PyInstaller` | Bundles Python runtime, Qt libraries, and audio backends into `Anuvad.exe` |
| **Web Frontend (Secondary)**| HTML5, CSS3, ES6 JavaScript, Web Audio API | Zero-dependency browser interface |
| **Chrome Extension** | Chrome Manifest V3, `chrome.tabCapture`, Offscreen API | In-browser tab audio capture and side-panel captioning |
| **Testing Suite** | `pytest`, `pytest-asyncio`, `anyio` | 25 automated unit and integration tests |

---

## 10. Requirements

### Operating System
- **Desktop Application & WASAPI Loopback**: Windows 10 or Windows 11 (64-bit).
- **Backend & Web Application**: Cross-platform (Windows, macOS, Linux).
- **Chrome Extension**: Any Chromium-based browser (Google Chrome, Microsoft Edge, Brave, Opera) supporting Manifest V3.

### Software Prerequisites
- **Python**: Version `3.9` through `3.12` (Python `3.10.9` recommended).
- **Git**: For cloning the repository.
- **C++ Build Tools**: Standard Windows Universal C Runtime (included in modern Windows 10/11 updates).

### Hardware Recommendations
| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Processor (CPU)** | Intel Core i3 / AMD Ryzen 3 (AVX support) | Intel Core i5/i7/i9 or AMD Ryzen 5/7/9 (AVX2 support) |
| **System Memory (RAM)**| 4 GB RAM | 8 GB or 16 GB RAM |
| **Storage** | 1.5 GB free disk space | 5.0 GB free SSD space (for multiple model weights) |
| **Graphics (GPU)** | Not required (runs efficiently on CPU) | NVIDIA GPU with CUDA 11.8+ (optional, for `large` models) |

---

## 11. Installation

### 1. Clone the Repository
```bash
git clone https://github.com/rakinmohammedrafeeq/anuvad.git
cd anuvad
```

### 2. Create and Activate a Virtual Environment
```powershell
# In Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(For Command Prompt, use `.\venv\Scripts\activate.bat`)*

### 3. Install Required Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

> [!NOTE]
> On the first run, `faster-whisper` will automatically download the default lightweight model (`tiny`, ~75 MB) to your local Hugging Face cache directory. Subsequent launches load in under 1 second.

---

## 12. Configuration

Anuvad is designed to work out of the box without required configuration, but can be customized via environment variables or CLI flags.

Create an optional `.env` file in the project root:

```env
# Server Networking
ANUVAD_HOST=127.0.0.1
ANUVAD_PORT=8000

# Speech Recognition Engine
ANUVAD_WHISPER_MODEL=tiny
ANUVAD_DEVICE=auto
ANUVAD_COMPUTE_TYPE=int8
ANUVAD_CPU_THREADS=4

# Voice Activity Detection
ANUVAD_ENABLE_VAD=true
ANUVAD_VAD_THRESHOLD=0.5

# Translation
ANUVAD_ENABLE_TRANSLATION=true
ANUVAD_SOURCE_LANGUAGE=auto
ANUVAD_TARGET_LANGUAGE=en
```

---

## 13. Running the Backend

The shared backend powers all three interfaces. Start it with:

```powershell
python run.py
```

### Startup Output
```text
============================================================
🎤 Starting ANUVAD Speech Captioning & Translation Server
============================================================
  • Address:            http://127.0.0.1:8000
  • WebSocket Endpoint: ws://127.0.0.1:8000/ws
  • Whisper Model:      tiny
  • Target Device:      auto
  • Translation:        Enabled
  • Voice Activity Det: Enabled
============================================================
  👉 Open your browser at: http://127.0.0.1:8000
============================================================
```

### CLI Command Options
```powershell
# Use a higher accuracy model:
python run.py --model base

# Run on NVIDIA GPU with FP16 precision:
python run.py --device cuda --compute-type float16

# Run on an alternative port:
python run.py --port 8080

# Run in pure offline ASR mode (disables outbound translation lookups):
python run.py --no-translate
```

---

## 14. Running the Desktop Application

The Desktop Application is the primary client interface.

```powershell
python run_desktop.py
```

> [!TIP]
> If the backend server is not already running, the desktop application will automatically detect that the local gateway is offline and spawn a background backend process for you.

### Selecting Your Audio Source
1. **To caption your own voice**: Select **Microphone** and pick your mic from the dropdown.
2. **To caption videos, calls, or games**: Select **System Audio (Loopback)** and select your active speaker device (e.g. `Speakers (Realtek(R) Audio) [Loopback]`).
3. Press **🎙️ START CAPTIONING** (or tap the `Spacebar`).

---

## 15. Building Anuvad.exe

You can bundle the desktop application into a standalone Windows executable using the preconfigured PyInstaller specification file:

```powershell
pyinstaller Anuvad.spec
```

### Build Details
- **Build Output**: Located in `dist/Anuvad/Anuvad.exe` (~61 MB).
- **Self-Contained**: Bundles PySide6, Qt6 runtime binaries, `pyaudiowpatch`, `sounddevice`, `scipy`, and application themes.
- **Clean Separation**: Excludes heavy server-side PyTorch ML models from the desktop UI binary so the executable remains compact and launches instantaneously.

To launch the built executable:
```powershell
.\dist\Anuvad\Anuvad.exe
```

---

## 16. Running the Web Application

With the backend running (`python run.py`):
1. Open your browser and navigate to:
   ```text
   http://127.0.0.1:8000
   ```
2. Select your **Speak In** (source) and **Translate To** (target) languages.
3. Click **🎙️ Start Listening** and grant microphone permissions when prompted by your browser.
4. Speak naturally. Live speech transcripts and translations will stream into the dual panes in real time.

---

## 17. Installing the Chrome Extension

1. Open Google Chrome (or Edge/Brave) and navigate to `chrome://extensions`.
2. Enable **Developer mode** using the toggle in the top-right corner.
3. Click the **Load unpacked** button in the top-left corner.
4. Select the `chrome_extension/` directory inside the Anuvad repository:
   ```text
   d:\Projects\Anuvad\chrome_extension
   ```
5. Click the **Puzzle piece** (Extensions) icon in your browser toolbar and pin **Anuvad**.
6. Open any tab playing audio (YouTube, Coursera, online lecture), click the Anuvad extension icon to open the **Side Panel**, and click **🎙️ Start Translation**.

---

## 18. Usage

### Workflow Walkthrough
1. **Choose an Interface**:
   - For system-wide audio or desktop use: Launch the **Desktop Application** (`run_desktop.py` or `Anuvad.exe`).
   - For quick browser testing: Open the **Web Application** at `http://127.0.0.1:8000`.
   - For in-browser tab captions: Open the **Chrome Extension** side panel.
2. **Select Language Pair**:
   - Choose your source language or keep it on `Auto Detect`.
   - Choose your target translation language (e.g. Spanish, French, German, Hindi, Japanese).
   - Use `⇄` to swap languages instantly.
3. **Start Capture**:
   - In Desktop App: Select `Microphone` or `System Audio (Loopback)`. Click `START CAPTIONING`.
   - In Web App: Click `Start Listening`.
   - In Chrome Extension: Click `Start Translation`.
4. **View Real-Time Results**:
   - Words stream in immediately with low-latency hypothesis updates.
   - The Local Agreement algorithm locks final sentences when pauses occur.
   - Dual panes display original speech alongside translated text.
5. **Export Your Session**:
   - Click `📋 Copy` on either card to copy text to your clipboard.
   - Click `📥 Export Session` to download a complete timestamped bilingual transcript.

---

## 19. Project Structure

```text
Anuvad/
├── backend/                       # Shared Speech Processing & Server Core
│   └── app/
│       ├── main.py                # FastAPI ASGI server, static files, WebSocket routes
│       ├── audio/
│       │   ├── buffer.py          # PCM16 byte accumulator & floating-point normalizer
│       │   └── vad.py             # Silero VAD v5 with mathematical RMS fallback
│       ├── speech/
│       │   ├── model.py           # WhisperModelManager singleton (CTranslate2)
│       │   └── streaming.py       # StreamingTranscriber with Local Agreement prefix-locking
│       ├── translation/
│       │   └── service.py         # Resilient cascading translation service & LRU cache
│       ├── websocket/
│       │   └── handler.py         # Bi-directional WebSocket protocol engine
│       └── config/
│           └── settings.py        # Centralized typed configuration & language registries
│
├── desktop/                       # PRIMARY INTERFACE: Windows Desktop Application
│   ├── app/
│   │   ├── main.py                # PySide6 application lifecycle & backend auto-spawn
│   │   └── client.py              # Threaded QThread WebSocket client & audio dispatcher
│   ├── audio/
│   │   ├── mic_capture.py         # Microphone capture stream (sounddevice)
│   │   ├── loopback_capture.py    # Windows WASAPI Loopback capture (pyaudiowpatch)
│   │   └── resampler.py           # Audio conversion (stereo downmixing, polyphase resampling)
│   ├── ui/
│   │   ├── main_window.py         # Main UI layout (Input sources, languages, dual panes)
│   │   ├── widgets.py             # Audio visualizer, status pills, caption cards
│   │   └── theme.py               # Dark cyber stylesheet (QSS)
│
├── web/                           # SECONDARY INTERFACE: Browser Web Application
│   ├── index.html                 # Web application markup
│   ├── css/styles.css             # Glassmorphic dark styling
│   ├── js/app.js                  # Browser WebSocket client & Web Audio processor
│   └── assets/                    # Application logos and favicons
│
├── chrome_extension/              # ADDITIONAL INTERFACE: Browser Companion
│   ├── manifest.json              # Chrome Manifest V3 configuration
│   ├── sidepanel.html             # Native side panel layout
│   ├── sidepanel.js               # Side panel UI controller & WebSocket bridge
│   ├── offscreen.html             # Headless offscreen document
│   ├── offscreen.js               # Tab audio capture pipeline via chrome.tabCapture
│   └── icons/                     # Extension branding icons
│
├── tests/                         # Comprehensive Automated Test Suite
│   ├── test_audio.py              # PCM16 conversion, buffering, and byte-alignment tests
│   ├── test_config.py             # Configuration validation & environment override tests
│   ├── test_desktop_audio.py      # Resampling, stereo downmix, RMS, device discovery tests
│   ├── test_translation.py        # Translation cascading, caching, and fallback tests
│   └── test_websocket.py          # HTTP health checks, language endpoints, WebSocket lifecycles
│
├── Anuvad.spec                    # PyInstaller packaging configuration
├── run.py                         # Root launcher for Shared Backend Server
├── run_desktop.py                 # Root launcher for Windows Desktop Application
├── requirements.txt               # Unified project dependencies
├── HOW_TO_RUN.md                  # Quick-start instructions for users
└── README.md                      # Comprehensive technical architecture & documentation
```

---

## 20. Testing

Anuvad includes a comprehensive automated test suite covering audio conversion, resampling, configuration, translation resilience, WebSocket protocol lifecycles, and device discovery.

### Running the Test Suite
```powershell
python -m pytest tests/ -v
```

### Verified Test Output (25 Passing Tests)
```text
============================= test session starts =============================
platform win32 -- Python 3.10.9, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Projects\Anuvad
collected 25 items

tests/test_audio.py::test_pcm16_to_float32_conversion PASSED             [  4%]
tests/test_audio.py::test_pcm16_empty_and_odd_bytes PASSED               [  8%]
tests/test_audio.py::test_float32_to_pcm16_roundtrip PASSED              [ 12%]
tests/test_audio.py::test_audio_buffer_lifecycle PASSED                  [ 16%]
tests/test_config.py::test_default_config PASSED                         [ 20%]
tests/test_config.py::test_supported_languages PASSED                    [ 24%]
tests/test_config.py::test_env_override PASSED                           [ 28%]
tests/test_desktop_audio.py::test_to_mono_stereo_downmix PASSED          [ 32%]
tests/test_desktop_audio.py::test_to_mono_int16_normalization PASSED     [ 36%]
tests/test_desktop_audio.py::test_resample_48k_to_16k PASSED             [ 40%]
tests/test_desktop_audio.py::test_resample_same_rate_noop PASSED         [ 44%]
tests/test_desktop_audio.py::test_resample_empty_array PASSED            [ 48%]
tests/test_desktop_audio.py::test_float32_to_pcm16_bytes PASSED          [ 52%]
tests/test_desktop_audio.py::test_calculate_rms PASSED                   [ 56%]
tests/test_desktop_audio.py::test_microphone_device_enumeration PASSED   [ 60%]
tests/test_desktop_audio.py::test_loopback_device_enumeration PASSED     [ 64%]
tests/test_translation.py::test_same_language_bypass PASSED              [ 68%]
tests/test_translation.py::test_empty_string_handling PASSED             [ 72%]
tests/test_translation.py::test_translator_caching PASSED                [ 76%]
tests/test_translation.py::test_resilient_fallback PASSED                [ 80%]
tests/test_websocket.py::test_health_endpoint PASSED                     [ 84%]
tests/test_websocket.py::test_languages_endpoint PASSED                  [ 88%]
tests/test_websocket.py::test_root_serves_html PASSED                    [ 92%]
tests/test_websocket.py::test_favicon_and_assets PASSED                  [ 96%]
tests/test_websocket.py::test_websocket_lifecycle_and_messages PASSED    [100%]

============================= 25 passed in 9.86s ==============================
```

---

## 21. Privacy

Data privacy is a foundational design principle of Anuvad:

### 1. Automatic Speech Recognition (100% Local & Offline)
- **Zero Voice Transmission**: Raw audio from your microphone or system speakers is streamed strictly over local loopback (`ws://127.0.0.1:8000/ws`).
- **In-Memory Only**: Audio frames exist only in volatile RAM buffers during active recognition and are automatically discarded once processed. No audio files are ever written to disk.
- **No Cloud ASR**: Automatic speech recognition is executed entirely on your local CPU/GPU via CTranslate2. No proprietary speech APIs (Google Cloud Speech, AWS Transcribe, Azure Speech) are called.

### 2. Live Translation Disclosure
- For multilingual translation, Anuvad queries an in-memory LRU cache first. If a translation is not cached, the fallback translation service requests translated text strings via public translation endpoints.
- **Audio is Never Transmitted for Translation**: Only text strings are sent; raw audio is never transmitted.
- **Complete Air-Gapped Operation**: To disable all external network traffic entirely, run Anuvad with the `--no-translate` flag:
  ```powershell
  python run.py --no-translate
  ```
  In this mode, Anuvad operates 100% air-gapped with zero outbound network calls.

---

## 22. Limitations

To ensure honest, transparent engineering expectations, please note the following technical characteristics:

1. **WASAPI Loopback is Windows-Specific**:
   - The loopback capture mechanism uses the Windows Audio Session API (WASAPI) via `pyaudiowpatch`. It is natively supported on Windows 10 and Windows 11. On macOS or Linux, system audio capture requires virtual audio routing devices (such as BlackHole or PulseAudio loopbacks).
2. **Exclusive Mode Audio**:
   - If a media application takes "Exclusive Mode" control of a Windows audio device (bypassing the Windows shared audio mixer), WASAPI loopback cannot capture the audio stream. Keep audio devices in "Shared Mode" in Windows Sound Settings.
3. **Hardware & Model Sizing Trade-Offs**:
   - The default `tiny` model runs with minimal CPU usage (~150ms latency) but may make phonetic errors with strong regional accents or technical jargon.
   - Larger models (`small`, `medium`, `large-v3-turbo`) provide near human-level accuracy but require modern multi-core CPUs (AVX2) or dedicated NVIDIA GPUs (CUDA) to maintain real-time streaming speeds.
4. **Streaming Speech Latency vs. Natural Pauses**:
   - Whisper is fundamentally a sequence-to-sequence transformer. Live interim hypothesis words appear rapidly, but final sentence locking occurs when natural speech pauses (detected by VAD) are reached.

---

## 23. Future Improvements

Planned enhancements for future releases of Anuvad:
- 🪟 **Floating Subtitle Overlay Bar**: A transparent, always-on-top, click-through caption bar that floats over full-screen games, movies, and Zoom meetings.
- 🧠 **Local Offline Neural Machine Translation (NMT)**: Integration with local MarianMT or NLLB-200 models to provide 100% offline neural translation without external internet dependencies.
- 👥 **Speaker Diarization**: Multi-speaker clustering using pyannote-audio to label speakers (e.g. *Speaker 1*, *Speaker 2*) in multi-party meetings.
- 🍎 **Cross-Platform System Audio**: Implementation of native macOS CoreAudio tap and Linux PulseAudio loopback backends for non-Windows operating systems.
- 📊 **Confidence Scoring & SRT Export**: Exporting standard subtitle formats (`.srt`, `.vtt`) with millisecond timestamps and word-level token confidence metrics.

---

## 24. Contributing, License & Author

### 🤝 Contributing

Contributions, feature proposals, and bug reports are welcome!

1. Fork the repository on GitHub.
2. Create a feature branch: `git checkout -b feature/audio-filter`.
3. Ensure all tests pass: `python -m pytest tests/ -v`.
4. Commit your changes: `git commit -m "feat(audio): add high-pass noise gate"`.
5. Push to your branch and submit a Pull Request.

---

### 📄 License

This project is open-source software licensed under the **[MIT License](LICENSE)**.

```text
MIT License

Copyright (c) 2026 Rakin Mohammed Rafeeq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

### 👨‍💻 Author

<div align="center">

### **Rakin Mohammed Rafeeq**

**Full-Stack Software Engineer & Distributed Systems Architect**

[![Portfolio](https://img.shields.io/badge/Portfolio-rakinmohammedrafeeq.vercel.app-10B981?style=for-the-badge&logo=vercel&logoColor=white)](https://rakinmohammedrafeeq.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-rakinmohammedrafeeq-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rakinmohammedrafeeq)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rakin%20Mohammed%20Rafeeq-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rakinmohammedrafeeq)

📧 **Email:** [rakinmohammedrafeeq@gmail.com](mailto:rakinmohammedrafeeq@gmail.com)  
🌐 **Website:** [rakinmohammedrafeeq.vercel.app](https://rakinmohammedrafeeq.vercel.app)

</div>

---

<div align="center">

⭐ **Star this repository if Anuvad helped your project!** ⭐

</div>
