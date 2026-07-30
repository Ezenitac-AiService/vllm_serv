// vLLM Control Center & AI Playground SPA JavaScript Controller (037-dashboard-enhancement)

document.addEventListener('DOMContentLoaded', () => {
    // --- Global Application State ---
    const state = {
        adminSecret: sessionStorage.getItem('adminSecret') || '',
        activeTab: 'monitoring',
        currentCapabilities: null,
        chart: null,
        sseSource: null,
        metricsHistory: {
            timestamps: [],
            vramUsed: [],
            gpuUtil: []
        }
    };

    // --- DOM Elements ---
    const elements = {
        tabs: document.querySelectorAll('.tab-btn'),
        tabPanels: document.querySelectorAll('.tab-panel'),
        statusBadge: document.getElementById('status-badge'),
        platformProfileSub: document.getElementById('platform-profile-subtitle'),
        // Stat Cards
        statModel: document.getElementById('stat-model'),
        statProfile: document.getElementById('stat-profile'),
        statVram: document.getElementById('stat-vram'),
        vramFill: document.getElementById('vram-fill'),
        vramWarningBadge: document.getElementById('vram-warning-badge'),
        statCtx: document.getElementById('stat-ctx'),
        statCtxLimit: document.getElementById('stat-ctx-limit'),
        statSpeed: document.getElementById('stat-speed'),
        statTtft: document.getElementById('stat-ttft'),
        // Control Tab
        presetsGrid: document.getElementById('presets-grid'),
        modelSelect: document.getElementById('model-select'),
        ctxSlider: document.getElementById('ctx-slider'),
        ctxInput: document.getElementById('ctx-input'),
        oomWarning: document.getElementById('oom-warning'),
        manualForm: document.getElementById('manual-form'),
        unloadBtn: document.getElementById('unload-btn'),
        // Admin Auth Modal
        adminLoginBtn: document.getElementById('admin-login-btn'),
        adminModal: document.getElementById('admin-modal'),
        adminSecretInput: document.getElementById('admin-secret-input'),
        modalLoginBtn: document.getElementById('modal-login-btn'),
        modalCloseBtn: document.getElementById('modal-close-btn'),
        // Playground
        pgSystemPrompt: document.getElementById('pg-system-prompt'),
        pgTemp: document.getElementById('pg-temp'),
        pgTempVal: document.getElementById('pg-temp-val'),
        pgTopP: document.getElementById('pg-top-p'),
        pgTopPVal: document.getElementById('pg-top-p-val'),
        pgMaxTokens: document.getElementById('pg-max-tokens'),
        pgPromptInput: document.getElementById('pg-prompt-input'),
        pgSubmitBtn: document.getElementById('pg-submit-btn'),
        pgActiveModel: document.getElementById('pg-active-model'),
        pgOutputText: document.getElementById('pg-output-text'),
        pgMetricTtft: document.getElementById('pg-metric-ttft'),
        pgMetricSpeed: document.getElementById('pg-metric-speed'),
        pgMetricLatency: document.getElementById('pg-metric-latency'),
        pgMetricTokens: document.getElementById('pg-metric-tokens'),
        codeExportBtn: document.getElementById('code-export-btn'),
        // Code Modal
        codeModal: document.getElementById('code-modal'),
        codeSnippet: document.getElementById('code-snippet'),
        copyCodeBtn: document.getElementById('copy-code-btn'),
        closeCodeBtn: document.getElementById('close-code-btn'),
        codeTabs: document.querySelectorAll('.code-tab'),
        // Audit
        auditListBody: document.getElementById('audit-list-body'),
        refreshAuditBtn: document.getElementById('refresh-audit-btn'),
        // Loading Overlay
        loadingOverlay: document.getElementById('loading-overlay')
    };

    // --- 1. SPA Navigation Tab Switcher ---
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab');
            elements.tabs.forEach(t => t.classList.remove('active'));
            elements.tabPanels.forEach(p => p.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`tab-${target}`).classList.add('active');
            state.activeTab = target;

            if (target === 'audit') {
                loadAuditLogs();
            }
        });
    });

    // --- 2. Chart.js Time-Series Canvas Graph Initialization (FR-001) ---
    function initMetricsChart() {
        if (typeof Chart === 'undefined') {
            console.warn('[Dashboard] Chart.js CDN not loaded or offline. Graph rendering will fallback.');
            return;
        }
        try {
            const ctx = document.getElementById('metricsChart').getContext('2d');
            state.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: state.metricsHistory.timestamps,
                    datasets: [
                        {
                            label: 'VRAM Used (MB)',
                            data: state.metricsHistory.vramUsed,
                            borderColor: '#06b6d4',
                            backgroundColor: 'rgba(6, 182, 212, 0.15)',
                            fill: true,
                            tension: 0.3,
                            yAxisID: 'y'
                        },
                        {
                            label: 'GPU Utilization (%)',
                            data: state.metricsHistory.gpuUtil,
                            borderColor: '#3b82f6',
                            backgroundColor: 'transparent',
                            borderDash: [5, 5],
                            tension: 0.3,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: false,
                    scales: {
                        x: {
                            ticks: { color: '#9ca3af', maxTicksLimit: 10 },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: {
                            position: 'left',
                            ticks: { color: '#06b6d4' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            title: { display: true, text: 'VRAM (MB)', color: '#06b6d4' }
                        },
                        y1: {
                            position: 'right',
                            min: 0,
                            max: 100,
                            ticks: { color: '#3b82f6' },
                            grid: { drawOnChartArea: false },
                            title: { display: true, text: 'GPU %', color: '#3b82f6' }
                        }
                    },
                    plugins: {
                        legend: { labels: { color: '#f3f4f6' } }
                    }
                }
            });
        } catch (err) {
            console.error('[Dashboard] Error initializing Chart.js:', err);
        }
    }


    // --- 3. Real-Time SSE Resource Metric Listener (FR-001, FR-003) ---
    function setupMetricSSE() {
        if (state.sseSource) {
            state.sseSource.close();
        }

        try {
            state.sseSource = new EventSource('/dashboard/api/stream');
            state.sseSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboardState(data);
            };
            state.sseSource.onerror = () => {
                elements.statusBadge.textContent = 'Polling Metric...';
                elements.statusBadge.className = 'status-badge loading';
                // Fallback polling
                fetchStatusFallback();
            };
        } catch (e) {
            fetchStatusFallback();
        }
    }

    async function fetchStatusFallback() {
        try {
            const res = await fetch('/dashboard/api/status');
            if (res.ok) {
                const data = await res.json();
                updateDashboardState(data);
            }
        } catch (e) {
            elements.statusBadge.textContent = 'Disconnected';
            elements.statusBadge.className = 'status-badge error';
        }
    }

    function updateDashboardState(data) {
        // Status Badge
        const statusStr = (data.state || 'UNKNOWN').toUpperCase();
        elements.statusBadge.textContent = statusStr;
        if (statusStr === 'READY') {
            elements.statusBadge.className = 'status-badge ready';
        } else if (statusStr === 'LOADING' || statusStr === 'DOWNLOADING') {
            elements.statusBadge.className = 'status-badge loading';
        } else {
            elements.statusBadge.className = 'status-badge error';
        }

        // Active Model & Context
        const modelName = data.current_model || 'Unloaded';
        elements.statModel.textContent = modelName;
        elements.pgActiveModel.textContent = `Model: ${modelName}`;
        elements.statCtx.textContent = data.current_n_ctx ? `${data.current_n_ctx}` : '--';

        // VRAM Calculations & 90% Warning Badge (FR-003)
        const vramTotal = data.vram_total || 8192;
        const vramUsed = data.vram_used || 0;
        const vramPct = (vramUsed / vramTotal) * 100;

        elements.statVram.textContent = `${vramUsed} / ${vramTotal} MB (${vramPct.toFixed(1)}%)`;
        elements.vramFill.style.width = `${Math.min(vramPct, 100)}%`;

        if (vramPct >= 90) {
            elements.vramWarningBadge.classList.remove('hidden');
        } else {
            elements.vramWarningBadge.classList.add('hidden');
        }

        // Push to Chart
        const timeStr = new Date().toLocaleTimeString();
        if (state.metricsHistory.timestamps.length > 20) {
            state.metricsHistory.timestamps.shift();
            state.metricsHistory.vramUsed.shift();
            state.metricsHistory.gpuUtil.shift();
        }
        state.metricsHistory.timestamps.push(timeStr);
        state.metricsHistory.vramUsed.push(vramUsed);
        state.metricsHistory.gpuUtil.push(Math.round(vramPct * 0.9)); // GPU estimate

        if (state.chart) {
            state.chart.update();
        }
    }

    // --- 4. Dynamic Platform Capabilities & Model Preset Loader (FR-002) ---
    async function loadCapabilities() {
        try {
            const res = await fetch('/dashboard/api/capabilities');
            if (!res.ok) return;
            const caps = await res.json();
            state.currentCapabilities = caps;

            elements.platformProfileSub.textContent = `Platform Profile: ${caps.platform_profile} (${caps.vram_total}MB VRAM)`;
            elements.statProfile.textContent = `Profile: ${caps.platform_profile}`;

            // Populate Model Dropdown
            elements.modelSelect.innerHTML = '';
            caps.available_models.forEach(model => {
                const opt = document.createElement('option');
                opt.value = model;
                opt.textContent = model;
                if (model === caps.current_model) opt.selected = true;
                elements.modelSelect.appendChild(opt);
            });

            // Populate Presets Grid
            elements.presetsGrid.innerHTML = '';
            caps.available_models.forEach(model => {
                const card = document.createElement('div');
                card.className = 'preset-card';
                card.innerHTML = `
                    <h4>🤖 ${model}</h4>
                    <p>Context Scaling Preset: 4096 / 8192</p>
                `;
                card.addEventListener('click', () => {
                    elements.modelSelect.value = model;
                    applyPreset(model, 4096);
                });
                elements.presetsGrid.appendChild(card);
            });
        } catch (e) {
            console.error('Failed to load capabilities:', e);
        }
    }

    // Context Slider Sync
    elements.ctxSlider.addEventListener('input', (e) => {
        elements.ctxInput.value = e.target.value;
        checkOomWarning();
    });
    elements.ctxInput.addEventListener('input', (e) => {
        elements.ctxSlider.value = e.target.value;
        checkOomWarning();
    });

    function checkOomWarning() {
        const val = parseInt(elements.ctxInput.value, 10);
        if (val > 8192) {
            elements.oomWarning.classList.remove('hidden');
        } else {
            elements.oomWarning.classList.add('hidden');
        }
    }

    // --- 5. Admin Authentication & State-Mutating Actions (FR-006) ---
    elements.adminLoginBtn.addEventListener('click', () => {
        elements.adminModal.classList.remove('hidden');
    });
    elements.modalCloseBtn.addEventListener('click', () => {
        elements.adminModal.classList.add('hidden');
    });
    elements.modalLoginBtn.addEventListener('click', () => {
        const secret = elements.adminSecretInput.value.trim();
        if (secret) {
            state.adminSecret = secret;
            sessionStorage.setItem('adminSecret', secret);
            elements.adminModal.classList.add('hidden');
            elements.adminLoginBtn.textContent = '✅ Authenticated';
            elements.adminLoginBtn.className = 'secondary-btn ready';
        }
    });

    async function applyPreset(modelId, nCtx) {
        if (!state.adminSecret) {
            elements.adminModal.classList.remove('hidden');
            return;
        }

        elements.loadingOverlay.classList.remove('hidden');
        try {
            const res = await fetch('/dashboard/api/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Secret': state.adminSecret
                },
                body: JSON.stringify({ model_id: modelId, n_ctx: nCtx })
            });

            if (res.status === 401) {
                alert('401 Unauthorized: Invalid Admin Secret password!');
                state.adminSecret = '';
                sessionStorage.removeItem('adminSecret');
                elements.adminModal.classList.remove('hidden');
            } else if (res.ok) {
                const data = await res.json();
                console.log('Apply success:', data);
            }
        } catch (e) {
            alert('Failed to apply configuration: ' + e);
        } finally {
            setTimeout(() => elements.loadingOverlay.classList.add('hidden'), 1000);
        }
    }

    elements.manualForm.addEventListener('submit', (e) => {
        e.preventDefault();
        applyPreset(elements.modelSelect.value, parseInt(elements.ctxInput.value, 10));
    });

    elements.unloadBtn.addEventListener('click', async () => {
        if (!state.adminSecret) {
            elements.adminModal.classList.remove('hidden');
            return;
        }
        elements.loadingOverlay.classList.remove('hidden');
        try {
            await fetch('/dashboard/api/unload', {
                method: 'POST',
                headers: { 'X-Admin-Secret': state.adminSecret }
            });
        } finally {
            setTimeout(() => elements.loadingOverlay.classList.add('hidden'), 1000);
        }
    });

    // --- 6. AI Playground & Real-time Benchmark (FR-007, FR-008, FR-009) ---
    elements.pgTemp.addEventListener('input', (e) => elements.pgTempVal.textContent = e.target.value);
    elements.pgTopP.addEventListener('input', (e) => elements.pgTopPVal.textContent = e.target.value);

    elements.pgSubmitBtn.addEventListener('click', async () => {
        const prompt = elements.pgPromptInput.value.trim();
        if (!prompt) {
            alert('Please enter a prompt for testing.');
            return;
        }

        elements.pgOutputText.textContent = 'Sending inference request to active model...';
        elements.pgSubmitBtn.disabled = true;

        try {
            const res = await fetch('/dashboard/api/playground', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: elements.modelSelect.value || 'qwen3.5-4b',
                    system_prompt: elements.pgSystemPrompt.value,
                    prompt: prompt,
                    temperature: parseFloat(elements.pgTemp.value),
                    top_p: parseFloat(elements.pgTopP.value),
                    max_tokens: parseInt(elements.pgMaxTokens.value, 10)
                })
            });

            if (res.ok) {
                const data = await res.json();
                elements.pgOutputText.textContent = data.text;
                elements.pgMetricTtft.textContent = `${data.ttft_ms} ms`;
                elements.pgMetricSpeed.textContent = `${data.token_speed_tok_s} tok/s`;
                elements.pgMetricLatency.textContent = `${data.total_latency_s} s`;
                elements.pgMetricTokens.textContent = `${data.prompt_tokens} in / ${data.completion_tokens} out`;

                // Update Header Summary
                elements.statSpeed.textContent = `${data.token_speed_tok_s} tok/s`;
                elements.statTtft.textContent = `TTFT: ${data.ttft_ms} ms`;
            } else {
                elements.pgOutputText.textContent = 'Error executing playground inference.';
            }
        } catch (e) {
            elements.pgOutputText.textContent = `Failed: ${e}`;
        } finally {
            elements.pgSubmitBtn.disabled = false;
        }
    });

    // Code Export Generator
    elements.codeExportBtn.addEventListener('click', () => {
        generateCodeSnippet('curl');
        elements.codeModal.classList.remove('hidden');
    });
    elements.closeCodeBtn.addEventListener('click', () => elements.codeModal.classList.add('hidden'));

    elements.codeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.codeTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            generateCodeSnippet(tab.getAttribute('data-lang'));
        });
    });

    function generateCodeSnippet(lang) {
        const model = elements.modelSelect.value || 'qwen3.5-4b';
        const prompt = elements.pgPromptInput.value || 'Hello AI';
        const sys = elements.pgSystemPrompt.value || 'You are helpful';

        if (lang === 'curl') {
            elements.codeSnippet.textContent = `curl http://10.0.0.41:8000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer sk-vllm-key" \\
  -d '{
    "model": "${model}",
    "messages": [
      {"role": "system", "content": "${sys}"},
      {"role": "user", "content": "${prompt}"}
    ],
    "temperature": ${elements.pgTemp.value},
    "top_p": ${elements.pgTopP.value}
  }'`;
        } else {
            elements.codeSnippet.textContent = `from openai import OpenAI

client = OpenAI(
    base_url="http://10.0.0.41:8000/v1",
    api_key="sk-vllm-key"
)

response = client.chat.completions.create(
    model="${model}",
    messages=[
        {"role": "system", "content": "${sys}"},
        {"role": "user", "content": "${prompt}"}
    ],
    temperature=${elements.pgTemp.value},
    top_p=${elements.pgTopP.value}
)

print(response.choices[0].message.content)`;
        }
    }

    elements.copyCodeBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(elements.codeSnippet.textContent);
        elements.copyCodeBtn.textContent = '✅ Copied!';
        setTimeout(() => elements.copyCodeBtn.textContent = '📋 Copy Code', 2000);
    });

    // --- 7. Audit Log Timeline Loader (FR-004) ---
    async function loadAuditLogs() {
        try {
            const res = await fetch('/dashboard/api/audit');
            if (!res.ok) return;
            const data = await res.json();

            elements.auditListBody.innerHTML = '';
            if (data.logs.length === 0) {
                elements.auditListBody.innerHTML = '<tr><td colspan="6" class="table-placeholder">No client access logs recorded yet.</td></tr>';
                return;
            }

            data.logs.forEach(log => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${log.timestamp}</td>
                    <td><code>${log.client_ip}</code></td>
                    <td><span class="live-indicator">Allowed Subnet</span></td>
                    <td><code>${log.endpoint}</code></td>
                    <td><span class="badge ${log.status_code < 400 ? 'badge-info' : 'warning-badge'}">${log.status_code}</span></td>
                    <td>${log.process_time_ms} ms</td>
                `;
                elements.auditListBody.appendChild(tr);
            });
        } catch (e) {
            elements.auditListBody.innerHTML = '<tr><td colspan="6" class="table-placeholder">Error loading audit logs.</td></tr>';
        }
    }

    elements.refreshAuditBtn.addEventListener('click', loadAuditLogs);

    // --- Feature 043: API Security & Metrics Handlers ---
    async function loadKeyMetrics() {
        const apiKeyBody = document.getElementById('apikey-list-body');
        const top5Container = document.getElementById('top5-ranking-container');
        const toggleText = document.getElementById('toggle-status-text');
        if (!apiKeyBody) return;

        try {
            const res = await fetch('/dashboard/api/keys/metrics');
            if (res.ok) {
                const data = await res.json();
                
                // Render Top 5 Card
                if (data.top_5 && data.top_5.length > 0) {
                    top5Container.innerHTML = data.top_5.map((item, idx) => `
                        <div style="display: inline-block; background: rgba(255,255,255,0.05); padding: 8px 12px; margin: 4px; border-radius: 6px;">
                            <strong>#${idx + 1} ${item.api_key.substring(0, 10)}...</strong>
                            <div style="font-size: 0.85em; color: #a0aec0;">Tokens: ${item.prompt_tokens + item.completion_tokens} | Est. Cost: $${item.estimated_cost_usd}</div>
                        </div>
                    `).join('');
                } else {
                    top5Container.innerHTML = '<p class="table-placeholder">No active key usage metrics recorded yet.</p>';
                }

                // Render Key Table
                if (data.metrics && data.metrics.length > 0) {
                    apiKeyBody.innerHTML = '';
                    data.metrics.forEach(m => {
                        const tr = document.createElement('tr');
                        const isAnomaly = m.error_count > 5 || (m.prompt_tokens + m.completion_tokens) > 50000;
                        tr.innerHTML = `
                            <td>Client-App</td>
                            <td><code>${m.api_key.substring(0, 8)}****</code></td>
                            <td>${m.request_count}</td>
                            <td>${m.error_count} ${isAnomaly ? '<span title="High Error/Traffic Anomaly">⚠️</span>' : ''}</td>
                            <td>${m.prompt_tokens}</td>
                            <td>${m.completion_tokens}</td>
                            <td>$${m.estimated_cost_usd}</td>
                            <td>
                                <button class="danger-btn revoke-key-btn" data-key="${m.api_key}" style="padding: 2px 8px; font-size: 0.8em;">Revoke</button>
                            </td>
                        `;
                        apiKeyBody.appendChild(tr);
                    });

                    // Attach revoke handlers
                    document.querySelectorAll('.revoke-key-btn').forEach(btn => {
                        btn.addEventListener('click', async (e) => {
                            const keyToRevoke = e.target.getAttribute('data-key');
                            const adminSecret = prompt('Enter Admin Secret to revoke key:');
                            if (!adminSecret) return;
                            const revRes = await fetch('/dashboard/api/keys/revoke', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-Admin-Secret': adminSecret
                                },
                                body: JSON.stringify({ key: keyToRevoke })
                            });
                            if (revRes.ok) {
                                alert('API key revoked successfully.');
                                loadKeyMetrics();
                            } else {
                                alert('Failed to revoke API key.');
                            }
                        });
                    });
                } else {
                    apiKeyBody.innerHTML = '<tr><td colspan="8" class="table-placeholder">No key metrics recorded yet.</td></tr>';
                }
            }
        } catch (e) {
            console.error('Failed loading key metrics:', e);
        }
    }

    const toggleSecurityBtn = document.getElementById('toggle-security-btn');
    if (toggleSecurityBtn) {
        toggleSecurityBtn.addEventListener('click', async () => {
            const adminSecret = prompt('Enter Admin Secret to toggle Security Mode:');
            if (!adminSecret) return;
            const currentState = document.getElementById('toggle-status-text').textContent.includes('ENABLED');
            const targetState = !currentState;

            const res = await fetch('/dashboard/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Admin-Secret': adminSecret
                },
                body: JSON.stringify({ api_key_enabled: targetState })
            });
            if (res.ok) {
                const data = await res.json();
                alert(data.message);
                document.getElementById('toggle-status-text').textContent = `Current Mode: ${targetState ? 'ENABLED (API Key Required)' : 'DISABLED (Public Access)'}`;
            } else {
                alert('Unauthorized: Invalid Admin Secret.');
            }
        });
    }

    const exportCsvBtn = document.getElementById('export-csv-btn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            window.location.href = '/dashboard/api/keys/export/csv';
        });
    }

    // --- Initial Bootstrapping ---
    initMetricsChart();
    setupMetricSSE();
    loadCapabilities();
    loadKeyMetrics();
});
