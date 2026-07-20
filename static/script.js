/**
 * script.js - Frontend logic for BI Statement Converter
 * 
 * Handles drag-and-drop upload, form submission, progress animation,
 * and auto-download of converted Excel files.
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Elements ──
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const filePreview = document.getElementById('filePreview');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const btnRemove = document.getElementById('btnRemove');
    const btnConvert = document.getElementById('btnConvert');

    const uploadSection = document.getElementById('uploadSection');
    const processingSection = document.getElementById('processingSection');
    const successSection = document.getElementById('successSection');
    const errorSection = document.getElementById('errorSection');

    const processingText = document.getElementById('processingText');
    const progressFill = document.getElementById('progressFill');

    const statCardholders = document.getElementById('statCardholders');
    const statTransactions = document.getElementById('statTransactions');
    const statRows = document.getElementById('statRows');

    const errorMessage = document.getElementById('errorMessage');
    const btnAnother = document.getElementById('btnAnother');
    const btnRetry = document.getElementById('btnRetry');

    let selectedFile = null;

    // ── Helpers ──
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function showSection(section) {
        [uploadSection, processingSection, successSection, errorSection].forEach(s => {
            s.style.display = 'none';
        });
        section.style.display = 'block';
    }

    function animateProgress() {
        const steps = [
            { width: '15%', text: 'Membaca PDF...', delay: 300 },
            { width: '35%', text: 'Mengekstrak data transaksi...', delay: 1500 },
            { width: '55%', text: 'Menggabungkan multi-line descriptions...', delay: 3000 },
            { width: '75%', text: 'Menangani tabel lintas halaman...', delay: 4500 },
            { width: '90%', text: 'Membuat file Excel...', delay: 6000 },
        ];

        steps.forEach(step => {
            setTimeout(() => {
                progressFill.style.width = step.width;
                processingText.textContent = step.text;
            }, step.delay);
        });
    }

    // ── File Selection ──
    function handleFileSelect(file) {
        if (!file) return;
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('File harus berformat PDF');
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        filePreview.style.display = 'block';

        // Subtle animation
        filePreview.style.opacity = '0';
        filePreview.style.transform = 'translateY(10px)';
        requestAnimationFrame(() => {
            filePreview.style.transition = 'all 0.3s ease-out';
            filePreview.style.opacity = '1';
            filePreview.style.transform = 'translateY(0)';
        });
    }

    function clearFile() {
        selectedFile = null;
        fileInput.value = '';
        filePreview.style.display = 'none';
    }

    // ── Drag & Drop ──
    uploadZone.addEventListener('click', () => fileInput.click());

    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadZone.classList.remove('drag-over');

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

    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFile();
    });

    // ── Convert ──
    btnConvert.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Show processing state
        showSection(processingSection);
        progressFill.style.width = '0%';
        animateProgress();

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let errorMsg = `Server error (${response.status})`;
                try {
                    const data = await response.json();
                    errorMsg = data.error || errorMsg;
                } catch {
                    // Response is not JSON (e.g. Vercel timeout HTML page)
                    const text = await response.text().catch(() => '');
                    if (response.status === 504 || text.includes('FUNCTION_INVOCATION_TIMEOUT')) {
                        errorMsg = 'Proses terlalu lama (timeout). File PDF mungkin terlalu besar untuk diproses di server. Coba gunakan versi lokal.';
                    } else if (response.status === 413) {
                        errorMsg = 'File terlalu besar. Maksimal ukuran file adalah 100MB.';
                    } else {
                        errorMsg = `Server error (${response.status}): ${text.substring(0, 200)}`;
                    }
                }
                throw new Error(errorMsg);
            }

            // Get stats from headers
            const cardholders = response.headers.get('X-Total-Cardholders') || '0';
            const transactions = response.headers.get('X-Total-Transactions') || '0';
            const rows = response.headers.get('X-Total-Rows') || '0';

            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            
            // Extract filename from Content-Disposition header
            const disposition = response.headers.get('Content-Disposition');
            let downloadName = 'output.xlsx';
            if (disposition) {
                const filenameMatch = disposition.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
                if (filenameMatch) {
                    downloadName = decodeURIComponent(filenameMatch[1].replace(/"/g, ''));
                }
            }

            a.href = url;
            a.download = downloadName;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            // Show success
            progressFill.style.width = '100%';
            setTimeout(() => {
                statCardholders.textContent = cardholders;
                statTransactions.textContent = transactions;
                statRows.textContent = rows;
                showSection(successSection);
            }, 500);

        } catch (err) {
            errorMessage.textContent = err.message;
            showSection(errorSection);
        }
    });

    // ── Reset Buttons ──
    btnAnother.addEventListener('click', () => {
        clearFile();
        showSection(uploadSection);
    });

    btnRetry.addEventListener('click', () => {
        clearFile();
        showSection(uploadSection);
    });
});
