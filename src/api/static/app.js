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

    // Admin Auth Elements
    const adminLoginBtn = document.getElementById('admin-login-btn');
    const adminModal = document.getElementById('admin-modal');
    const adminSecretInput = document.getElementById('admin-secret-input');
    const modalLoginBtn = document.getElementById('modal-login-btn');
    const modalCloseBtn = document.getElementById('modal-close-btn');

    // API Key Elements
    const createKeyBtn = document.getElementById('create-key-btn');
    const newKeyNameInput = document.getElementById('new-key-name');
    const newKeyAlert = document.getElementById('new-key-alert');
    const apikeyListBody = document.getElementById('apikey-list-body');

    let adminSecret = sessionStorage.getItem('ADMIN_SECRET') || '';

    // Token authentication helper
    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token');
    if (token) {
        sessionStorage.setItem('DASHBOARD_TOKEN', token);
    } else {
        token = sessionStorage.getItem('DASHBOARD_TOKEN') || '';
    }

    function getAuthHeaders(extraHeaders = {}) {
        const headers = { ...extraHeaders };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        if (adminSecret) {
            headers['X-Admin-Secret'] = adminSecret;
        }
        return headers;
    }

    function getAuthUrl(url) {
        if (!token) return url;
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}token=${encodeURIComponent(token)}`;
    }

    // Modal Events
    adminLoginBtn.addEventListener('click', () => adminModal.classList.remove('hidden'));
    modalCloseBtn.addEventListener('click', () => adminModal.classList.add('hidden'));

    modalLoginBtn.addEventListener('click', async () => {
        const secret = adminSecretInput.value.trim();
        if (!secret) return;

        try {
            const res = await fetch('/v1/admin/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ admin_secret: secret })
            });

            if (res.ok) {
                adminSecret = secret;
                sessionStorage.setItem('ADMIN_SECRET', adminSecret);
                adminModal.classList.add('hidden');
                adminLoginBtn.textContent = '🔓 Admin Verified';
                fetchApiKeys();
            } else {
                alert('Invalid Admin Secret Password');
            }
        } catch (e) {
            alert('Admin Authentication Failed: ' + e.message);
        }
    });

    // API Key Management Functions
    async function fetchApiKeys() {
        if (!adminSecret) return;

        try {
            const res = await fetch('/v1/admin/api-keys', {
                headers: getAuthHeaders()
            });

            if (!res.ok) {
                apikeyListBody.innerHTML = `<tr><td colspan="4" style="padding: 15px; text-align: center; color: #e74c3c;">🔒 Unauthorized: Admin Secret required</td></tr>`;
                return;
            }

            const data = await res.json();
            const keys = data.api_keys || [];

            if (keys.length === 0) {
                apikeyListBody.innerHTML = `<tr><td colspan="4" style="padding: 15px; text-align: center; color: #8a99ad;">No API keys generated yet</td></tr>`;
                return;
            }

            apikeyListBody.innerHTML = keys.map(k => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <td style="padding: 10px; font-weight: 500;">${k.name}</td>
                    <td style="padding: 10px; font-family: monospace; color: #2ecc71;">${k.masked_key}</td>
                    <td style="padding: 10px; color: #8a99ad; font-size: 12px;">${new Date(k.created_at).toLocaleString()}</td>
                    <td style="padding: 10px;">
                        <button onclick="revokeKey('${k.key_id}')" class="danger-btn" style="padding: 4px 10px; font-size: 12px;">Revoke</button>
                    </td>
                </tr>
            `).join('');

        } catch (e) {
            console.error('Failed to fetch API keys', e);
        }
    }

    window.revokeKey = async function(keyId) {
        if (!confirm('Are you sure you want to revoke this API Key?')) return;

        try {
            const res = await fetch(`/v1/admin/api-keys/${keyId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (res.ok) {
                fetchApiKeys();
            } else {
                alert('Failed to revoke API key');
            }
        } catch (e) {
            alert('Error revoking key: ' + e.message);
        }
    };

    createKeyBtn.addEventListener('click', async () => {
        const name = newKeyNameInput.value.trim();
        if (!name) {
            alert('Please enter a Client Name for the API Key');
            return;
        }

        if (!adminSecret) {
            adminModal.classList.remove('hidden');
            return;
        }

        try {
            const res = await fetch('/v1/admin/api-keys', {
                method: 'POST',
                headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({ name })
            });

            if (res.ok) {
                const data = await res.json();
                newKeyAlert.innerHTML = `<strong>New API Key Created!</strong><br><span style="font-size: 16px;">${data.raw_api_key}</span><br><span style="font-size: 11px; opacity: 0.8;">⚠️ Store this key now. It will NOT be shown again.</span>`;
                newKeyAlert.classList.remove('hidden');
                newKeyNameInput.value = '';
                fetchApiKeys();
            } else {
                alert('Failed to create API key');
            }
        } catch (e) {
            alert('Error creating API key: ' + e.message);
        }
    });

    // Auto load API keys if secret exists
    if (adminSecret) {
        adminLoginBtn.textContent = '🔓 Admin Verified';
        fetchApiKeys();
    }

    // Sync slider and input
    let capabilities = null;
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
            const res = await fetch(getAuthUrl('/dashboard/api/capabilities'), {
                headers: getAuthHeaders()
            });
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
        statusBadge.textContent = data.state;
        statusBadge.className = 'status-badge ' + data.state.toLowerCase();

        statModel.textContent = data.current_model || 'None';
        statCtx.textContent = data.current_n_ctx || '0';

        const used = data.vram_used || 0;
        const total = data.vram_total || 1;
        statVram.textContent = `${used} / ${total} MB`;
        vramFill.style.width = `${Math.min((used/total)*100, 100)}%`;

        if (data.state === 'LOADING') {
            loadingOverlay.classList.remove('hidden');
        } else {
            loadingOverlay.classList.add('hidden');
        }

        if (data.state === 'ERROR' && data.error_msg) {
            errorBanner.textContent = data.error_msg;
            errorBanner.classList.remove('hidden');
        } else {
            errorBanner.classList.add('hidden');
        }
    }

    // Connect SSE
    function connectSSE() {
        const evtSource = new EventSource(getAuthUrl('/dashboard/api/stream'));

        evtSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                updateStatusUI(data);
            } catch (e) {
                console.error("Failed to parse SSE data", e);
            }
        };

        evtSource.onerror = (err) => {
            console.error("SSE connection error", err);
            statusBadge.textContent = 'Disconnected';
            statusBadge.className = 'status-badge disconnected';
            evtSource.close();
            setTimeout(connectSSE, 5000);
        };
    }

    // Form submit
    manualForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const model = modelSelect.value;
        const n_ctx = parseInt(ctxInput.value);

        try {
            await fetch(getAuthUrl('/dashboard/api/apply'), {
                method: 'POST',
                headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                body: JSON.stringify({ model_id: model, n_ctx: n_ctx })
            });
        } catch (e) {
            console.error("Failed to apply preset", e);
        }
    });

    unloadBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to unload the model?')) return;
        try {
            await fetch(getAuthUrl('/dashboard/api/unload'), {
                method: 'POST',
                headers: getAuthHeaders()
            });
        } catch (e) {
            console.error("Failed to unload model", e);
        }
    });

    // Preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const model = btn.dataset.model;
            const ctx = parseInt(btn.dataset.ctx);

            try {
                await fetch(getAuthUrl('/dashboard/api/apply'), {
                    method: 'POST',
                    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                    body: JSON.stringify({ model_id: model, n_ctx: ctx })
                });
            } catch (e) {
                console.error("Failed to apply preset", e);
            }
        });
    });

    fetchCapabilities();
    connectSSE();
});
