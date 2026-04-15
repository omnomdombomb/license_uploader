/**
 * License Uploader - Main JavaScript
 */

// API Configuration Manager - Server-side session storage (secure)
const APIConfig = {
    /**
     * Get API configuration from server-side session
     * SECURITY: API keys are stored server-side, not in browser localStorage
     */
    async getConfig() {
        try {
            const response = await fetch('/api/config', {
                method: 'GET',
                credentials: 'same-origin'  // Send session cookie
            });
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Failed to get API config:', error);
        }
        // Fallback to defaults
        return {
            litellm_api_key: '',
            alma_api_key: '',
            llm_model: 'gpt-5'
        };
    },

    /**
     * Save API configuration to server-side session
     * SECURITY: Keys stored server-side with httpOnly cookies
     */
    async saveConfig(config) {
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',  // Send session cookie
                body: JSON.stringify(config)
            });
            return response.ok;
        } catch (error) {
            console.error('Failed to save API config:', error);
            return false;
        }
    },

    /**
     * Initialize API config inputs from server session
     */
    async initializeInputs() {
        const config = await this.getConfig();

        const litellmInput = document.getElementById('litellm-api-key');
        const almaInput = document.getElementById('alma-api-key');
        const modelSelect = document.getElementById('llm-model');

        if (litellmInput) {
            litellmInput.value = config.litellm_api_key;
            litellmInput.addEventListener('change', async (e) => {
                await this.saveConfig({
                    litellm_api_key: e.target.value,
                    alma_api_key: config.alma_api_key,
                    llm_model: config.llm_model
                });
            });
        }

        if (almaInput) {
            almaInput.value = config.alma_api_key;
            almaInput.addEventListener('change', async (e) => {
                await this.saveConfig({
                    litellm_api_key: config.litellm_api_key,
                    alma_api_key: e.target.value,
                    llm_model: config.llm_model
                });
            });
        }

        if (modelSelect) {
            const chosen = await this.populateModels(modelSelect, config.llm_model);
            // If populateModels auto-switched (saved model was unavailable),
            // persist the new selection immediately so extraction uses it.
            if (chosen && chosen !== config.llm_model) {
                await this.saveConfig({
                    litellm_api_key: config.litellm_api_key,
                    alma_api_key: config.alma_api_key,
                    llm_model: chosen
                });
                config.llm_model = chosen;
            }
            modelSelect.addEventListener('change', async (e) => {
                await this.saveConfig({
                    litellm_api_key: config.litellm_api_key,
                    alma_api_key: config.alma_api_key,
                    llm_model: e.target.value
                });
            });
        }
    },

    /**
     * Populate the model <select> from the live LiteLLM /v1/models list.
     * Falls back to the previously-configured model if the fetch fails.
     */
    async populateModels(selectEl, preferredModel) {
        const statusEl = document.getElementById('llm-model-status');
        const setStatus = (msg, isError) => {
            if (!statusEl) return;
            if (!msg) {
                statusEl.style.display = 'none';
                statusEl.textContent = '';
                return;
            }
            statusEl.style.display = '';
            statusEl.textContent = msg;
            statusEl.style.color = isError ? '#b00020' : '';
        };

        try {
            const resp = await fetch('/api/models', { credentials: 'same-origin' });
            const data = await resp.json();

            if (!data.success || !Array.isArray(data.models) || data.models.length === 0) {
                throw new Error(data.error || 'No models returned');
            }

            const models = data.models;
            const configured = preferredModel || data.configured_model;
            const configuredAvailable = configured && models.includes(configured);

            selectEl.innerHTML = '';
            for (const id of models) {
                const opt = document.createElement('option');
                opt.value = id;
                opt.textContent = id;
                selectEl.appendChild(opt);
            }

            // If the saved model is no longer available, auto-switch to the
            // first available one. Keeping it selected just reproduces the
            // upstream 401 every upload.
            const finalValue = configuredAvailable ? configured : models[0];
            selectEl.value = finalValue;

            if (configured && !configuredAvailable) {
                setStatus(`⚠ Saved model "${configured}" is no longer available on the gateway. Switched to "${finalValue}".`, true);
            } else {
                setStatus('', false);
            }
            return finalValue;
        } catch (err) {
            console.error('Failed to load model list:', err);
            // Fallback: keep the saved value so the app still works
            selectEl.innerHTML = '';
            const opt = document.createElement('option');
            opt.value = preferredModel || 'gpt-5';
            opt.textContent = opt.value;
            selectEl.appendChild(opt);
            selectEl.value = opt.value;
            setStatus('Could not load models from LiteLLM — using saved value.', true);
            return opt.value;
        }
    }
};

