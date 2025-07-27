// SIP Calculator Dashboard JavaScript with Fixed Input Field Synchronization

class SIPCalculator {
    constructor() {
        this.currentMode = 'sip';
        this.currentTheme = 'light';
        this.chart = null;
        this.debounceTimer = null;
        
        // Initialize default values
        this.values = {
            monthlyInvestment: 25000,
            expectedReturn: 12,
            timePeriod: 10
        };

        // Define ranges for validation
        this.ranges = {
            monthlyInvestment: { min: 500, max: 100000, step: 500 },
            expectedReturn: { min: 1, max: 25, step: 0.5 },
            timePeriod: { min: 1, max: 50, step: 1 }
        };

        this.init();
    }

    init() {
        this.initializeElements();
        this.bindEvents();
        this.initializeTheme();
        this.updateAllDisplays();
        this.calculate();
        this.initChart();
    }

    initializeElements() {
        // Sliders
        this.monthlyInvestmentSlider = document.getElementById('monthlyInvestment');
        this.expectedReturnSlider = document.getElementById('expectedReturn');
        this.timePeriodSlider = document.getElementById('timePeriod');

        // Input fields
        this.monthlyInvestmentInput = document.getElementById('monthlyInvestmentInput');
        this.expectedReturnInput = document.getElementById('expectedReturnInput');
        this.timePeriodInput = document.getElementById('timePeriodInput');

        // Value displays
        this.investmentValueDisplay = document.getElementById('investmentValue');
        this.returnValueDisplay = document.getElementById('returnValue');
        this.periodValueDisplay = document.getElementById('periodValue');

        // Result displays
        this.totalInvestedDisplay = document.getElementById('totalInvested');
        this.estimatedReturnsDisplay = document.getElementById('estimatedReturns');
        this.totalValueDisplay = document.getElementById('totalValue');

        // Controls
        this.modeButtons = document.querySelectorAll('.mode-btn');
        this.themeToggle = document.getElementById('themeToggle');
        this.investButton = document.querySelector('.invest-btn');
        this.loadingIndicator = document.getElementById('loadingIndicator');

        // Labels
        this.investmentLabel = document.getElementById('investmentLabel');
    }

