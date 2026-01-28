/**
 * ANUVAD — Real-Time Speech Intelligence & Live Translation Client
 * Gen-Z Cyber Glassmorphic Experience
 */

class AnuvadApp {
    constructor() {
        this.socket = null;
        this.audioContext = null;
        this.mediaStream = null;
        this.processorNode = null;
        this.analyserNode = null;
        this.isRecording = false;

        this.transcriptionFinal = "";
        this.translationFinal = "";

        this.initDOMElements();
        this.initServerUrl();
        this.bindEvents();
        this.initEqualizerBars();
    }

    initDOMElements() {
        this.toggleBtn = document.getElementById("toggleBtn");
        this.clearBtn = document.getElementById("clearBtn");
        this.exportBtn = document.getElementById("exportBtn");
        this.swapLangBtn = document.getElementById("swapLangBtn");
        this.sourceLangSelect = document.getElementById("sourceLangSelect");
        this.targetLangSelect = document.getElementById("targetLangSelect");
        this.serverUrlInput = document.getElementById("serverUrl");
        this.connectionBadge = document.getElementById("connectionBadge");
        this.statusText = document.getElementById("statusText");
        this.transcriptBox = document.getElementById("transcriptBox");
        this.translationBox = document.getElementById("translationBox");
        this.alertBox = document.getElementById("alertBox");
        this.originalLangTag = document.getElementById("originalLangTag");
        this.translationLangTag = document.getElementById("translationLangTag");
        this.transcriptWordCount = document.getElementById("transcriptWordCount");
        this.translationWordCount = document.getElementById("translationWordCount");
        this.copyTranscriptBtn = document.getElementById("copyTranscriptBtn");
        this.copyTranslationBtn = document.getElementById("copyTranslationBtn");
        this.visualizerBarsContainer = document.getElementById("visualizerBars");
        this.micVolText = document.getElementById("micVolText");
        this.toastNotification = document.getElementById("toastNotification");
        this.toastMessage = document.getElementById("toastMessage");
        this.chips = document.querySelectorAll(".lang-chip");
    }

    initServerUrl() {
        if (window.location.protocol === "http:" || window.location.protocol === "https:") {
            const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
            this.serverUrlInput.value = `${wsProtocol}//${window.location.host}/ws`;
        } else {
            this.serverUrlInput.value = "ws://127.0.0.1:8000/ws";
        }
    }

    initEqualizerBars() {
        this.eqBars = Array.from(this.visualizerBarsContainer.querySelectorAll(".bar"));
    }

