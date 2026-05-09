let selectedFile = null;
let uploadedFilename = null;
let currentVideoId = null;
let detectionPollingInterval = null;
let originalVideoUrl = null;
let isVideoStreamActive = false;
let allDetections = [];

function cleanupVideoState() {
    if (currentVideoId) {
        try {
            fetch('/api/video/stop/' + currentVideoId, { method: 'POST' }).catch(() => {});
        } catch (e) {}
        currentVideoId = null;
    }
    if (detectionPollingInterval) {
        clearInterval(detectionPollingInterval);
        detectionPollingInterval = null;
    }
    isVideoStreamActive = false;
}

function stopCurrentVideoStream() {
    cleanupVideoState();
    const streamImg = document.getElementById('streamImg');
    if (streamImg) {
        streamImg.src = '';
        streamImg.classList.add('d-none');
    }
    isVideoStreamActive = false;
}

document.getElementById('fileInput').addEventListener('change', async function(e) {
    selectedFile = e.target.files[0];
    const previewImg = document.getElementById('previewImg');
    const previewVideo = document.getElementById('previewVideo');
    const streamImg = document.getElementById('streamImg');
    const cameraPlaceholder = document.getElementById('cameraPlaceholder');

    stopCurrentVideoStream();

    uploadedFilename = null;
    allDetections = [];

    if (previewImg) {
        previewImg.classList.add('d-none');
        previewImg.src = '';
    }
    if (previewVideo) {
        previewVideo.classList.add('d-none');
        previewVideo.src = '';
        previewVideo.pause();
    }
    if (streamImg) {
        streamImg.classList.add('d-none');
        streamImg.src = '';
    }

    updateDetectionsDisplay();

    if (selectedFile) {
        // 有文件时隐藏占位符
        if (cameraPlaceholder) {
            cameraPlaceholder.classList.add('d-none');
        }

        console.log('Selected file:', selectedFile.name, 'type:', selectedFile.type);

        const isImage = selectedFile.type.startsWith('image/');

        if (isImage) {
            const url = URL.createObjectURL(selectedFile);
            if (previewImg) {
                previewImg.src = url;
                previewImg.classList.remove('d-none');
            }
            if (previewVideo) {
                previewVideo.classList.add('d-none');
            }
        } else {
            const blobUrl = URL.createObjectURL(selectedFile);
            console.log('Blob URL:', blobUrl);

            if (previewVideo) {
                previewVideo.src = blobUrl;
                previewVideo.classList.remove('d-none');
                previewVideo.onloadedmetadata = function() {
                    console.log('Video metadata loaded, duration:', previewVideo.duration, 'seconds');
                };
                previewVideo.onerror = function(e) {
                    console.error('Video load error:', e);
                };
                previewVideo.oncanplay = function() {
                    console.log('Video is ready to play');
                };
                previewVideo.load();
            }
            if (previewImg) {
                previewImg.classList.add('d-none');
            }
            if (streamImg) {
                streamImg.classList.add('d-none');
            }
        }

        updateDetectionsDisplay();
    } else {
        // 没有文件时显示占位符
        if (cameraPlaceholder) {
            cameraPlaceholder.classList.remove('d-none');
        }
    }
});

