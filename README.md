# Anuvad - AI-Powered Real-Time Multilingual Speech Captioning System

A sophisticated real-time speech captioning and translation system that converts live audio into text captions with multilingual translation capabilities. Built to enhance accessibility and enable cross-language communication through advanced speech processing technology.

[![Portfolio](https://img.shields.io/badge/Portfolio-rakinmohammedrafeeq.vercel.app-blue)](https://rakinmohammedrafeeq.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-rakinmohammedrafeeq-black)](https://github.com/rakinmohammedrafeeq)

## 🎯 Overview

Anuvad delivers real-time multilingual speech captioning by combining automatic speech recognition (ASR), natural language processing (NLP), and machine translation. The system provides low-latency audio processing optimized for real-time inference, making live speech accessible across language barriers.

## ✨ Key Features

- **Real-Time Speech Recognition**: Live audio-to-text transcription with minimal latency
- **Multilingual Translation**: Support for 100+ languages with automatic translation
- **Low-Latency Processing**: Optimized pipeline for responsive caption generation
- **Voice Activity Detection**: Intelligent speech detection to reduce processing overhead
- **WebSocket Support**: Real-time audio streaming with efficient bidirectional communication
- **Browser Extension**: Chrome extension for capturing and translating audio from any browser tab
- **Web Interface**: Responsive browser-based interface for live transcription
- **GPU Acceleration**: CUDA-optimized processing for enhanced performance
- **Flexible Deployment**: Multiple deployment modes including WebSocket server and local processing

## 🛠️ Technology Stack

- **Speech Recognition**: Faster-Whisper (OpenAI Whisper optimized)
- **Translation Engine**: Google Translate API integration
- **Audio Processing**: LibROSA, SoundFile
- **Real-Time Communication**: WebSockets, Socket.IO
- **Voice Activity Detection**: Silero VAD
- **Backend**: Python, FastAPI-ready architecture
- **Frontend**: HTML5, JavaScript, WebSocket API
- **Deep Learning**: PyTorch, ONNX Runtime
- **GPU Acceleration**: CUDA 11.7, cuDNN 8.5.0

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- (Optional) NVIDIA GPU with CUDA support for accelerated processing

### Required Dependencies

```bash
# Core dependencies
pip install librosa soundfile websockets

# Faster-Whisper backend (recommended)
pip install faster-whisper

# Optional: Voice Activity Detection
pip install torch torchaudio

# Optional: Translation support
pip install requests
```

### GPU Acceleration Setup (Recommended)

For optimal performance with GPU acceleration:

1. Install NVIDIA CUDA Toolkit 11.7
2. Install cuDNN 8.5.0
3. Uncomment GPU model configuration in `whisper_online.py` (line ~119)

GPU acceleration provides 4-5x faster processing compared to CPU-only inference.

## 🚀 Quick Start

### WebSocket Server Mode

Launch the real-time transcription server:

```bash
# Basic transcription
python start_whisper.py

# With translation enabled
python start_whisper.py --translate --vac --vad

# Production configuration
python start_whisper.py --host 0.0.0.0 --port 43007 --model large-v3 --translate --vac --vad
```

Access the web interface at `http://localhost:43007` or open `index.html` in your browser.

### Command Line Options

#### Server Configuration
- `--host HOST` - Server bind address (default: 0.0.0.0)
- `--port PORT` - Server port (default: 43007)

#### Model Settings
- `--model MODEL` - Whisper model size: `tiny`, `base`, `small`, `medium`, `large-v1`, `large-v2`, `large-v3`, `large-v3-turbo` (default: large-v3)
- `--language LANG` - Source language code or `auto` for detection (default: en)

#### Audio Processing
- `--chunk-size SIZE` - Audio chunk size in seconds (default: 0.3)
- `--vac` - Enable Voice Activity Controller
- `--vad` - Enable Voice Activity Detection

#### Features
- `--translate` - Enable real-time translation
- `--warmup-file FILE` - Warm up model with sample audio
- `--log-level LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### File Processing Mode

Process pre-recorded audio files:

```bash
python whisper_online.py demo.wav --language en --min-chunk-size 1
```

### Chrome Extension

1. Start the Whisper server with translation:
   ```bash
   python start_whisper.py --translate
   ```

2. Load the extension:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `chrome_extension/` folder

3. Use the extension:
   - Click extension icon to open side panel
   - Navigate to any tab with audio
   - Select languages and start translation

## 💻 Usage Examples

### As a Python Module

```python
from whisper_online import *

# Initialize ASR system
asr = FasterWhisperASR("en", "large-v3")
asr.use_vad()  # Enable voice activity detection

# Create online processor
online = OnlineASRProcessor(asr)

# Process real-time audio
while audio_available:
    audio_chunk = get_audio_chunk()  # 16kHz, float32
    online.insert_audio_chunk(audio_chunk)
    result = online.process_iter()
    
    if result[2]:  # Transcribed text available
        start_time, end_time, text = result
        print(f"[{start_time:.2f}s - {end_time:.2f}s]: {text}")

# Get final result
final_result = online.finish()
```

### WebSocket Client Example

```javascript
const ws = new WebSocket('ws://localhost:43007');

// Send audio configuration
ws.send(JSON.stringify({
    type: 'config',
    source_language: 'en',
    target_language: 'es'
}));

// Stream audio data
ws.send(audioBuffer);

// Receive transcription
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Transcription:', data.text);
    console.log('Translation:', data.translation);
};
```

## 📁 Project Structure

```
Anuvad/
├── whisper_online.py              # Core streaming processor
├── whisper_websocket_server.py    # WebSocket server implementation
├── start_whisper.py               # Enhanced launcher script
├── silero_vad_iterator.py         # Voice Activity Detection
├── index.html                     # Web interface
├── demo.wav                       # Sample audio file
├── chrome_extension/              # Browser extension
│   ├── manifest.json
│   ├── sidepanel.html
│   ├── sidepanel.js
│   ├── service-worker.js
│   ├── offscreen.js
│   └── offscreen.html
├── docs/                          # Documentation site
│   ├── index.html
│   └── styles.css
└── README.md
```

## 🌍 Supported Languages

### Source Languages (Speech Recognition)

All 99 Whisper-supported languages including:
- **European**: English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Turkish, Swedish, Danish, Norwegian, Finnish, Czech, Romanian
- **Asian**: Japanese, Korean, Chinese, Hindi, Arabic, Russian, Thai, Vietnamese, Indonesian, Bengali, Tamil, Telugu
- **Others**: Hebrew, Persian, Urdu, Swahili, and many more

Use `--language auto` for automatic language detection.

### Translation Languages

100+ languages supported via Google Translate integration.

## ⚡ Performance Optimization

- **Model Selection**: Balance accuracy and speed based on your needs
  - `tiny`: Fastest, suitable for testing
  - `small/medium`: Good balance for real-time applications
  - `large-v3`: Best accuracy, recommended for production
  
- **Chunk Size Tuning**: 
  - Smaller (0.1-0.3s): Lower latency, higher CPU usage
  - Larger (0.5-1.0s): Better accuracy, more latency
  
- **Voice Activity Detection**: Reduces processing by 30-50% during silence
- **GPU Acceleration**: 4-5x performance improvement over CPU

## 🎨 Web Interface Features

- **Language Selection**: Choose from 25+ languages for source and target
- **Real-Time Switching**: Change languages during active recording
- **Voice Activity Indicator**: Visual feedback for speech detection
- **Dual Output Panels**: Separate displays for transcription and translation
- **Auto-Scroll**: Automatically follows latest output
- **Responsive Design**: Works on desktop and mobile browsers

## 🔧 Development

### Running Tests

```bash
# Test with sample audio
python whisper_online.py demo.wav --language en

# Test WebSocket server
python start_whisper.py --log-level DEBUG
```

### Integration Points

The system provides multiple integration options:
- WebSocket API for real-time applications
- Python module for embedding in larger systems
- REST API endpoints (coming soon)
- Chrome extension for browser integration

## 📊 Architecture

```
┌─────────────────┐
│  Audio Source   │
│ (Mic/Tab/File)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Audio Processing      │
│  (16kHz, PCM16, Mono)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Voice Activity         │
│  Detection (VAD)        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Whisper ASR Engine     │
│  (Faster-Whisper)       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Translation Engine     │
│  (Google Translate)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Output (Captions +     │
│  Translation)           │
└─────────────────────────┘
```

## 🔒 Privacy & Security

- Audio processing can be performed entirely locally
- No audio data stored permanently
- WebSocket connections use secure protocols
- Translation API calls can be self-hosted if needed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Rakin Mohammed Rafeeq**

- Email: rakinmohammedrafeeq@gmail.com
- Portfolio: [rakinmohammedrafeeq.vercel.app](https://rakinmohammedrafeeq.vercel.app)
- GitHub: [@rakinmohammedrafeeq](https://github.com/rakinmohammedrafeeq)

## 🙏 Acknowledgments

- OpenAI Whisper for the foundational ASR model
- Faster-Whisper team for optimized implementation
- Silero VAD for efficient voice activity detection
- Google Translate for multilingual support

---

**Built with ❤️ for making speech accessible across languages**