    bindEvents() {
        // Slider events
        this.monthlyInvestmentSlider.addEventListener('input', () => {
            this.values.monthlyInvestment = parseFloat(this.monthlyInvestmentSlider.value);
            this.syncInputFromSlider('monthlyInvestment');
            this.debounceCalculation();
        });

        this.expectedReturnSlider.addEventListener('input', () => {
            this.values.expectedReturn = parseFloat(this.expectedReturnSlider.value);
            this.syncInputFromSlider('expectedReturn');
            this.debounceCalculation();
        });

        this.timePeriodSlider.addEventListener('input', () => {
            this.values.timePeriod = parseFloat(this.timePeriodSlider.value);
            this.syncInputFromSlider('timePeriod');
            this.debounceCalculation();
        });

        // Input field change events (when user types)
        this.monthlyInvestmentInput.addEventListener('input', (e) => {
            this.handleInputChange('monthlyInvestment', e.target.value);
        });

        this.expectedReturnInput.addEventListener('input', (e) => {
            this.handleInputChange('expectedReturn', e.target.value);
        });

        this.timePeriodInput.addEventListener('input', (e) => {
            this.handleInputChange('timePeriod', e.target.value);
        });

        // Input field blur events (when user finishes editing)
        this.monthlyInvestmentInput.addEventListener('blur', () => {
            this.validateAndFormatInput('monthlyInvestment');
        });

        this.expectedReturnInput.addEventListener('blur', () => {
            this.validateAndFormatInput('expectedReturn');
        });

        this.timePeriodInput.addEventListener('blur', () => {
            this.validateAndFormatInput('timePeriod');
        });

        // Focus events to clear invalid styling
        this.monthlyInvestmentInput.addEventListener('focus', () => {
            this.monthlyInvestmentInput.classList.remove('error');
        });

        this.expectedReturnInput.addEventListener('focus', () => {
            this.expectedReturnInput.classList.remove('error');
        });

        this.timePeriodInput.addEventListener('focus', () => {
            this.timePeriodInput.classList.remove('error');
        });

        // Mode toggle events
        this.modeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchMode(e.target.dataset.mode);
            });
        });

        // Theme toggle event
        this.themeToggle.addEventListener('click', this.toggleTheme.bind(this));

        // Invest button event
        this.investButton.addEventListener('click', this.handleInvestClick.bind(this));

        // Keyboard accessibility for sliders
        [this.monthlyInvestmentSlider, this.expectedReturnSlider, this.timePeriodSlider].forEach(slider => {
            slider.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft' || e.key === 'ArrowRight' || e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                    setTimeout(() => this.debounceCalculation(), 10);
                }
            });
        });
    }

    handleInputChange(type, inputValue) {
        const inputElement = this[`${type}Input`];
        let value = this.parseInputValue(inputValue, type);
        
        if (!isNaN(value) && this.isValueInRange(value, type)) {
            // Valid input - update internal value and sync slider
            this.values[type] = value;
            this.syncSliderFromInput(type);
            this.debounceCalculation();
            inputElement.classList.remove('error');
        } else if (inputValue.trim() === '') {
            // Empty input - don't show error, just don't update
            inputElement.classList.remove('error');
        } else {
            // Invalid input - show error styling but don't update values
            inputElement.classList.add('error');
        }
    }

    parseInputValue(inputValue, type) {
        // Remove currency symbols, percentage signs, and other non-numeric characters
        let cleanValue = inputValue.replace(/[₹,%\s]/g, '');
        let numValue = parseFloat(cleanValue);
        
        // For expectedReturn, also handle if user types just the number without %
        if (type === 'expectedReturn' && !isNaN(numValue)) {
            return numValue;
        }
        
        return numValue;
    }

    isValueInRange(value, type) {
        const range = this.ranges[type];
        return value >= range.min && value <= range.max;
    }

    validateAndFormatInput(type) {
        const inputElement = this[`${type}Input`];
        let value = this.parseInputValue(inputElement.value, type);
        
        if (isNaN(value) || !this.isValueInRange(value, type)) {
            // Invalid input - reset to current valid value
            value = this.values[type];
            inputElement.classList.remove('error');
        } else {
            // Valid input - round to step if needed and update internal value
            const range = this.ranges[type];
            value = Math.round(value / range.step) * range.step;
            
            // Ensure value stays within bounds after rounding
            value = Math.max(range.min, Math.min(range.max, value));
            
            this.values[type] = value;
            this.syncSliderFromInput(type);
        }
        
        // Format and update input field with clean value
        this.formatInputField(type, value);
        inputElement.classList.remove('error');
        this.updateDisplayValues();
        this.calculate();
    }

    formatInputField(type, value) {
        const inputElement = this[`${type}Input`];
        
        switch (type) {
            case 'monthlyInvestment':
                inputElement.value = Math.round(value).toString();
                break;
            case 'expectedReturn':
                inputElement.value = value.toString();
                break;
            case 'timePeriod':
                inputElement.value = Math.round(value).toString();
                break;
        }
    }

    syncInputFromSlider(type) {
        this.formatInputField(type, this.values[type]);
        this.updateDisplayValues();
    }

    syncSliderFromInput(type) {
        const sliderElement = this[`${type}Slider`];
        sliderElement.value = this.values[type];
        this.updateDisplayValues();
    }

    updateAllDisplays() {
        this.updateDisplayValues();
        this.formatInputField('monthlyInvestment', this.values.monthlyInvestment);
        this.formatInputField('expectedReturn', this.values.expectedReturn);
        this.formatInputField('timePeriod', this.values.timePeriod);
    }

    debounceCalculation() {
        this.showLoading();
        
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.updateDisplayValues();
            this.calculate();
            this.hideLoading();
        }, 150);
    }

    updateDisplayValues() {
        this.investmentValueDisplay.textContent = this.formatCurrency(this.values.monthlyInvestment);
        this.returnValueDisplay.textContent = `${this.values.expectedReturn}%`;
        this.periodValueDisplay.textContent = `${this.values.timePeriod} Year${this.values.timePeriod !== 1 ? 's' : ''}`;
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        // Update active button
        this.modeButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.mode === mode);
        });

        // Update labels
        if (mode === 'sip') {
            this.investmentLabel.textContent = 'Monthly Investment';
        } else {
            this.investmentLabel.textContent = 'Lumpsum Amount';
        }

        // Recalculate
        this.calculate();
    }

    calculate() {
        const { monthlyInvestment, expectedReturn, timePeriod } = this.values;
        
        let totalInvested, estimatedReturns, totalValue;

        if (this.currentMode === 'sip') {
            // SIP Calculation: FV = P × ({[1 + i]^n – 1} / i) × (1 + i)
            const monthlyRate = expectedReturn / 100 / 12;
            const totalMonths = timePeriod * 12;
            
            if (monthlyRate === 0) {
                // Handle 0% return case
                totalValue = monthlyInvestment * totalMonths;
                estimatedReturns = 0;
            } else {
                totalValue = monthlyInvestment * (((Math.pow(1 + monthlyRate, totalMonths) - 1) / monthlyRate) * (1 + monthlyRate));
                estimatedReturns = totalValue - (monthlyInvestment * totalMonths);
            }
            
            totalInvested = monthlyInvestment * totalMonths;
        } else {
            // Lumpsum Calculation: FV = PV × (1 + r)^n
            totalInvested = monthlyInvestment;
            totalValue = monthlyInvestment * Math.pow(1 + expectedReturn / 100, timePeriod);
            estimatedReturns = totalValue - totalInvested;
        }

        // Update displays
        this.totalInvestedDisplay.textContent = this.formatCurrency(Math.round(totalInvested));
        this.estimatedReturnsDisplay.textContent = this.formatCurrency(Math.round(estimatedReturns));
        this.totalValueDisplay.textContent = this.formatCurrency(Math.round(totalValue));

        // Update chart
        this.updateChart(Math.round(totalInvested), Math.round(estimatedReturns));
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    }

    initChart() {
        const ctx = document.getElementById('investmentChart').getContext('2d');
        
        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Total Invested', 'Estimated Returns'],
                datasets: [{
                    data: [3000000, 2600897],
                    backgroundColor: ['#1FB8CD', '#FFC185'],
                    borderWidth: 0,
                    cutout: '60%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#1FB8CD',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            label: (context) => {
                                const value = this.formatCurrency(context.raw);
                                return `${context.label}: ${value}`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 1000,
                    easing: 'easeOutQuart'
                },
                interaction: {
                    intersect: false,
                    mode: 'nearest'
                }
            }
        });
    }

    updateChart(totalInvested, estimatedReturns) {
        if (this.chart) {
            this.chart.data.datasets[0].data = [totalInvested, Math.max(0, estimatedReturns)];
            this.chart.update('none'); // No animation for real-time updates
        }
    }

    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('hidden');
    }

    initializeTheme() {
        // Initialize with system preference
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.currentTheme = systemPrefersDark ? 'dark' : 'light';
        
        this.applyTheme(this.currentTheme);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.currentTheme = e.matches ? 'dark' : 'light';
            this.applyTheme(this.currentTheme);
        });
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(this.currentTheme);
    }

    applyTheme(theme) {
        // Apply theme to document
        document.documentElement.setAttribute('data-color-scheme', theme);
        
        // Update theme toggle icon
        const themeIcon = this.themeToggle.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
        
        // Update chart colors if needed
        if (this.chart) {
            this.chart.update('none');
        }
    }

    handleInvestClick() {
        // Add click animation
        this.investButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.investButton.style.transform = '';
        }, 150);

        // Show success message
        this.showInvestmentModal();
    }

    showInvestmentModal() {
        // Create a simple modal for demonstration
        const modal = document.createElement('div');
        modal.className = 'investment-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Ready to Invest? 🚀</h3>
                    <button class="modal-close" aria-label="Close modal">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Your investment plan:</p>
                    <div class="investment-summary">
                        <div class="summary-item">
                            <span>Mode:</span>
                            <strong>${this.currentMode.toUpperCase()}</strong>
                        </div>
                        <div class="summary-item">
                            <span>${this.currentMode === 'sip' ? 'Monthly' : 'Lumpsum'} Investment:</span>
                            <strong>${this.formatCurrency(this.values.monthlyInvestment)}</strong>
                        </div>
                        <div class="summary-item">
                            <span>Expected Return:</span>
                            <strong>${this.values.expectedReturn}% p.a.</strong>
                        </div>
                        <div class="summary-item">
                            <span>Time Period:</span>
                            <strong>${this.values.timePeriod} years</strong>
                        </div>
                        <div class="summary-item total">
                            <span>Target Value:</span>
                            <strong>${this.totalValueDisplay.textContent}</strong>
                        </div>
                    </div>
                    <p class="modal-disclaimer">
                        This is a demo calculator. In a real application, you would be redirected to complete your investment.
                    </p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn--secondary modal-cancel">Cancel</button>
                    <button class="btn btn--primary modal-proceed">Proceed to Invest</button>
                </div>
            </div>
        `;

        // Add modal styles
        const modalStyles = document.createElement('style');
        modalStyles.textContent = `
            .investment-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: modalFadeIn 0.3s ease-out;
            }
            
            .modal-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            
            .modal-content {
                position: relative;
                background: var(--color-surface);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-lg);
                max-width: 500px;
                width: 90%;
                max-height: 90vh;
                overflow: auto;
                animation: modalSlideIn 0.3s ease-out;
            }
            
            .modal-header {
                padding: var(--space-20);
                border-bottom: 1px solid var(--color-border);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                margin: 0;
                color: var(--color-text);
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: var(--font-size-2xl);
                cursor: pointer;
                color: var(--color-text-secondary);
                padding: var(--space-4);
                border-radius: var(--radius-sm);
                line-height: 1;
            }
            
            .modal-close:hover {
                background: var(--color-secondary);
            }
            
            .modal-body {
                padding: var(--space-20);
            }
            
            .investment-summary {
                background: var(--color-bg-1);
                border-radius: var(--radius-base);
                padding: var(--space-16);
                margin: var(--space-16) 0;
            }
            
            .summary-item {
                display: flex;
                justify-content: space-between;
                padding: var(--space-8) 0;
                border-bottom: 1px solid var(--color-border);
            }
            
            .summary-item:last-child {
                border-bottom: none;
            }
            
            .summary-item.total {
                font-size: var(--font-size-lg);
                font-weight: var(--font-weight-bold);
                color: var(--color-primary);
                margin-top: var(--space-8);
                padding-top: var(--space-12);
                border-top: 2px solid var(--color-primary);
            }
            
            .modal-disclaimer {
                font-size: var(--font-size-sm);
                color: var(--color-text-secondary);
                font-style: italic;
                margin-top: var(--space-16);
            }
            
            .modal-footer {
                padding: var(--space-20);
                border-top: 1px solid var(--color-border);
                display: flex;
                gap: var(--space-12);
                justify-content: flex-end;
            }
            
            @keyframes modalFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes modalSlideIn {
                from { 
                    opacity: 0;
                    transform: translateY(-20px) scale(0.95);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
        `;

        document.head.appendChild(modalStyles);
        document.body.appendChild(modal);

        // Add event listeners
        const closeBtn = modal.querySelector('.modal-close');
        const cancelBtn = modal.querySelector('.modal-cancel');
        const proceedBtn = modal.querySelector('.modal-proceed');
        const backdrop = modal.querySelector('.modal-backdrop');

        const closeModal = () => {
            modal.style.animation = 'modalFadeIn 0.2s ease-in reverse';
            setTimeout(() => {
                if (document.body.contains(modal)) {
                    document.body.removeChild(modal);
                }
                if (document.head.contains(modalStyles)) {
                    document.head.removeChild(modalStyles);
                }
            }, 200);
        };

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        backdrop.addEventListener('click', closeModal);
        
        proceedBtn.addEventListener('click', () => {
            alert('Thank you for your interest! This is a demo application.');
            closeModal();
        });

        // Close on Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }
}

// Initialize the calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SIPCalculator();
});

// Add some additional utility functions for enhanced UX
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scroll behavior for any anchor links
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add focus indicators for better accessibility
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', () => {
        document.body.classList.remove('keyboard-navigation');
    });
    
    // Add additional keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Alt + T for theme toggle
        if (e.altKey && e.key === 't') {
            document.getElementById('themeToggle').click();
        }
        
        // Alt + S for SIP mode
        if (e.altKey && e.key === 's') {
            document.querySelector('[data-mode="sip"]').click();
        }
        
        // Alt + L for Lumpsum mode
        if (e.altKey && e.key === 'l') {
            document.querySelector('[data-mode="lumpsum"]').click();
        }
    });
});

// Add performance monitoring for debugging
if (window.performance && window.performance.mark) {
    window.performance.mark('sip-calculator-start');
    
    window.addEventListener('load', () => {
        window.performance.mark('sip-calculator-end');
        window.performance.measure('sip-calculator-load', 'sip-calculator-start', 'sip-calculator-end');
        
        const measure = window.performance.getEntriesByName('sip-calculator-load')[0];
        console.log(`SIP Calculator loaded in ${measure.duration.toFixed(2)}ms`);
    });
}