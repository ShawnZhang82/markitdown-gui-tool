document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const actions = document.getElementById('actions');
    const convertBtn = document.getElementById('convertBtn');
    const clearBtn = document.getElementById('clearBtn');
    const results = document.getElementById('results');

    let files = [];
    let resultsData = [];

    // Configure marked
    marked.setOptions({
        gfm: true,
        breaks: true,
        headerIds: true,
        mangle: false,
        sanitize: false,
    });

    // Drag & Drop
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
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(fileList) {
        for (const file of fileList) {
            if (!files.some(f => f.name === file.name && f.size === file.size)) {
                files.push(file);
            }
        }
        renderFileList();
        updateActions();
    }

    function renderFileList() {
        fileList.innerHTML = '';
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const item = document.createElement('div');
            item.className = 'file-item';
            item.innerHTML = `
                <div class="file-icon">${getFileIcon(file.name)}</div>
                <div class="file-info">
                    <div class="file-name">${escapeHtml(file.name)}</div>
                    <div class="file-size">${formatSize(file.size)}</div>
                </div>
                <div class="file-status">
                    <span class="status-badge status-pending" id="status-${i}">待转换</span>
                    <button class="file-remove" data-index="${i}" title="移除">&times;</button>
                </div>
            `;
            fileList.appendChild(item);
        }

        document.querySelectorAll('.file-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.target.dataset.index);
                files.splice(idx, 1);
                renderFileList();
                updateActions();
            });
        });
    }

    function updateActions() {
        actions.style.display = files.length > 0 ? 'flex' : 'none';
    }

    function updateStatus(index, status, text) {
        const badge = document.getElementById(`status-${index}`);
        if (badge) {
            badge.className = `status-badge status-${status}`;
            badge.textContent = text;
        }
    }

    // Convert
    convertBtn.addEventListener('click', async () => {
        if (files.length === 0) return;

        convertBtn.disabled = true;
        convertBtn.textContent = '转换中...';
        resultsData = [];
        results.innerHTML = '';
        results.classList.remove('has-content');

        if (files.length === 1) {
            await convertSingle(files[0], 0);
        } else {
            await convertBatch();
        }

        convertBtn.disabled = false;
        convertBtn.textContent = '开始转换';
    });

    async function convertSingle(file, index) {
        updateStatus(index, 'converting', '转换中');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/convert', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || '转换失败');
            }

            const data = await res.json();
            resultsData.push({ ...data, success: true });
            updateStatus(index, 'success', '成功');
            renderResults();
            showToast('转换成功', 'success');
        } catch (e) {
            resultsData.push({
                filename: file.name,
                success: false,
                error: e.message,
            });
            updateStatus(index, 'error', '失败');
            renderResults();
            showToast(e.message, 'error');
        }
    }

    async function convertBatch() {
        // Mark all as converting
        for (let i = 0; i < files.length; i++) {
            updateStatus(i, 'converting', '转换中');
        }

        const formData = new FormData();
        files.forEach(f => formData.append('files', f));

        try {
            const res = await fetch('/api/convert-batch', {
                method: 'POST',
                body: formData,
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || '批量转换失败');
            }

            const data = await res.json();
            resultsData = data.results;

            for (let i = 0; i < resultsData.length; i++) {
                const r = resultsData[i];
                updateStatus(i, r.success ? 'success' : 'error', r.success ? '成功' : '失败');
            }

            renderResults();
            const successCount = resultsData.filter(r => r.success).length;
            showToast(`转换完成: ${successCount}/${resultsData.length} 成功`, successCount === resultsData.length ? 'success' : 'error');
        } catch (e) {
            for (let i = 0; i < files.length; i++) {
                updateStatus(i, 'error', '失败');
            }
            resultsData = files.map(f => ({
                filename: f.name,
                success: false,
                error: e.message,
            }));
            renderResults();
            showToast(e.message, 'error');
        }
    }

    function renderResults() {
        if (resultsData.length === 0) {
            results.classList.remove('has-content');
            return;
        }

        const successCount = resultsData.filter(r => r.success).length;
        const hasErrors = resultsData.some(r => !r.success);

        let html = `
            <div class="results-header">
                <h2>转换结果 (${successCount}/${resultsData.length})</h2>
                <div class="results-actions">
                    ${successCount > 1 ? `<button class="btn btn-secondary btn-small" id="downloadZipBtn">打包下载 ZIP</button>` : ''}
                </div>
            </div>
        `;

        for (const item of resultsData) {
            html += renderResultItem(item);
        }

        results.innerHTML = html;
        results.classList.add('has-content');

        // Highlight code blocks
        results.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });

        // Attach download handlers
        results.querySelectorAll('.download-single').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filename = e.target.dataset.filename;
                const markdown = e.target.dataset.markdown;
                downloadSingle(filename, markdown);
            });
        });

        results.querySelectorAll('.copy-md').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const markdown = e.target.dataset.markdown;
                navigator.clipboard.writeText(markdown).then(() => {
                    showToast('已复制到剪贴板', 'success');
                });
            });
        });

        const zipBtn = document.getElementById('downloadZipBtn');
        if (zipBtn) {
            zipBtn.addEventListener('click', downloadZip);
        }
    }

    function renderResultItem(item) {
        if (!item.success) {
            return `
                <div class="result-item">
                    <div class="result-header">
                        <span class="result-title">${escapeHtml(item.filename)}</span>
                    </div>
                    <div class="result-error">${escapeHtml(item.error)}</div>
                </div>
            `;
        }

        const previewId = 'preview-' + Math.random().toString(36).substr(2, 9);
        const rawPreview = marked.parse(item.markdown || '');

        return `
            <div class="result-item">
                <div class="result-header">
                    <span class="result-title">${escapeHtml(item.filename)}</span>
                    <div class="result-actions">
                        <button class="btn-link copy-md" data-markdown="${escapeHtmlAttr(item.markdown || '')}">复制</button>
                        <button class="btn-link download-single" data-filename="${escapeHtmlAttr(item.filename)}" data-markdown="${escapeHtmlAttr(item.markdown || '')}">下载 .md</button>
                    </div>
                </div>
                <div class="result-preview" id="${previewId}">
                    ${rawPreview}
                </div>
            </div>
        `;
    }

    function downloadSingle(filename, markdown) {
        const baseName = filename.replace(/\.[^/.]+$/, '');
        const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${baseName}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    async function downloadZip() {
        const zipResults = resultsData.filter(r => r.success);
        if (zipResults.length === 0) return;

        try {
            const res = await fetch('/api/download-zip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ results: zipResults }),
            });

            if (!res.ok) throw new Error('打包失败');

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'markitdown_results.zip';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast('ZIP 下载已开始', 'success');
        } catch (e) {
            showToast(e.message, 'error');
        }
    }

    // Clear
    clearBtn.addEventListener('click', () => {
        files = [];
        resultsData = [];
        fileList.innerHTML = '';
        results.innerHTML = '';
        results.classList.remove('has-content');
        updateActions();
    });

    // Toast
    function showToast(message, type = 'info') {
        const existing = document.querySelector('.toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Helpers
    function getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            pdf: '📄',
            docx: '📝',
            doc: '📝',
            xlsx: '📊',
            xls: '📊',
            pptx: '📊',
            ppt: '📊',
            html: '🌐',
            htm: '🌐',
            csv: '📊',
            json: '📝',
            xml: '📝',
            epub: '📚',
            txt: '📝',
            md: '📝',
            jpg: '🖼️',
            jpeg: '🖼️',
            png: '🖼️',
            gif: '🖼️',
            mp3: '🎧',
            wav: '🎧',
            mp4: '🎥',
            zip: '📦',
        };
        return icons[ext] || '📁';
    }

    function formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function escapeHtmlAttr(str) {
        return str
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
});