document.getElementById('detectBtn').addEventListener('click', async function() {
    if (!selectedFile) {
        alert('Please select an image or video first');
        return;
    }

    const loading = document.getElementById('loading');
    const detectBtn = document.getElementById('detectBtn');

    stopCurrentVideoStream();

    if (loading) loading.classList.remove('d-none');
    if (detectBtn) detectBtn.disabled = true;

    if (!uploadedFilename) {
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);
            const uploadResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            if (!uploadResponse.ok) throw new Error('Upload failed');
            const uploadResult = await uploadResponse.json();
            uploadedFilename = uploadResult.filename;
            console.log('File uploaded:', uploadedFilename);
        } catch (error) {
            console.error('Upload error:', error);
            alert('File upload failed');
            if (loading) loading.classList.add('d-none');
            if (detectBtn) detectBtn.disabled = false;
            return;
        }
    }

    const formData = new FormData();
    formData.append('filename', uploadedFilename);

    try {
        const response = await fetch('/api/detect', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(`HTTP ${response.status}: ${text}`);
        }

        const result = await response.json();

        if (result.success) {
            if (result.type === 'video') {
                await startVideoStream(result);
            } else {
                displayResults(result);
            }
        } else {
            alert('Detection failed: ' + result.error);
        }
    } catch (error) {
        console.error('Detection request failed:', error);
        alert('Request failed: ' + error.message);
    } finally {
        if (loading) loading.classList.add('d-none');
        if (detectBtn) detectBtn.disabled = false;
    }
});

async function startVideoStream(data) {
    const streamImg = document.getElementById('streamImg');
    const previewVideo = document.getElementById('previewVideo');
    const detectInterval = document.getElementById('detectInterval').value;

    currentVideoId = 'video_' + Date.now();

    try {
        const response = await fetch('/api/video/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: currentVideoId,
                filename: data.original,
                detect_interval: parseInt(detectInterval)
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
            if (previewVideo) previewVideo.classList.add('d-none');
            if (previewVideo) previewVideo.pause();
            if (streamImg) {
                streamImg.classList.remove('d-none');
                streamImg.src = '/api/video/stream/' + currentVideoId;
            }
            isVideoStreamActive = true;

            startDetectionPolling(currentVideoId);
        } else {
            alert('Video stream start failed: ' + result.error);
            displayResults(data);
        }
    } catch (error) {
        console.error('Video stream request failed:', error);
        alert('Video stream request failed: ' + error.message);
        displayResults(data);
    }
}

function startDetectionPolling(videoId) {
    if (detectionPollingInterval) {
        clearInterval(detectionPollingInterval);
    }

    detectionPollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/video/frame/' + videoId);
            if (!response.ok) {
                console.error('Failed to get detection results: HTTP', response.status);
                return;
            }
            const result = await response.json();
            if (result.success && result.detections.length > 0) {
                addDetectionsToHistory(result.detections, result.frame);
                updateDetectionsDisplay();
            }
        } catch (error) {
            console.error('Failed to get detection results:', error);
        }
    }, 500);
}

function addDetectionsToHistory(newDetections, frameFilename) {
    newDetections.forEach(det => {
        allDetections.unshift({
            ...det,
            timestamp: new Date().toLocaleTimeString(),
            frame: frameFilename
        });
    });
}