// CSRF Token Management
const CSRF = {
    token: null,

    /**
     * Get CSRF token from server
     */
    async getToken() {
        if (!this.token) {
            try {
                const response = await fetch('/api/csrf-token', {
                    credentials: 'same-origin'
                });
                const data = await response.json();
                this.token = data.csrf_token;
            } catch (error) {
                console.error('Failed to get CSRF token:', error);
            }
        }
        return this.token;
    }
};

// Utility Functions
const Utils = {
    /**
     * Show status message
     */
    showMessage(element, message, type = 'info') {
        element.textContent = message;
        element.className = `status-msg ${type}`;
        element.style.display = 'block';

        // Auto-hide after 5 seconds for success/info messages
        if (type !== 'error') {
            setTimeout(() => {
                element.style.display = 'none';
            }, 5000);
        }
    },

    /**
     * Hide message
     */
    hideMessage(element) {
        element.style.display = 'none';
    },

    /**
     * Show loading modal
     */
    showLoading(text = 'Processing...') {
        const modal = document.getElementById('loading-modal');
        const loadingText = document.getElementById('loading-text');
        if (modal) {
            if (loadingText) loadingText.textContent = text;
            modal.style.display = 'flex';
        }
    },

    /**
     * Hide loading modal
     */
    hideLoading() {
        const modal = document.getElementById('loading-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    },

    /**
     * Validate required fields
     */
    validateRequired(fields) {
        const errors = [];

        fields.forEach(field => {
            const element = document.getElementById(field.id);
            if (!element) return;

            const value = element.value.trim();
            if (!value) {
                errors.push(field.name);
                element.style.borderColor = 'var(--danger-color)';
            } else {
                element.style.borderColor = '';
            }
        });

        return errors;
    },

    /**
     * Format date to YYYY-MM-DD
     */
    formatDate(date) {
        if (!date) return null;
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API Service
const API = {
    /**
     * Generic fetch wrapper
     * SECURITY: API keys stored server-side, sent via session cookies (not headers)
     */
    async request(url, options = {}) {
        const defaultOptions = {
            credentials: 'same-origin',  // Send session cookie
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const config = { ...defaultOptions, ...options };

        // Add CSRF token for POST/PUT/DELETE/PATCH requests
        const method = (config.method || 'GET').toUpperCase();
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
            const csrfToken = await CSRF.getToken();
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken;
            }
        }

        // Merge headers if options has headers
        if (options.headers) {
            config.headers = { ...defaultOptions.headers, ...options.headers };
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Test Alma API connection
     */
    async testConnection() {
        return await this.request('/test-connection');
    },

    /**
     * Get vendors from Alma
     */
    async getVendors() {
        return await this.request('/get-vendors');
    },

    /**
     * Upload file
     */
    async uploadFile(formData) {
        return await this.request('/upload', {
            method: 'POST',
            headers: {}, // Let browser set Content-Type for FormData
            body: formData
        });
    },

    /**
     * Refine a specific term
     */
    async refineTerm(termCode, currentValue) {
        return await this.request('/refine-term', {
            method: 'POST',
            body: JSON.stringify({
                term_code: termCode,
                current_value: currentValue
            })
        });
    },

    /**
     * Submit license to Alma
     */
    async submitLicense(licenseData) {
        return await this.request('/submit-license', {
            method: 'POST',
            body: JSON.stringify(licenseData)
        });
    },

    /**
     * Get extraction prompt
     */
    async getPrompt() {
        return await this.request('/api/prompt', {
            method: 'GET'
        });
    },

    /**
     * Update extraction prompt
     */
    async updatePrompt(promptText) {
        return await this.request('/api/prompt', {
            method: 'POST',
            body: JSON.stringify({ prompt: promptText })
        });
    },

    /**
     * Reset prompt to default
     */
    async resetPrompt() {
        return await this.request('/api/prompt', {
            method: 'DELETE'
        });
    },

    /**
     * Get all term descriptions (with custom overrides)
     */
    async getTermDescriptions() {
        return await this.request('/api/term-descriptions', {
            method: 'GET'
        });
    },

    /**
     * Update custom term descriptions
     */
    async updateTermDescriptions(descriptions) {
        return await this.request('/api/term-descriptions', {
            method: 'POST',
            body: JSON.stringify({ descriptions: descriptions })
        });
    },

    /**
     * Reset term descriptions (all or specific codes)
     */
    async resetTermDescriptions(codes = null) {
        return await this.request('/api/term-descriptions', {
            method: 'DELETE',
            body: JSON.stringify(codes ? { codes: codes } : {})
        });
    }
};

// Prompt Editor
const PromptEditor = {
    /**
     * Initialize prompt editor modal
     */
    init() {
        const editPromptBtn = document.getElementById('edit-prompt-btn');
        const promptModal = document.getElementById('prompt-editor-modal');
        const closeModalBtn = document.getElementById('close-prompt-modal');
        const cancelBtn = document.getElementById('cancel-prompt-btn');
        const saveBtn = document.getElementById('save-prompt-btn');
        const resetBtn = document.getElementById('reset-prompt-btn');
        const promptEditor = document.getElementById('prompt-editor');
        const promptStatus = document.getElementById('prompt-status');

        if (!editPromptBtn || !promptModal) return;

        // Open modal
        editPromptBtn.addEventListener('click', async () => {
            try {
                Utils.showLoading('Loading prompt...');
                const result = await API.getPrompt();
                Utils.hideLoading();

                if (result.success) {
                    promptEditor.value = result.prompt;
                    promptStatus.textContent = result.is_custom ? 'Custom prompt' : 'Default prompt';
                    promptStatus.style.color = result.is_custom ? '#059669' : '#666';
                    promptModal.style.display = 'flex';
                }
            } catch (error) {
                Utils.hideLoading();
                alert('Error loading prompt: ' + error.message);
            }
        });

        // Close modal
        const closeModal = () => {
            promptModal.style.display = 'none';
        };

        closeModalBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);

        // Close modal on background click
        promptModal.addEventListener('click', (e) => {
            if (e.target === promptModal) {
                closeModal();
            }
        });

        // Save prompt
        saveBtn.addEventListener('click', async () => {
            const promptText = promptEditor.value.trim();

            if (!promptText) {
                alert('Prompt cannot be empty');
                return;
            }

            // Validate required placeholders
            const requiredPlaceholders = ['{terms_description}', '{document_text}'];
            const missingPlaceholders = requiredPlaceholders.filter(p => !promptText.includes(p));

            if (missingPlaceholders.length > 0) {
                alert(`Prompt must contain these placeholders:\n${missingPlaceholders.join('\n')}`);
                return;
            }

            try {
                Utils.showLoading('Saving prompt...');
                const result = await API.updatePrompt(promptText);
                Utils.hideLoading();

                if (result.success) {
                    alert('Prompt saved successfully! It will be used for future document processing.');
                    promptStatus.textContent = 'Custom prompt';
                    promptStatus.style.color = '#059669';
                    closeModal();
                }
            } catch (error) {
                Utils.hideLoading();
                alert('Error saving prompt: ' + error.message);
            }
        });

        // Reset to default
        resetBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to reset to the default prompt? This will delete your custom prompt.')) {
                return;
            }

            try {
                Utils.showLoading('Resetting prompt...');
                const result = await API.resetPrompt();
                Utils.hideLoading();

                if (result.success) {
                    // Reload the default prompt
                    const promptResult = await API.getPrompt();
                    if (promptResult.success) {
                        promptEditor.value = promptResult.prompt;
                        promptStatus.textContent = 'Default prompt';
                        promptStatus.style.color = '#666';
                        alert('Prompt reset to default successfully!');
                    }
                }
            } catch (error) {
                Utils.hideLoading();
                alert('Error resetting prompt: ' + error.message);
            }
        });
    }
};

// Term Description Editor
const TermDescriptionEditor = {
    descriptions: [],

    init() {
        const editBtn = document.getElementById('edit-descriptions-btn');
        const modal = document.getElementById('term-descriptions-modal');

        if (!editBtn || !modal) return;

        editBtn.addEventListener('click', () => this.openModal());

        document.getElementById('close-descriptions-modal').addEventListener('click', () => this.closeModal());
        document.getElementById('cancel-descriptions-btn').addEventListener('click', () => this.closeModal());
        document.getElementById('save-descriptions-btn').addEventListener('click', () => this.saveChanges());
        document.getElementById('reset-all-descriptions-btn').addEventListener('click', () => this.resetAll());

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal();
        });

        // Search/filter
        const searchInput = document.getElementById('desc-search');
        if (searchInput) {
            searchInput.addEventListener('input', Utils.debounce(() => {
                this.filterDescriptions(searchInput.value.toLowerCase());
            }, 200));
        }

        const filterSelect = document.getElementById('desc-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', () => {
                this.filterDescriptions(
                    document.getElementById('desc-search')?.value?.toLowerCase() || ''
                );
            });
        }
    },

    async openModal() {
        try {
            Utils.showLoading('Loading term descriptions...');
            const result = await API.getTermDescriptions();
            Utils.hideLoading();

            if (result.success) {
                this.descriptions = result.descriptions;
                this.renderDescriptions();
                document.getElementById('term-descriptions-modal').style.display = 'flex';
            }
        } catch (error) {
            Utils.hideLoading();
            alert('Error loading descriptions: ' + error.message);
        }
    },

    closeModal() {
        document.getElementById('term-descriptions-modal').style.display = 'none';
    },

    renderDescriptions() {
        const container = document.getElementById('desc-list-container');
        container.innerHTML = '';

        const customCount = this.descriptions.filter(d => d.is_custom).length;
        const countEl = document.getElementById('desc-custom-count');
        countEl.textContent = customCount > 0 ? `${customCount} customized` : 'All defaults';
        countEl.style.color = customCount > 0 ? '#059669' : '#666';

        this.descriptions.forEach(desc => {
            const item = document.createElement('div');
            item.className = `desc-item ${desc.is_custom ? 'desc-item-custom' : ''}`;
            item.dataset.code = desc.code;
            item.dataset.type = desc.type;
            item.dataset.isCustom = desc.is_custom;

            item.innerHTML = `
                <div class="desc-item-header">
                    <div class="desc-item-title">
                        <strong>${this.escapeHtml(desc.name)}</strong>
                        <span class="term-code">${this.escapeHtml(desc.code)}</span>
                        ${desc.is_custom ? '<span class="desc-badge-custom">Customized</span>' : ''}
                    </div>
                    <div class="desc-item-actions">
                        ${desc.is_custom ? `<button class="btn-reset-desc" data-code="${this.escapeHtml(desc.code)}" title="Reset to default">Reset</button>` : ''}
                    </div>
                </div>
                <div class="desc-item-type">Type: ${this.escapeHtml(desc.type)}</div>
                ${desc.is_custom ? `<div class="desc-item-default"><em>Default:</em> ${this.escapeHtml(desc.default_description)}</div>` : ''}
                <textarea class="desc-textarea" data-code="${this.escapeHtml(desc.code)}" rows="2">${this.escapeHtml(desc.description)}</textarea>
            `;

            container.appendChild(item);
        });

        // Attach reset handlers
        container.querySelectorAll('.btn-reset-desc').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const code = e.target.dataset.code;
                this.resetSingle(code);
            });
        });

        // Mark textareas that change from their loaded value
        container.querySelectorAll('.desc-textarea').forEach(textarea => {
            const code = textarea.dataset.code;
            const desc = this.descriptions.find(d => d.code === code);
            const loadedValue = desc.description;

            textarea.addEventListener('input', () => {
                if (textarea.value.trim() !== loadedValue) {
                    textarea.classList.add('desc-textarea-modified');
                } else {
                    textarea.classList.remove('desc-textarea-modified');
                }
            });
        });
    },

    filterDescriptions(searchTerm) {
        const filterValue = document.getElementById('desc-filter')?.value || 'all';
        const items = document.querySelectorAll('.desc-item');

        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            const matchesSearch = !searchTerm || text.includes(searchTerm);

            let matchesFilter = true;
            switch (filterValue) {
                case 'custom':
                    matchesFilter = item.dataset.isCustom === 'true';
                    break;
                case 'default':
                    matchesFilter = item.dataset.isCustom !== 'true';
                    break;
            }

            item.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
        });
    },

    async saveChanges() {
        const textareas = document.querySelectorAll('.desc-textarea');
        const updates = {};
        const codesToReset = [];

        textareas.forEach(textarea => {
            const code = textarea.dataset.code;
            const desc = this.descriptions.find(d => d.code === code);
            const newValue = textarea.value.trim();

            if (newValue === desc.default_description) {
                // Changed back to default - reset if it was custom
                if (desc.is_custom) {
                    codesToReset.push(code);
                }
            } else if (newValue && newValue !== desc.description) {
                // Different from current - save as custom
                updates[code] = newValue;
            }
        });

        if (Object.keys(updates).length === 0 && codesToReset.length === 0) {
            alert('No changes to save.');
            return;
        }

        try {
            Utils.showLoading('Saving descriptions...');

            if (codesToReset.length > 0) {
                await API.resetTermDescriptions(codesToReset);
            }

            if (Object.keys(updates).length > 0) {
                await API.updateTermDescriptions(updates);
            }

            Utils.hideLoading();
            alert('Term descriptions saved! Changes will apply to future document processing.');
            this.closeModal();
        } catch (error) {
            Utils.hideLoading();
            alert('Error saving descriptions: ' + error.message);
        }
    },

    async resetAll() {
        if (!confirm('Reset ALL term descriptions to their defaults? This cannot be undone.')) {
            return;
        }

        try {
            Utils.showLoading('Resetting descriptions...');
            await API.resetTermDescriptions();
            Utils.hideLoading();
            await this.openModal();
            alert('All descriptions reset to defaults.');
        } catch (error) {
            Utils.hideLoading();
            alert('Error resetting descriptions: ' + error.message);
        }
    },

    async resetSingle(code) {
        try {
            await API.resetTermDescriptions([code]);
            await this.openModal();
        } catch (error) {
            alert('Error resetting description: ' + error.message);
        }
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('License Uploader initialized');

    // Initialize API configuration inputs
    APIConfig.initializeInputs();

    // Initialize prompt editor
    PromptEditor.init();

    // Initialize term description editor
    TermDescriptionEditor.init();

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utils, API };
}
