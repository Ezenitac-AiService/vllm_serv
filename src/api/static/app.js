document.addEventListener('DOMContentLoaded', async () => {
    const statusBadge = document.getElementById('status-badge');
    const loadingOverlay = document.getElementById('loading-overlay');
    const statModel = document.getElementById('stat-model');
    const statCtx = document.getElementById('stat-ctx');
    const statVram = document.getElementById('stat-vram');
    const vramFill = document.getElementById('vram-fill');
    const errorBanner = document.getElementById('error-message');
    
    const manualForm = document.getElementById('manual-form');
    const modelSelect = document.getElementById('model-select');
    const ctxSlider = document.getElementById('ctx-slider');
    const ctxInput = document.getElementById('ctx-input');
    const unloadBtn = document.getElementById('unload-btn');
    const oomWarning = document.getElementById('oom-warning');

    let capabilities = null;

    // Sync slider and input
    ctxSlider.addEventListener('input', (e) => {
        ctxInput.value = e.target.value;
        checkOOM();
    });
    ctxInput.addEventListener('input', (e) => {
        ctxSlider.value = e.target.value;
        checkOOM();
    });
    modelSelect.addEventListener('change', checkOOM);

    async function fetchCapabilities() {
        try {
            const res = await fetch('/dashboard/api/capabilities');
            capabilities = await res.json();
            checkOOM();
        } catch (e) {
            console.error("Failed to fetch capabilities", e);
        }
    }

    function checkOOM() {
        if (!capabilities) return;
        const model = modelSelect.value;
        const ctx = parseInt(ctxInput.value);
        const limit = capabilities.limits[model];
        
        if (limit && ctx > limit) {
            oomWarning.classList.remove('hidden');
        } else {
            oomWarning.classList.add('hidden');
        }
    }

    function updateStatusUI(data) {
        // Badge
        statusBadge.textContent = data.state;
        statusBadge.className = 'status-badge ' + data.state.toLowerCase();
        
        // Stats
        statModel.textContent = data.current_model || 'None';
        statCtx.textContent = data.current_n_ctx || '0';
        
        const used = data.vram_used || 0;
        const total = data.vram_total || 1;
        statVram.textContent = `${used} / ${total} MB`;
        vramFill.style.width = `${Math.min((used/total)*100, 100)}%`;

        // Loading Overlay
        if (data.state === 'LOADING') {
            loadingOverlay.classList.remove('hidden');
        } else {
            loadingOverlay.classList.add('hidden');
        }

        // Errors
        if (data.state === 'ERROR' && data.error_msg) {
            errorBanner.textContent = data.error_msg;
            errorBanner.classList.remove('hidden');
        } else {
            errorBanner.classList.add('hidden');
        }
    }

    async function applyModel(model_id, n_ctx) {
        try {
            const res = await fetch('/dashboard/api/apply', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ model_id, n_ctx: parseInt(n_ctx) })
            });
            if (!res.ok) throw new Error("Apply failed");
        } catch(e) {
            console.error(e);
            alert("Error applying configuration");
        }
    }

    async function unloadModel() {
        try {
            await fetch('/dashboard/api/unload', { method: 'POST' });
        } catch(e) {
            console.error(e);
        }
    }

    // Connect SSE
    function connectSSE() {
        const es = new EventSource('/dashboard/api/stream');
        
        es.addEventListener('status', (e) => {
            const data = JSON.parse(e.data);
            updateStatusUI(data);
        });

        es.onerror = () => {
            statusBadge.textContent = 'DISCONNECTED';
            statusBadge.className = 'status-badge error';
        };
    }

    // Events
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const model = btn.dataset.model;
            const ctx = btn.dataset.ctx;
            modelSelect.value = model;
            ctxInput.value = ctx;
            ctxSlider.value = ctx;
            applyModel(model, ctx);
        });
    });

    manualForm.addEventListener('submit', (e) => {
        e.preventDefault();
        applyModel(modelSelect.value, ctxInput.value);
    });

    unloadBtn.addEventListener('click', () => {
        unloadModel();
    });

    // Init
    await fetchCapabilities();
    connectSSE();
});
