# Anuvad Chrome Extension

A Chrome extension that provides real-time audio translation from browser tabs. Capture audio from any tab (YouTube, podcasts, videos, etc.) and get live transcription and translation using the Anuvad speech processing backend.

## 🌟 Features

- **Real-Time Tab Audio Capture**: Capture audio from any browser tab
- **Live Transcription**: Real-time speech-to-text using Whisper ASR
- **Live Translation**: Instant translation supporting 100+ languages
- **Multilingual Support**: All Whisper-supported languages including English, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Arabic, Russian, Hindi, and many more
- **Side Panel Interface**: Persistent side panel that stays open while browsing
- **Language Switching**: Change languages during recording without interruption
- **Text Accumulation**: Keeps all transcriptions/translations for slow readers
- **Auto-scroll**: Automatically scrolls to show latest text

## 🚀 Quick Start

### Prerequisites
1. **Anuvad Server**: You need the Anuvad WebSocket server running on localhost:43007
2. **Python Environment**: Python 3.8+ with required dependencies installed

### Installation
1. **Start the Server**:
   ```bash
   python start_whisper.py --translate --vac --vad
   ```

2. **Load Extension**:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `chrome_extension` folder

3. **Use Extension**:
   - Click the extension icon → Side panel opens automatically
   - Navigate to any tab with audio content
   - Select source and target languages
   - Click "Start Translation"
   - Watch real-time transcription and translation appear

## 📁 File Structure

```
chrome_extension/
├── manifest.json           # Extension configuration
├── service-worker.js       # Background script, handles tab capture
├── sidepanel.html          # Main UI interface
├── sidepanel.js           # Side panel logic and event handling
├── offscreen.html         # Offscreen document for audio processing
├── offscreen.js           # Audio capture and server communication
├── socket.io.min.js       # Socket.IO client library
├── icons/                 # Extension icons
│   ├── not-recording.png  # Default state icon
│   └── recording.png      # Recording state icon
└── README.md              # This file
```

## 🔧 How It Works

### Architecture
```
Browser Tab Audio → Chrome Extension → WebSocket → Anuvad Server → Processing Pipeline
                                                                    ├── Whisper ASR (Speech-to-Text)
                                                                    ├── Google Translate (Translation)
                                                                    └── Voice Activity Detection
```

### Component Breakdown

#### 1. **Service Worker** (`service-worker.js`)
- Handles extension icon clicks
- Manages tab capture permissions
- Creates offscreen documents for audio processing
- Coordinates between UI and audio processing

#### 2. **Side Panel** (`sidepanel.html` + `sidepanel.js`)
- Main user interface
- Language selection controls
- Real-time display of transcription/translation
- Text accumulation and management
- Start/Stop/Clear controls

#### 3. **Offscreen Document** (`offscreen.html` + `offscreen.js`)
- Captures tab audio using `getUserMedia` with `tabCapture`
- Converts audio to PCM16 format (44.1kHz)
- Connects to localhost:3000 via Socket.IO
- Streams audio data in real-time
- Handles server responses and forwards to UI

#### 4. **WebSocket Communication**
- **Client → Server**: Audio data, language configuration, control commands
- **Server → Client**: Transcription results, translation results, status updates

## 🎯 Key Features Explained

### Real-time Language Switching
- Change source/target languages during active recording
- Server automatically restarts transcription with new language
- No interruption to audio capture
- Visual feedback for language changes

### Text Accumulation System
- **Final text**: Added to accumulated display
- **Partial text**: Shown in italics after accumulated text
- **Persistent**: Text remains visible after stopping translation
- **Clear button**: Users can clear accumulated text when needed
- **Auto-scroll**: Always shows latest text at bottom

### Proper Tab Capture Management
- Explicitly stops all media stream tracks on translation stop
- Removes Chrome's recording indicator immediately
- Prevents audio muting issues
- Clean resource cleanup

### Error Handling & Recovery
- Connection timeout and retry logic
- Graceful handling of server disconnections
- Proper cleanup on errors
- User-friendly error messages

## 🛠️ Technical Details

### Audio Processing
- **Format**: PCM16, 44.1kHz, mono
- **Chunk size**: 4096 samples processed in real-time
- **Streaming**: 100ms audio chunks sent to server
- **Compatibility**: Works with any tab audio source

### Server Communication
- **Protocol**: WebSocket
- **Port**: 43007 (default)
- **Events**: Audio streaming, configuration updates, control commands
- **Responses**: Transcription results, translation output, status updates

### Chrome APIs Used
- `chrome.tabCapture` - Capture tab audio
- `chrome.offscreen` - Background audio processing
- `chrome.sidePanel` - Persistent side panel UI
- `chrome.runtime` - Message passing between components

## 🎨 UI/UX Design

### Color Scheme
- **Background**: Clean white (#FFFFFF)
- **Text**: Dark gray (#282828)
- **Sections**: Light gray (#EAEAEA)
- **Borders**: Subtle gray (#d0d0d0)
- **Success**: Green (#4CAF50)
- **Error**: Red (#f44336)
- **Warning**: Orange (#ff9800)

### Layout
- **Responsive**: Adapts to side panel width
- **Compact**: Efficient use of space
- **Accessible**: High contrast, clear typography
- **Intuitive**: Logical flow and clear controls

## 🔍 Troubleshooting

### Common Issues

1. **"Server connection failed"**
   - Ensure `python start_whisper.py` is running on port 43007
   - Check that all Python dependencies are installed

2. **"No audio detected"**
   - Make sure the tab has audio playing
   - Check Chrome's site permissions for the target website

3. **"Recording indicator stays on"**
   - This was fixed - extension now properly stops all media tracks
   - If issue persists, reload the extension

4. **"Side panel won't open"**
   - Try right-clicking extension icon → "Open Audio Translator"
   - Reload the extension in chrome://extensions/

### Debug Information
- Check browser console for detailed logs
- Extension logs show connection status and audio processing
- Server logs show transcription and translation pipeline

## 🚀 Performance

- **Low latency**: ~100-200ms from speech to transcription
- **Efficient**: Minimal CPU usage, optimized audio processing
- **Scalable**: Handles long recording sessions without memory leaks
- **Reliable**: Robust error handling and recovery mechanisms

## 🔒 Privacy & Security

- **Local processing**: Audio processing happens on your local machine
- **Secure transmission**: Audio sent to localhost server only
- **No storage**: No audio data stored permanently
- **Open source**: Full transparency in data handling

## 📝 Development Notes

### Recent Improvements
- Fixed tab capture release issues
- Added text accumulation for better readability
- Improved language controls layout
- Enhanced error handling and recovery
- Optimized audio processing pipeline
- Added proper cleanup mechanisms

### Code Quality
- Clean, documented code
- Proper error handling
- Resource cleanup
- Performance optimizations
- User experience focus

---

## 🎉 Usage Summary

1. **Start server**: `python start_whisper.py --translate`
2. **Load extension**: Chrome Developer Mode → Load Unpacked
3. **Click extension icon**: Side panel opens automatically
4. **Navigate to audio content**: YouTube, podcasts, etc.
5. **Select languages**: Choose source and target languages
6. **Start translation**: Click "Start Translation"
7. **Watch results**: Real-time transcription and translation
8. **Change languages**: Modify settings during recording if needed
9. **Stop when done**: Click "Stop Translation"
10. **Clear text**: Use "Clear Text" button for fresh start

Perfect for language learning, accessibility, content consumption, and international communication!

---

**Part of the Anuvad project** - Real-time multilingual speech captioning system