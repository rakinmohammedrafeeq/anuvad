# Anuvad Chrome Extension (Secondary Interface)

A Manifest V3 Chrome extension that captures audio from an active browser tab and streams it to the local Anuvad backend for live speech captioning and translation in a persistent side panel.

## Features

- **Tab Audio Capture**: Captures audio playing in an active browser tab using `chrome.tabCapture`.
- **Side Panel Interface**: Native Chrome side panel stays visible while you browse.
- **Real-Time Dual Captions**: Displays original speech transcripts and live translations side by side.
- **Configurable Backend**: Connects to the local Anuvad backend (default: `ws://127.0.0.1:8000/ws`).
- **Dynamic Language Selection**: Change source and target languages on the fly.

## Prerequisites

Start the local Anuvad backend before using the extension:

```bash
python backend/run.py
```

Ensure the backend is running and listening on `http://127.0.0.1:8000`.

## Installation (Developer Mode)

1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Toggle on **Developer mode** in the top right corner.
4. Click **Load unpacked**.
5. Select the `chrome_extension` directory inside this repository.
6. The "Anuvad - Multilingual Speech Captioning" extension will appear in your extensions list.

## Usage

1. Click the Anuvad extension icon in the Chrome toolbar.
2. The side panel will open on the right.
3. Open a tab playing speech or audio (e.g. YouTube, a podcast, or meeting).
4. Verify the backend URL is set to `ws://127.0.0.1:8000/ws`.
5. Select the source language spoken in the video and your desired translation language.
6. Click **Start Translation**.
7. Captions and translations will stream into the side panel in real time.
8. Click **Stop Translation** when finished.

## Extension Architecture

```
Active Tab Audio (chrome.tabCapture)
        ↓
Offscreen Document (offscreen.js)
        ↓
PCM16 16kHz Audio Chunks (WebSocket)
        ↓
Local Anuvad Backend (ws://127.0.0.1:8000/ws)
        ↓
Faster-Whisper + Translation
        ↓
Side Panel UI (sidepanel.html / sidepanel.js)
```

## Troubleshooting

- **"Connection Error" / "Disconnected"**: Ensure the local backend server is running (`python backend/run.py`) and that the server address in the extension matches `ws://127.0.0.1:8000/ws`.
- **No audio captured**: Chrome tab capture requires user interaction with the tab or audio actively playing in that tab.