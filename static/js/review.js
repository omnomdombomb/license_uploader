/**
 * License Uploader - Review Page JavaScript
 */

// State management
const ReviewPage = {
    extractedTerms: {},

    /**
     * Initialize the review page
     */
    init() {
        this.initializeDatePickers();
        this.initializeTermFiltering();
        this.initializeRefineButtons();
        // FEATURE DISABLED: Show Source buttons
        // this.initializeShowSourceButtons();
        this.initializeFormValidation();
        this.initializeActionButtons();
        this.loadExtractedTerms();
    },

    /**
     * Initialize Flatpickr date pickers
     */
    initializeDatePickers() {
        const dateInputs = document.querySelectorAll('.date-picker');

        dateInputs.forEach(input => {
            flatpickr(input, {
                dateFormat: 'Y-m-d',
                allowInput: true,
                altInput: true,
                altFormat: 'F j, Y',
                theme: 'light'
            });
        });
    },

    /**
     * Load extracted terms from the page
     */
    loadExtractedTerms() {
        const termCards = document.querySelectorAll('.term-card');

        termCards.forEach(card => {
            const code = card.dataset.code;
            const type = card.dataset.type;
            const input = card.querySelector('.term-input');

            if (input) {
                this.extractedTerms[code] = {
                    type: type,
                    value: input.value || null,
                    element: input
                };
            }
        });
    },

    /**
     * Initialize term filtering and search
     */
    initializeTermFiltering() {
        const searchInput = document.getElementById('term-search');
        const filterSelect = document.getElementById('term-filter');

        if (!searchInput || !filterSelect) return;

        const performFilter = Utils.debounce(() => {
            const searchTerm = searchInput.value.toLowerCase();
            const filterType = filterSelect.value;

            this.filterTerms(searchTerm, filterType);
        }, 300);

        searchInput.addEventListener('input', performFilter);
        filterSelect.addEventListener('change', performFilter);
    },

    /**
     * Filter terms based on search and filter criteria
     */
    filterTerms(searchTerm, filterType) {
        const termCards = document.querySelectorAll('.term-card');

        termCards.forEach(card => {
            const code = card.dataset.code;
            const type = card.dataset.type;
            const hasValue = card.dataset.hasValue === 'true';
            const input = card.querySelector('.term-input');
            const currentValue = input ? input.value.trim() : '';

            // Text search
            const cardText = card.textContent.toLowerCase();
            const matchesSearch = !searchTerm || cardText.includes(searchTerm);

            // Filter by type/status
            let matchesFilter = true;

            switch (filterType) {
                case 'extracted':
                    matchesFilter = currentValue !== '';
                    break;
                case 'empty':
                    matchesFilter = currentValue === '';
                    break;
                case 'yes-no':
                    matchesFilter = type === 'LicenseTermsYesNo';
                    break;
                case 'permitted-prohibited':
                    matchesFilter = type === 'LicenseTermsPermittedProhibited';
                    break;
                case 'all':
                default:
                    matchesFilter = true;
            }

            // Show/hide card
            if (matchesSearch && matchesFilter) {
                card.classList.remove('hidden');
            } else {
                card.classList.add('hidden');
            }
        });
    },

    /**
     * Initialize AI refine buttons
     */
    initializeRefineButtons() {
        const refineButtons = document.querySelectorAll('.btn-refine');

        refineButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                await this.handleRefine(button);
            });
        });
    },

    // FEATURE DISABLED: Show Source functionality
    /*
    /**
     * Initialize Show Source buttons
     *\/
    initializeShowSourceButtons() {
        const showSourceButtons = document.querySelectorAll('.btn-show-source');

        showSourceButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSourceModal(button);
            });
        });
    },

    /**
     * Show source citation modal
     *\/
    showSourceModal(button) {
        const termCode = button.dataset.code;
        const termCard = button.closest('.term-card');

        if (!termCard) return;

        // Get citation and source location from data attributes
        const citation = termCard.dataset.citation;
        const sourceLocationStr = termCard.dataset.sourceLocation;

        // Get term name from card
        const termName = termCard.querySelector('h4').textContent;

        // Parse source location if available
        let sourceLocation = null;
        if (sourceLocationStr) {
            try {
                sourceLocation = JSON.parse(sourceLocationStr);
            } catch (e) {
                console.error('Error parsing source location:', e);
            }
        }

        // Populate modal
        const modal = document.getElementById('source-modal');
        const titleEl = document.getElementById('source-modal-title');
        const pageInfoEl = document.getElementById('source-page-info');
        const contextBeforeEl = document.getElementById('source-context-before');
        const matchedTextEl = document.getElementById('source-matched-text');
        const contextAfterEl = document.getElementById('source-context-after');
        const confidenceInfoEl = document.getElementById('source-confidence-info');

        titleEl.textContent = `Source: ${termName}`;

        if (sourceLocation) {
            // Display page information
            const pageText = sourceLocation.page ? `Page ${sourceLocation.page}` : 'Location in document';
            pageInfoEl.textContent = pageText;
            pageInfoEl.style.display = 'block';

            // Display citation with context
            contextBeforeEl.textContent = sourceLocation.context_before ? `...${sourceLocation.context_before} ` : '';
            matchedTextEl.textContent = sourceLocation.matched_text || citation || '';
            contextAfterEl.textContent = sourceLocation.context_after ? ` ${sourceLocation.context_after}...` : '';

            // Show confidence info if fuzzy matched
            if (sourceLocation.fuzzy_matched) {
                const confidence = Math.round(sourceLocation.match_confidence * 100);
                confidenceInfoEl.textContent = `⚠️ Approximate match (${confidence}% confidence) - The exact text may have been paraphrased by the AI.`;
                confidenceInfoEl.style.display = 'block';
            } else {
                confidenceInfoEl.style.display = 'none';
            }
        } else if (citation) {
            // Only citation available, no source location
            pageInfoEl.textContent = 'Citation from document';
            pageInfoEl.style.display = 'block';

            contextBeforeEl.textContent = '';
            matchedTextEl.textContent = citation;
            contextAfterEl.textContent = '';

            confidenceInfoEl.textContent = 'ℹ️ Citation provided by AI - exact location in document not verified.';
            confidenceInfoEl.style.display = 'block';
        } else {
            // No citation or source location
            pageInfoEl.textContent = 'No source information available';
            pageInfoEl.style.display = 'block';

            contextBeforeEl.textContent = '';
            matchedTextEl.textContent = 'No citation found for this term.';
            contextAfterEl.textContent = '';

            confidenceInfoEl.style.display = 'none';
        }

        // Show modal
        modal.style.display = 'block';

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    },
    */

    /**
     * Handle AI refinement of a term
     */
    async handleRefine(button) {
        const termCode = button.dataset.code;
        const termCard = button.closest('.term-card');
        const input = termCard.querySelector('.term-input');

        if (!input) return;

        const currentValue = input.value.trim();

        // Disable button
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.innerHTML = '<div class="spinner" style="width: 20px; height: 20px; margin: 0;"></div>';

        try {
            Utils.showLoading('Refining term with AI...');

            const result = await API.refineTerm(termCode, currentValue);

            if (result.success && result.value !== null) {
                input.value = result.value;
                input.style.backgroundColor = '#fef3c7'; // Highlight changed value

                // Update extracted terms
                this.extractedTerms[termCode].value = result.value;

                // Reset highlight after 2 seconds
                setTimeout(() => {
                    input.style.backgroundColor = '';
                }, 2000);
            } else if (result.value === null) {
                alert('AI could not extract a value for this term from the document.');
            }
        } catch (error) {
            alert('Error refining term: ' + error.message);
        } finally {
            Utils.hideLoading();
            button.disabled = false;
            button.innerHTML = originalHTML;
        }
    },

    /**
     * Initialize form validation
     */
    initializeFormValidation() {
        // Real-time validation for required fields
        const requiredFields = [
            'license-code',
            'license-name',
            'license-type',
            'license-status'
        ];

        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => {
                    if (!field.value.trim()) {
                        field.style.borderColor = 'var(--danger-color)';
                    } else {
                        field.style.borderColor = '';
                    }
                });

                field.addEventListener('input', () => {
                    if (field.value.trim()) {
                        field.style.borderColor = '';
                    }
                });
            }
        });
    },

    /**
     * Initialize action buttons
     */
    initializeActionButtons() {
        const cancelBtn = document.getElementById('cancel-btn');
        const validateBtn = document.getElementById('validate-btn');
        const submitBtn = document.getElementById('submit-btn');

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                if (confirm('Are you sure you want to cancel? All unsaved changes will be lost.')) {
                    window.location.href = '/';
                }
            });
        }

        if (validateBtn) {
            validateBtn.addEventListener('click', () => this.validateForm());
        }

        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitLicense());
        }
    },

    /**
     * Validate the form
     */
    validateForm() {
        const statusMsg = document.getElementById('status-msg');

        const requiredFields = [
            { id: 'license-code', name: 'License Code' },
            { id: 'license-name', name: 'License Name' },
            { id: 'license-type', name: 'Type' },
            { id: 'license-status', name: 'Status' }
        ];

        const errors = Utils.validateRequired(requiredFields);

        if (errors.length > 0) {
            Utils.showMessage(
                statusMsg,
                `Please fill in required fields: ${errors.join(', ')}`,
                'error'
            );
            return false;
        }

        // Validate dates
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);

            if (end < start) {
                Utils.showMessage(
                    statusMsg,
                    'End date must be after start date',
                    'error'
                );
                return false;
            }
        }

        Utils.showMessage(
            statusMsg,
            'Validation successful! You can now submit to Alma.',
            'success'
        );

        return true;
    },

    /**
     * Collect form data
     */
    collectFormData() {
        // Basic information
        const basicInfo = {
            code: document.getElementById('license-code').value.trim(),
            name: document.getElementById('license-name').value.trim(),
            type: document.getElementById('license-type').value,
            status: document.getElementById('license-status').value,
            review_status: document.getElementById('review-status').value,
            vendor_code: document.getElementById('vendor').value || null,
            start_date: document.getElementById('start-date').value || null,
            end_date: document.getElementById('end-date').value || null
        };

        // Collect all terms
        const terms = {};
        const termCards = document.querySelectorAll('.term-card');

        termCards.forEach(card => {
            const code = card.dataset.code;
            const type = card.dataset.type;
            const input = card.querySelector('.term-input');

            if (input) {
                const value = input.value.trim();
                terms[code] = {
                    value: value || null,
                    type: type
                };
            }
        });

        return { basic_info: basicInfo, terms: terms };
    },

    /**
     * Submit license to Alma
     */
    async submitLicense() {
        const statusMsg = document.getElementById('status-msg');

        // Validate first
        if (!this.validateForm()) {
            return;
        }

        // Confirm submission
        const confirmed = confirm(
            'Are you ready to submit this license to Alma/PrimoVE?\n\n' +
            'Please verify all information is correct before proceeding.'
        );

        if (!confirmed) return;

        try {
            Utils.showLoading('Submitting license to Alma...');

            const licenseData = this.collectFormData();
            const result = await API.submitLicense(licenseData);

            if (result.success) {
                Utils.hideLoading();

                // Show success message
                const message = `License created successfully!\nLicense Code: ${result.license_code}`;
                alert(message);

                // Redirect to home
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                throw new Error(result.message || 'Submission failed');
            }
        } catch (error) {
            Utils.hideLoading();
            Utils.showMessage(
                statusMsg,
                'Error submitting license: ' + error.message,
                'error'
            );
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    ReviewPage.init();
});