function updateDetectionsDisplay() {
    const detectionsContainer = document.getElementById('detectionsContainer');
    const framesContainer = document.getElementById('framesContainer');
    const historySelect = document.getElementById('historySelect');

    if (allDetections.length === 0) {
        if (detectionsContainer) {
            detectionsContainer.innerHTML = '<p class="text-muted text-center">No detection results</p>';
        }
        if (framesContainer) {
            framesContainer.innerHTML = '<div class="carousel-item active"><p class="text-muted text-center">No detection results</p></div>';
        }
        if (historySelect) {
            historySelect.innerHTML = '<option value="">-- No history --</option>';
        }
        return;
    }

    const displayDetections = allDetections.slice(0, 5);

    let framesHtml = '';
    displayDetections.forEach((det, idx) => {
        const isActive = idx === 0 ? 'active' : '';
        framesHtml += `
            <div class="carousel-item ${isActive}">
                <div class="text-center">
                    ${det.frame ? `<img src="/uploads/${det.frame}" class="img-fluid" style="max-height: 500px;" alt="Detection frame">` : '<p>No frame image</p>'}
                    <div class="mt-2">
                        <span class="badge bg-primary">#${idx + 1} - Confidence: ${(det.confidence * 100).toFixed(2)}%</span>
                        <span class="badge bg-info">Position: [${det.bbox.join(', ')}]</span>
                        <span class="badge bg-secondary">${det.timestamp}</span>
                    </div>
                </div>
            </div>
        `;
    });
    if (framesContainer) {
        framesContainer.innerHTML = framesHtml;
    }

    let detectionsHtml = '<div class="list-group">';
    displayDetections.forEach((det, idx) => {
        const isLatest = idx === 0 ? 'border-primary' : '';
        detectionsHtml += `
            <div class="list-group-item ${isLatest}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>#${idx + 1}${idx === 0 ? ' (Latest)' : ''}</strong>
                        <div class="text-muted small">Position: [${det.bbox.join(', ')}]</div>
                        <div class="text-primary">Confidence: ${(det.confidence * 100).toFixed(2)}%</div>
                        <div class="text-info small">Time: ${det.timestamp}</div>
                    </div>
                    ${det.crop ? `<img src="/crops/${det.crop}" class="detection-crop" alt="Detected object" style="width: 80px; height: 80px; object-fit: cover;">` : ''}
                </div>
            </div>
        `;
    });
    detectionsHtml += '</div>';
    if (detectionsContainer) {
        detectionsContainer.innerHTML = detectionsHtml;
    }

    if (historySelect) {
        historySelect.innerHTML = '<option value="">-- Select history --</option>';
        allDetections.forEach((det, idx) => {
            const option = document.createElement('option');
            option.value = idx;
            option.textContent = `#${idx + 1} - ${(det.confidence * 100).toFixed(0)}% - ${det.timestamp}`;
            historySelect.appendChild(option);
        });
    }
}

function showHistoryDetail(idx) {
    if (idx === '' || idx === null) return;

    const det = allDetections[parseInt(idx)];
    if (!det) return;

    const modalElement = document.getElementById('historyModal');
    if (!modalElement) return;

    const modal = new bootstrap.Modal(modalElement);

    const modalFrameImg = document.getElementById('modalFrameImg');
    const modalDetectionInfo = document.getElementById('modalDetectionInfo');

    if (modalFrameImg) {
        modalFrameImg.src = det.frame ? `/uploads/${det.frame}` : '';
    }
    if (modalDetectionInfo) {
        modalDetectionInfo.innerHTML = `
            <div class="text-start">
                <p><strong>ID:</strong> #${parseInt(idx) + 1}</p>
                <p><strong>Position:</strong> [${det.bbox.join(', ')}]</p>
                <p><strong>Confidence:</strong> ${(det.confidence * 100).toFixed(2)}%</p>
                <p><strong>Detection Time:</strong> ${det.timestamp}</p>
                ${det.crop ? `<p><strong>Cropped Image:</strong></p><img src="/crops/${det.crop}" class="img-thumbnail" style="max-width: 200px;">` : ''}
            </div>
        `;
    }

    modal.show();
}

function displayResults(result) {
    // 不隐藏原始图片/视频
    const previewImg = document.getElementById('previewImg');
    const previewVideo = document.getElementById('previewVideo');
    const streamImg = document.getElementById('streamImg');

    stopCurrentVideoStream();

    if (streamImg) {
        streamImg.classList.add('d-none');
        streamImg.src = '';
    }

    if (result.type === 'image' || result.type === 'video') {
        result.detections.forEach(det => {
            allDetections.unshift({
                ...det,
                timestamp: new Date().toLocaleTimeString(),
                frame: result.result
            });
        });

        updateDetectionsDisplay();
    }
}

document.getElementById('switchModelBtn').addEventListener('click', async function() {
    const modelSelect = document.getElementById('modelSelect');
    const modelName = modelSelect.value;

    try {
        const response = await fetch('/api/switch_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ model_name: modelName })
        });

        const result = await response.json();
        if (result.success) {
            alert('Model switched successfully: ' + modelName);
        } else {
            alert('Model switch failed: ' + result.error);
        }
    } catch (error) {
        console.error('Model switch failed:', error);
        alert('Model switch request failed');
    }
});
