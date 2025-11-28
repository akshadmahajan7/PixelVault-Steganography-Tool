document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Tab Switching Logic ---
    window.switchTab = function(tab) {
        const encSection = document.getElementById('section-encode');
        const decSection = document.getElementById('section-decode');
        const btnEnc = document.getElementById('btn-tab-encode');
        const btnDec = document.getElementById('btn-tab-decode');

        if (tab === 'encode') {
            encSection.classList.remove('hidden');
            decSection.classList.add('hidden');
            
            // Active State
            btnEnc.className = "flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 border-l-4 border-emerald-500 text-white shadow-lg transition-all";
            // Inactive State
            btnDec.className = "flex items-center gap-3 px-4 py-3 rounded-xl bg-transparent hover:bg-slate-800 border-l-4 border-transparent text-slate-400 transition-all";
        } else {
            encSection.classList.add('hidden');
            decSection.classList.remove('hidden');
            
            btnEnc.className = "flex items-center gap-3 px-4 py-3 rounded-xl bg-transparent hover:bg-slate-800 border-l-4 border-transparent text-slate-400 transition-all";
            btnDec.className = "flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 border-l-4 border-blue-500 text-white shadow-lg transition-all";
        }
    };

    // --- 2. File Input & Drag-Drop Visuals ---
    function setupFileInput(inputId, nameId, zoneId) {
        const input = document.getElementById(inputId);
        const nameDisplay = document.getElementById(nameId);
        const zone = document.getElementById(zoneId);

        // Handle File Selection via Click
        input.addEventListener('change', (e) => {
            if(e.target.files.length > 0) {
                nameDisplay.innerText = "Selected: " + e.target.files[0].name;
                nameDisplay.classList.add("text-emerald-400");
                zone.style.borderColor = "#10b981";
                zone.style.background = "rgba(16, 185, 129, 0.05)";
            }
        });

        // Handle Drag Over
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('dragover');
        });

        // Handle Drag Leave / Drop
        ['dragleave', 'drop'].forEach(event => {
            zone.addEventListener(event, () => zone.classList.remove('dragover'));
        });
    }

    setupFileInput('input-cover', 'name-cover', 'drop-cover');
    setupFileInput('input-secret', 'name-secret', 'drop-secret');
    setupFileInput('input-stego', 'name-stego', 'drop-stego');

    // --- 3. Toast Notifications ---
    window.showToast = function(msg, type='success') {
        const toast = document.getElementById('toast');
        const toastMsg = document.getElementById('toast-msg');
        const toastIcon = document.getElementById('toast-icon');

        toastMsg.innerText = msg;
        toastIcon.innerText = type === 'success' ? '✅' : '❌';
        toast.style.borderColor = type === 'success' ? '#10b981' : '#ef4444';
        
        // Show
        toast.classList.remove('toast-hidden');
        toast.classList.add('toast-visible');
        
        // Hide after 4 seconds
        setTimeout(() => {
            toast.classList.remove('toast-visible');
            toast.classList.add('toast-hidden');
        }, 4000);
    };

    // --- 4. AJAX Form Submission (Encoding) ---
    const encForm = document.getElementById('form-encode');
    if(encForm) {
        encForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btnText = document.getElementById('btn-text-enc');
            const loader = document.getElementById('loader-enc');
            const formData = new FormData(e.target);

            btnText.innerText = "PROCESSING...";
            loader.classList.remove('hidden');

            try {
                const response = await fetch('/api/encode', { method: 'POST', body: formData });
                
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = "pixelvault_secure.png";
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showToast("Success! Image downloaded.");
                    // Reset form
                    encForm.reset();
                    document.getElementById('name-cover').innerText = "Supported: PNG, JPG, BMP";
                } else {
                    const err = await response.json();
                    showToast(err.error || "Encryption failed", 'error');
                }
            } catch (err) {
                showToast("Network Error: Check console", 'error');
                console.error(err);
            } finally {
                btnText.innerText = "EXECUTE STEGANOGRAPHY";
                loader.classList.add('hidden');
            }
        });
    }

    // --- 5. AJAX Form Submission (Decoding) ---
    const decForm = document.getElementById('form-decode');
    if(decForm) {
        decForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btnText = document.getElementById('btn-text-dec');
            const loader = document.getElementById('loader-dec');
            const formData = new FormData(e.target);

            btnText.innerText = "EXTRACTING...";
            loader.classList.remove('hidden');

            try {
                const response = await fetch('/api/decode', { method: 'POST', body: formData });
                
                if (response.ok) {
                    // Extract filename from Content-Disposition header
                    const disposition = response.headers.get('Content-Disposition');
                    let filename = "extracted_secret";
                    if (disposition && disposition.indexOf('attachment') !== -1) {
                        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                        const matches = filenameRegex.exec(disposition);
                        if (matches != null && matches[1]) { 
                            filename = matches[1].replace(/['"]/g, '');
                        }
                    }

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showToast("Success! Secret file recovered.");
                    decForm.reset();
                } else {
                    const err = await response.json();
                    showToast(err.error || "Decryption failed", 'error');
                }
            } catch (err) {
                showToast("Network Error", 'error');
            } finally {
                btnText.innerText = "RETRIEVE DATA";
                loader.classList.add('hidden');
            }
        });
    }
});