    bindEvents() {
        this.toggleBtn.addEventListener("click", () => this.toggleRecording());
        this.clearBtn.addEventListener("click", () => this.clearCaptions());
        this.exportBtn.addEventListener("click", () => this.exportTranscript());
        this.swapLangBtn.addEventListener("click", () => this.swapLanguages());

        const handleLangChange = () => {
            const src = this.sourceLangSelect.value;
            const target = this.targetLangSelect.value;
            this.updateLanguageTags(src, target);
            this.syncChipActiveState(target);

            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: "setLanguages",
                    sourceLanguage: src,
                    targetLanguage: target
                }));
            }
        };

        this.sourceLangSelect.addEventListener("change", handleLangChange);
        this.targetLangSelect.addEventListener("change", handleLangChange);

        // Quick language chips
        this.chips.forEach((chip) => {
            chip.addEventListener("click", () => {
                const lang = chip.dataset.lang;
                this.targetLangSelect.value = lang;
                handleLangChange();
            });
        });

        // Copy buttons
        this.copyTranscriptBtn.addEventListener("click", () => {
            this.copyToClipboard(this.transcriptionFinal || this.transcriptBox.innerText, "Transcript copied! ✨");
        });

        this.copyTranslationBtn.addEventListener("click", () => {
            this.copyToClipboard(this.translationFinal || this.translationBox.innerText, "Translation copied! 🌍");
        });

        // Initial tag update
        this.updateLanguageTags(this.sourceLangSelect.value, this.targetLangSelect.value);
    }

    syncChipActiveState(targetLang) {
        this.chips.forEach((chip) => {
            if (chip.dataset.lang === targetLang) {
                chip.classList.add("active");
            } else {
                chip.classList.remove("active");
            }
        });
    }

    swapLanguages() {
        const currentSrc = this.sourceLangSelect.value;
        const currentTarget = this.targetLangSelect.value;

        // Auto cannot be a target language
        if (currentSrc === "auto") {
            this.sourceLangSelect.value = currentTarget;
            this.targetLangSelect.value = "en";
        } else {
            this.sourceLangSelect.value = currentTarget;
            this.targetLangSelect.value = currentSrc;
        }

        const newSrc = this.sourceLangSelect.value;
        const newTarget = this.targetLangSelect.value;
        this.updateLanguageTags(newSrc, newTarget);
        this.syncChipActiveState(newTarget);

        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: "setLanguages",
                sourceLanguage: newSrc,
                targetLanguage: newTarget
            }));
        }

        this.showToast(`Swapped: ${newSrc.toUpperCase()} ➔ ${newTarget.toUpperCase()} 🔄`);
    }

    updateLanguageTags(src, target) {
        const srcText = this.sourceLangSelect.options[this.sourceLangSelect.selectedIndex]?.text || src;
        const targetText = this.targetLangSelect.options[this.targetLangSelect.selectedIndex]?.text || target;
        this.originalLangTag.textContent = srcText;
        this.translationLangTag.textContent = targetText;
    }

    showAlert(message) {
        this.alertBox.textContent = message;
        this.alertBox.style.display = "block";
    }

    hideAlert() {
        this.alertBox.style.display = "none";
        this.alertBox.textContent = "";
    }

    showToast(message) {
        this.toastMessage.textContent = message;
        this.toastNotification.classList.add("show");
        clearTimeout(this.toastTimeout);
        this.toastTimeout = setTimeout(() => {
            this.toastNotification.classList.remove("show");
        }, 2200);
    }

    async copyToClipboard(text, successMsg) {
        if (!text || text.includes("Waiting for speech") || text.includes("Translations will appear")) {
            this.showToast("Nothing to copy yet! 🎙️");
            return;
        }
        try {
            await navigator.clipboard.writeText(text.trim());
            this.showToast(successMsg);
        } catch (err) {
            console.error("Clipboard copy error:", err);
            this.showToast("Copy failed");
        }
    }

    exportTranscript() {
        if (!this.transcriptionFinal && !this.translationFinal) {
            this.showToast("No transcript available to export! 📄");
            return;
        }

        const now = new Date();
        const timestamp = now.toISOString().replace(/[:.]/g, "-");
        const srcLang = this.sourceLangSelect.value.toUpperCase();
        const tgtLang = this.targetLangSelect.value.toUpperCase();

        const fileContent = [
            `==================================================`,
            `ANUVAD SPEECH TRANSCRIPTION & TRANSLATION SESSION`,
            `Recorded: ${now.toLocaleString()}`,
            `Source Language: ${srcLang} | Target Language: ${tgtLang}`,
            `==================================================\n`,
            `[ORIGINAL SPEECH (${srcLang})]`,
            this.transcriptionFinal.trim() || "(No speech recorded)",
            `\n--------------------------------------------------\n`,
            `[TRANSLATION (${tgtLang})]`,
            this.translationFinal.trim() || "(No translation recorded)",
            `\n==================================================`,
        ].join("\n");

        const blob = new Blob([fileContent], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `anuvad_session_${timestamp}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast("Transcript exported as .txt! 📥");
    }

    setConnectionStatus(status, text) {
        this.connectionBadge.className = `connection-badge ${status}`;
        this.statusText.textContent = text;
    }

    async toggleRecording() {
        if (this.isRecording) {
            await this.stopRecording();
        } else {
            await this.startRecording();
        }
    }

    async startRecording() {
        this.hideAlert();
        this.setConnectionStatus("", "Connecting...");

        try {
            // 1. Request microphone access
            this.mediaStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
        } catch (err) {
            console.error("Microphone access error:", err);
            let msg = "Microphone access failed.";
            if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
                msg = "Microphone permission denied. Allow mic access in browser address bar.";
            } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
                msg = "No microphone found on system. Please connect an audio input device.";
            }
            this.showAlert(msg);
            this.setConnectionStatus("error", "Mic Error");
            return;
        }

        // 2. Connect WebSocket
        const wsUrl = this.serverUrlInput.value.trim();
        try {
            this.socket = new WebSocket(wsUrl);
            this.socket.binaryType = "arraybuffer";
        } catch (err) {
            this.showAlert(`Invalid WebSocket URL: ${wsUrl}`);
            this.setConnectionStatus("error", "URL Error");
            this.cleanupAudio();
            return;
        }

        this.socket.onopen = () => {
            this.setConnectionStatus("recording", "Listening Live");
            this.toggleBtn.innerHTML = `<span class="btn-icon">⏹</span> <span class="btn-text">Stop Session</span>`;
            this.toggleBtn.className = "btn btn-hero btn-recording";
            this.isRecording = true;

            // Configure initial languages and start session
            this.socket.send(JSON.stringify({
                type: "setLanguages",
                sourceLanguage: this.sourceLangSelect.value,
                targetLanguage: this.targetLangSelect.value
            }));
            this.socket.send(JSON.stringify({ type: "start" }));

            // Setup audio capture stream
            this.setupAudioProcessing(this.mediaStream);
            this.visualizerBarsContainer.classList.add("active");
        };

        this.socket.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                this.handleServerMessage(msg);
            } catch (err) {
                console.error("Error parsing message:", err);
            }
        };

        this.socket.onerror = (event) => {
            console.error("WebSocket error:", event);
            this.showAlert("Failed to connect to Anuvad backend. Ensure server is running on " + wsUrl);
            this.setConnectionStatus("error", "Offline");
        };

        this.socket.onclose = () => {
            if (this.isRecording) {
                this.stopRecording();
                this.setConnectionStatus("", "Disconnected");
            }
        };
    }

    setupAudioProcessing(stream) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: 16000
        });

        const sourceNode = this.audioContext.createMediaStreamSource(stream);

        // Analyser for visual volume meter & equalizers
        this.analyserNode = this.audioContext.createAnalyser();
        this.analyserNode.fftSize = 64;
        sourceNode.connect(this.analyserNode);
        this.startMeterLoop();

        // Audio processor node (1024 samples ~ 64ms for ultra low-latency streaming)
        this.processorNode = this.audioContext.createScriptProcessor(1024, 1, 1);

        this.processorNode.onaudioprocess = (e) => {
            if (!this.isRecording || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
                return;
            }

            const inputData = e.inputBuffer.getChannelData(0);
            const pcm16 = this.float32ToPCM16(inputData);
            this.socket.send(pcm16);
        };

        sourceNode.connect(this.processorNode);
        this.processorNode.connect(this.audioContext.destination);
    }

    startMeterLoop() {
        const bufferLength = this.analyserNode.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const updateMeter = () => {
            if (!this.isRecording || !this.analyserNode) {
                this.eqBars.forEach((bar) => (bar.style.height = "4px"));
                this.micVolText.textContent = "0%";
                return;
            }

            this.analyserNode.getByteFrequencyData(dataArray);

            let sum = 0;
            const barCount = this.eqBars.length;
            const step = Math.floor(bufferLength / barCount) || 1;

            for (let i = 0; i < barCount; i++) {
                const val = dataArray[i * step] || 0;
                sum += val;
                const heightPx = Math.max(4, Math.round((val / 255) * 24));
                this.eqBars[i].style.height = `${heightPx}px`;
            }

            const avg = sum / barCount;
            const percentage = Math.min(100, Math.round((avg / 128) * 100));
            this.micVolText.textContent = `${percentage}%`;

            requestAnimationFrame(updateMeter);
        };
        requestAnimationFrame(updateMeter);
    }

    float32ToPCM16(float32Array) {
        const pcm16 = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            const s = Math.max(-1, Math.min(1, float32Array[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return pcm16.buffer;
    }

    async stopRecording() {
        this.isRecording = false;
        this.toggleBtn.innerHTML = `<span class="btn-icon">🎙️</span> <span class="btn-text">Start Listening</span>`;
        this.toggleBtn.className = "btn btn-hero";
        this.setConnectionStatus("", "Ready");
        this.visualizerBarsContainer.classList.remove("active");

        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ type: "stop" }));
            setTimeout(() => {
                if (this.socket) {
                    this.socket.close();
                    this.socket = null;
                }
            }, 300);
        }

        this.cleanupAudio();
    }

    cleanupAudio() {
        if (this.processorNode) {
            this.processorNode.disconnect();
            this.processorNode = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach((track) => track.stop());
            this.mediaStream = null;
        }
        this.eqBars.forEach((bar) => (bar.style.height = "4px"));
        this.micVolText.textContent = "0%";
    }

    handleServerMessage(msg) {
        switch (msg.type) {
            case "transcription":
                this.renderTranscription(msg.text, msg.isFinal);
                break;

            case "translation":
                this.renderTranslation(msg.text, msg.isFinal !== false);
                break;

            case "status":
                console.log("Server status:", msg.message);
                break;

            case "error":
                console.error("Server error:", msg.message);
                this.showAlert(msg.message);
                break;

            case "languageChangeRestart":
            case "targetLanguageChanged":
                console.log("Language updated:", msg.message);
                break;
        }
    }

    renderTranscription(text, isFinal) {
        if (!text || !text.trim()) return;

        if (isFinal) {
            this.transcriptionFinal += (this.transcriptionFinal ? " " : "") + text.trim();
            this.transcriptBox.innerHTML = `<span class="final-text">${this.escapeHTML(this.transcriptionFinal)}</span>`;
            this.updateWordCount(this.transcriptionFinal, this.transcriptWordCount);
        } else {
            const currentFinal = this.transcriptionFinal ? `<span class="final-text">${this.escapeHTML(this.transcriptionFinal)} </span>` : "";
            const currentPartial = `<span class="partial-text">${this.escapeHTML(text.trim())}</span>`;
            this.transcriptBox.innerHTML = currentFinal + currentPartial;
        }

        this.transcriptBox.scrollTop = this.transcriptBox.scrollHeight;
    }

    renderTranslation(text, isFinal = true) {
        if (!text || !text.trim()) return;

        if (isFinal) {
            this.translationFinal += (this.translationFinal ? " " : "") + text.trim();
            this.translationBox.innerHTML = `<span class="final-text">${this.escapeHTML(this.translationFinal)}</span>`;
            this.updateWordCount(this.translationFinal, this.translationWordCount);
        } else {
            const currentFinal = this.translationFinal ? `<span class="final-text">${this.escapeHTML(this.translationFinal)} </span>` : "";
            const currentPartial = `<span class="partial-text">${this.escapeHTML(text.trim())}</span>`;
            this.translationBox.innerHTML = currentFinal + currentPartial;
        }

        this.translationBox.scrollTop = this.translationBox.scrollHeight;
    }

    updateWordCount(text, element) {
        const words = text.trim().split(/\s+/).filter(Boolean);
        element.textContent = `${words.length} word${words.length === 1 ? "" : "s"}`;
    }

    clearCaptions() {
        this.transcriptionFinal = "";
        this.translationFinal = "";
        this.transcriptWordCount.textContent = "0 words";
        this.translationWordCount.textContent = "0 words";

        this.transcriptBox.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🎧</div>
                <h3>Waiting for speech...</h3>
                <p>Click "Start Listening" and speak into your microphone. Words stream in real-time.</p>
            </div>
        `;

        this.translationBox.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">✨</div>
                <h3>Translations will appear here</h3>
                <p>Locked speech segments are instantly translated into your target language.</p>
            </div>
        `;

        this.showToast("Captions cleared! 🧹");
    }

    escapeHTML(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    window.anuvadApp = new AnuvadApp();
});
