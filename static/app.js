document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const clearFileBtn = document.getElementById('clear-file');
    const transcribeBtn = document.getElementById('transcribe-btn');
    const enableDiarization = document.getElementById('enable-diarization');
    const uploadSection = document.getElementById('upload-section');
    const progressSection = document.getElementById('progress-section');
    const progressFill = document.getElementById('progress-fill');
    const progressStatus = document.getElementById('progress-status');
    const resultsSection = document.getElementById('results-section');
    const speakersSection = document.getElementById('speakers-section');
    const speakersList = document.getElementById('speakers-list');
    const updateSpeakersBtn = document.getElementById('update-speakers-btn');
    const transcriptContent = document.getElementById('transcript-content');
    const detectedLanguage = document.getElementById('detected-language');
    const downloadTxt = document.getElementById('download-txt');
    const downloadSrt = document.getElementById('download-srt');
    const downloadJson = document.getElementById('download-json');
    const errorToast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');

    let selectedFile = null;
    let currentJsonFile = null;
    let detectedSpeakers = [];
    let speakerClips = {};
    let currentAudio = null;

    // Drag and drop handlers
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    clearFileBtn.addEventListener('click', () => {
        clearFile();
    });

    transcribeBtn.addEventListener('click', () => {
        if (selectedFile) {
            startTranscription();
        }
    });

    updateSpeakersBtn.addEventListener('click', () => {
        updateSpeakerNames();
    });

    function handleFileSelect(file) {
        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        dropZone.classList.add('hidden');
        fileInfo.classList.remove('hidden');
        transcribeBtn.disabled = false;
        resultsSection.classList.add('hidden');
    }

    function clearFile() {
        selectedFile = null;
        fileInput.value = '';
        dropZone.classList.remove('hidden');
        fileInfo.classList.add('hidden');
        transcribeBtn.disabled = true;
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorToast.classList.remove('hidden');
        errorToast.classList.remove('warning');
        errorToast.classList.remove('success');
        setTimeout(() => {
            errorToast.classList.add('hidden');
        }, 5000);
    }

    function showWarning(message) {
        errorMessage.textContent = message;
        errorToast.classList.remove('hidden');
        errorToast.classList.add('warning');
        errorToast.classList.remove('success');
        setTimeout(() => {
            errorToast.classList.add('hidden');
        }, 8000);
    }

    function showSuccess(message) {
        errorMessage.textContent = message;
        errorToast.classList.remove('hidden');
        errorToast.classList.remove('warning');
        errorToast.classList.add('success');
        setTimeout(() => {
            errorToast.classList.add('hidden');
        }, 5000);
    }

    function setProgress(percent, status) {
        progressFill.style.width = percent + '%';
        progressStatus.textContent = status;
    }

    async function startTranscription() {
        const btnText = transcribeBtn.querySelector('.btn-text');
        const btnLoading = transcribeBtn.querySelector('.btn-loading');

        // Show loading state
        btnText.classList.add('hidden');
        btnLoading.classList.remove('hidden');
        transcribeBtn.disabled = true;

        // Show progress section
        progressSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        setProgress(10, 'Uploading file...');

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('diarization', enableDiarization.checked);

        try {
            setProgress(20, 'Processing audio...');

            // Simulate progress updates during processing
            const progressInterval = setInterval(() => {
                const currentWidth = parseFloat(progressFill.style.width) || 20;
                if (currentWidth < 90) {
                    setProgress(currentWidth + Math.random() * 5, 'Transcribing...');
                }
            }, 2000);

            const response = await fetch('/api/transcribe', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Transcription failed');
            }

            setProgress(100, 'Complete!');

            const result = await response.json();
            displayResults(result);

        } catch (error) {
            showError(error.message);
            progressSection.classList.add('hidden');
        } finally {
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
            transcribeBtn.disabled = false;
        }
    }

    function displayResults(result) {
        setTimeout(() => {
            progressSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
        }, 500);

        // Show diarization warning if present
        if (result.diarization_warning) {
            showWarning('Diarization skipped: ' + result.diarization_warning);
        }

        // Set language
        detectedLanguage.textContent = result.language || 'Unknown';

        // Handle speakers
        detectedSpeakers = result.speakers || [];
        speakerClips = result.speaker_clips || {};
        currentJsonFile = result.files.json;

        if (detectedSpeakers.length > 0) {
            speakersSection.classList.remove('hidden');
            speakersList.innerHTML = '';

            detectedSpeakers.forEach(speaker => {
                const row = document.createElement('div');
                row.className = 'speaker-row';
                const clipFile = speakerClips[speaker];
                const playButton = clipFile
                    ? `<button class="btn-play" data-clip="${clipFile}" title="Play sample">
                         <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                           <polygon points="5 3 19 12 5 21 5 3"></polygon>
                         </svg>
                       </button>`
                    : '';
                row.innerHTML = `
                    <span class="speaker-id">${speaker}</span>
                    ${playButton}
                    <input type="text" class="speaker-input"
                           data-speaker="${speaker}"
                           placeholder="Enter name...">
                `;
                speakersList.appendChild(row);
            });

            // Add click handlers for play buttons
            speakersList.querySelectorAll('.btn-play').forEach(btn => {
                btn.addEventListener('click', () => {
                    playClip(btn.dataset.clip, btn);
                });
            });
        } else {
            speakersSection.classList.add('hidden');
        }

        // Display transcript
        renderTranscript(result.segments);

        // Set download links
        downloadTxt.href = `/api/download/${result.files.txt}`;
        downloadSrt.href = `/api/download/${result.files.srt}`;
        downloadJson.href = `/api/download/${result.files.json}`;
    }

    function renderTranscript(segments) {
        transcriptContent.innerHTML = '';

        segments.forEach(segment => {
            const div = document.createElement('div');
            div.className = 'segment';

            const speaker = segment.speaker_name || segment.speaker || '';
            const time = formatTime(segment.start);
            const text = segment.text || '';

            let html = '';
            if (speaker) {
                html += `<span class="segment-speaker">[${speaker}]</span>`;
            }
            html += `<span class="segment-time">${time}</span> `;
            html += text;

            div.innerHTML = html;
            transcriptContent.appendChild(div);
        });
    }

    function formatTime(seconds) {
        if (seconds === undefined || seconds === null) return '';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    function playClip(clipFile, button) {
        // Stop any currently playing audio
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
            // Reset all play buttons
            document.querySelectorAll('.btn-play.playing').forEach(btn => {
                btn.classList.remove('playing');
            });
        }

        // Create and play new audio
        currentAudio = new Audio(`/api/clips/${clipFile}`);
        button.classList.add('playing');

        currentAudio.addEventListener('ended', () => {
            button.classList.remove('playing');
            currentAudio = null;
        });

        currentAudio.addEventListener('error', () => {
            button.classList.remove('playing');
            showError('Failed to play audio clip');
            currentAudio = null;
        });

        currentAudio.play().catch(err => {
            button.classList.remove('playing');
            showError('Failed to play audio clip');
            currentAudio = null;
        });
    }

    async function updateSpeakerNames() {
        const speakerNames = {};
        const inputs = speakersList.querySelectorAll('.speaker-input');

        inputs.forEach(input => {
            const speaker = input.dataset.speaker;
            const name = input.value.trim();
            if (name) {
                speakerNames[speaker] = name;
            }
        });

        // Check for merged speakers (same name)
        const nameToSpeakers = {};
        for (const [speaker, name] of Object.entries(speakerNames)) {
            if (!nameToSpeakers[name]) {
                nameToSpeakers[name] = [];
            }
            nameToSpeakers[name].push(speaker);
        }

        const mergedGroups = Object.entries(nameToSpeakers)
            .filter(([name, speakers]) => speakers.length > 1)
            .map(([name, speakers]) => ({ name, speakers }));

        updateSpeakersBtn.disabled = true;
        updateSpeakersBtn.textContent = 'Updating...';

        try {
            const response = await fetch('/api/update-speakers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    json_file: currentJsonFile,
                    speaker_names: speakerNames
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Update failed');
            }

            const result = await response.json();
            renderTranscript(result.segments);

            // Show merge notification if speakers were merged
            if (mergedGroups.length > 0) {
                const mergeMessages = mergedGroups.map(g =>
                    `${g.speakers.join(' + ')} merged as "${g.name}"`
                ).join('; ');
                showSuccess(`Speakers merged: ${mergeMessages}`);

                // Highlight merged inputs
                inputs.forEach(input => {
                    const speaker = input.dataset.speaker;
                    const name = input.value.trim();
                    const isMerged = mergedGroups.some(g =>
                        g.speakers.includes(speaker)
                    );
                    if (isMerged) {
                        input.classList.add('merged');
                    } else {
                        input.classList.remove('merged');
                    }
                });
            }

        } catch (error) {
            showError(error.message);
        } finally {
            updateSpeakersBtn.disabled = false;
            updateSpeakersBtn.textContent = 'Update Names';
        }
    }
});
