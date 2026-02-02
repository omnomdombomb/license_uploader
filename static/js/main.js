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
            modelSelect.value = config.llm_model;
            modelSelect.addEventListener('change', async (e) => {
                await this.saveConfig({
                    litellm_api_key: config.litellm_api_key,
                    alma_api_key: config.alma_api_key,
                    llm_model: e.target.value
                });
            });
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

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('License Uploader initialized');

    // Initialize API configuration inputs
    APIConfig.initializeInputs();

    // Initialize prompt editor
    PromptEditor.init();

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
