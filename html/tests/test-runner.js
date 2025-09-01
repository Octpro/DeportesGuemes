/**
 * Test Runner for Deportes Güemes Store
 * Coordinates and runs all test suites with comprehensive reporting
 */

class TestRunner {
    constructor() {
        this.testSuites = new Map();
        this.overallResults = {
            startTime: null,
            endTime: null,
            totalTests: 0,
            totalPassed: 0,
            totalFailed: 0,
            totalDuration: 0,
            suiteResults: []
        };
        this.setupTestEnvironment();
    }

    setupTestEnvironment() {
        // Create test results container
        this.createTestUI();
        
        // Register test suites
        this.registerTestSuite('unit', UnitTestSuite);
        this.registerTestSuite('integration', IntegrationTestSuite);
        this.registerTestSuite('e2e', E2ETestSuite);
        this.registerTestSuite('visual', VisualRegressionTestSuite);
        
        // Setup error handling
        this.setupErrorHandling();
    }

    createTestUI() {
        // Create test results UI
        const testContainer = document.createElement('div');
        testContainer.id = 'test-runner-container';
        testContainer.innerHTML = `
            <div class="test-runner-header">
                <h2>🧪 Test Runner - Deportes Güemes</h2>
                <div class="test-controls">
                    <button id="run-all-tests" class="btn btn-primary">Run All Tests</button>
                    <button id="run-unit-tests" class="btn btn-secondary">Unit Tests</button>
                    <button id="run-integration-tests" class="btn btn-secondary">Integration Tests</button>
                    <button id="run-e2e-tests" class="btn btn-secondary">E2E Tests</button>
                    <button id="run-visual-tests" class="btn btn-secondary">Visual Tests</button>
                    <button id="clear-results" class="btn btn-outline">Clear Results</button>
                </div>
            </div>
            <div class="test-progress">
                <div class="progress-bar">
                    <div class="progress-fill" id="test-progress-fill"></div>
                </div>
                <div class="progress-text" id="test-progress-text">Ready to run tests</div>
            </div>
            <div class="test-summary" id="test-summary" style="display: none;">
                <div class="summary-stats">
                    <div class="stat-item">
                        <span class="stat-label">Total Tests:</span>
                        <span class="stat-value" id="total-tests">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Passed:</span>
                        <span class="stat-value passed" id="total-passed">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Failed:</span>
                        <span class="stat-value failed" id="total-failed">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Duration:</span>
                        <span class="stat-value" id="total-duration">0ms</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Success Rate:</span>
                        <span class="stat-value" id="success-rate">0%</span>
                    </div>
                </div>
            </div>
            <div class="test-results" id="test-results"></div>
        `;
        
        // Add styles
        const styles = document.createElement('style');
        styles.textContent = `
            #test-runner-container {
                position: fixed;
                top: 0;
                right: 0;
                width: 400px;
                height: 100vh;
                background: white;
                border-left: 2px solid #ddd;
                z-index: 10000;
                overflow-y: auto;
                font-family: monospace;
                font-size: 12px;
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
            }
            
            .test-runner-header {
                padding: 15px;
                background: #f8f9fa;
                border-bottom: 1px solid #ddd;
                position: sticky;
                top: 0;
                z-index: 1;
            }
            
            .test-runner-header h2 {
                margin: 0 0 10px 0;
                font-size: 16px;
                color: #333;
            }
            
            .test-controls {
                display: flex;
                flex-wrap: wrap;
                gap: 5px;
            }
            
            .test-controls button {
                padding: 5px 10px;
                border: 1px solid #ddd;
                background: white;
                cursor: pointer;
                border-radius: 3px;
                font-size: 11px;
            }
            
            .btn-primary { background: #007bff; color: white; border-color: #007bff; }
            .btn-secondary { background: #6c757d; color: white; border-color: #6c757d; }
            .btn-outline { background: transparent; }
            
            .test-progress {
                padding: 15px;
                border-bottom: 1px solid #eee;
            }
            
            .progress-bar {
                width: 100%;
                height: 20px;
                background: #f0f0f0;
                border-radius: 10px;
                overflow: hidden;
                margin-bottom: 10px;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                width: 0%;
                transition: width 0.3s ease;
            }
            
            .progress-text {
                text-align: center;
                font-weight: bold;
                color: #666;
            }
            
            .test-summary {
                padding: 15px;
                background: #f8f9fa;
                border-bottom: 1px solid #eee;
            }
            
            .summary-stats {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }
            
            .stat-item {
                display: flex;
                justify-content: space-between;
                padding: 5px;
                background: white;
                border-radius: 3px;
            }
            
            .stat-value.passed { color: #28a745; font-weight: bold; }
            .stat-value.failed { color: #dc3545; font-weight: bold; }
            
            .test-results {
                padding: 15px;
            }
            
            .test-suite-result {
                margin-bottom: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                overflow: hidden;
            }
            
            .suite-header {
                padding: 10px;
                background: #f8f9fa;
                border-bottom: 1px solid #ddd;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .suite-header.passed { background: #d4edda; }
            .suite-header.failed { background: #f8d7da; }
            
            .suite-details {
                padding: 10px;
                display: none;
            }
            
            .suite-details.expanded { display: block; }
            
            .test-item {
                padding: 5px 10px;
                margin: 2px 0;
                border-radius: 3px;
                display: flex;
                justify-content: space-between;
            }
            
            .test-item.passed { background: #d4edda; }
            .test-item.failed { background: #f8d7da; }
            
            .test-duration {
                color: #666;
                font-size: 10px;
            }
            
            @media (max-width: 768px) {
                #test-runner-container {
                    width: 100%;
                    height: 50vh;
                    top: auto;
                    bottom: 0;
                    right: 0;
                }
            }
        `;
        
        document.head.appendChild(styles);
        document.body.appendChild(testContainer);
        
        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.getElementById('run-all-tests').addEventListener('click', () => this.runAllTests());
        document.getElementById('run-unit-tests').addEventListener('click', () => this.runTestSuite('unit'));
        document.getElementById('run-integration-tests').addEventListener('click', () => this.runTestSuite('integration'));
        document.getElementById('run-e2e-tests').addEventListener('click', () => this.runTestSuite('e2e'));
        document.getElementById('run-visual-tests').addEventListener('click', () => this.runTestSuite('visual'));
        document.getElementById('clear-results').addEventListener('click', () => this.clearResults());
    }

    setupErrorHandling() {
        // Capture uncaught errors during testing
        window.addEventListener('error', (event) => {
            if (this.overallResults.startTime && !this.overallResults.endTime) {
                console.error('Uncaught error during testing:', event.error);
                this.logTestError('Uncaught Error', event.error.message, event.error.stack);
            }
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            if (this.overallResults.startTime && !this.overallResults.endTime) {
                console.error('Unhandled promise rejection during testing:', event.reason);
                this.logTestError('Unhandled Promise Rejection', event.reason);
            }
        });
    }

    registerTestSuite(name, TestSuiteClass) {
        this.testSuites.set(name, TestSuiteClass);
    }

    async runAllTests() {
        console.log('🚀 Starting comprehensive test run...');
        this.overallResults.startTime = Date.now();
        this.updateProgress(0, 'Initializing test run...');
        
        const suiteNames = Array.from(this.testSuites.keys());
        let completedSuites = 0;
        
        try {
            for (const suiteName of suiteNames) {
                this.updateProgress(
                    (completedSuites / suiteNames.length) * 100,
                    `Running ${suiteName} tests...`
                );
                
                await this.runTestSuite(suiteName, false); // Don't update UI for each suite
                completedSuites++;
            }
            
            this.overallResults.endTime = Date.now();
            this.updateProgress(100, 'All tests completed!');
            this.displayOverallResults();
            
        } catch (error) {
            console.error('Test run failed:', error);
            this.updateProgress(100, 'Test run failed with errors');
            this.logTestError('Test Runner Error', error.message, error.stack);
        }
    }

    async runTestSuite(suiteName, updateUI = true) {
        const TestSuiteClass = this.testSuites.get(suiteName);
        if (!TestSuiteClass) {
            console.error(`Test suite '${suiteName}' not found`);
            return;
        }
        
        console.log(`🧪 Running ${suiteName} test suite...`);
        
        if (updateUI) {
            this.updateProgress(0, `Running ${suiteName} tests...`);
        }
        
        try {
            const testSuite = new TestSuiteClass();
            const startTime = Date.now();
            
            // Run the test suite
            await testSuite.runAllTests();
            
            const endTime = Date.now();
            const duration = endTime - startTime;
            
            // Get results from the test suite
            const results = testSuite.testResults || [];
            const passed = results.filter(r => r.status === 'PASS').length;
            const failed = results.filter(r => r.status === 'FAIL').length;
            
            // Store suite results
            const suiteResult = {
                name: suiteName,
                results,
                passed,
                failed,
                total: results.length,
                duration,
                successRate: results.length > 0 ? (passed / results.length) * 100 : 0
            };
            
            this.overallResults.suiteResults.push(suiteResult);
            this.overallResults.totalTests += results.length;
            this.overallResults.totalPassed += passed;
            this.overallResults.totalFailed += failed;
            this.overallResults.totalDuration += duration;
            
            if (updateUI) {
                this.updateProgress(100, `${suiteName} tests completed`);
                this.displaySuiteResult(suiteResult);
                this.displayOverallResults();
            }
            
            console.log(`✅ ${suiteName} test suite completed: ${passed}/${results.length} passed`);
            
        } catch (error) {
            console.error(`❌ ${suiteName} test suite failed:`, error);
            
            const suiteResult = {
                name: suiteName,
                results: [],
                passed: 0,
                failed: 1,
                total: 1,
                duration: 0,
                successRate: 0,
                error: error.message
            };
            
            this.overallResults.suiteResults.push(suiteResult);
            this.overallResults.totalTests += 1;
            this.overallResults.totalFailed += 1;
            
            if (updateUI) {
                this.displaySuiteResult(suiteResult);
                this.displayOverallResults();
            }
        }
    }

    updateProgress(percentage, message) {
        const progressFill = document.getElementById('test-progress-fill');
        const progressText = document.getElementById('test-progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = message;
        }
    }

    displayOverallResults() {
        const summary = document.getElementById('test-summary');
        const totalTests = document.getElementById('total-tests');
        const totalPassed = document.getElementById('total-passed');
        const totalFailed = document.getElementById('total-failed');
        const totalDuration = document.getElementById('total-duration');
        const successRate = document.getElementById('success-rate');
        
        if (summary) {
            summary.style.display = 'block';
        }
        
        if (totalTests) {
            totalTests.textContent = this.overallResults.totalTests;
        }
        
        if (totalPassed) {
            totalPassed.textContent = this.overallResults.totalPassed;
        }
        
        if (totalFailed) {
            totalFailed.textContent = this.overallResults.totalFailed;
        }
        
        if (totalDuration) {
            totalDuration.textContent = `${this.overallResults.totalDuration}ms`;
        }
        
        if (successRate) {
            const rate = this.overallResults.totalTests > 0 ? 
                (this.overallResults.totalPassed / this.overallResults.totalTests) * 100 : 0;
            successRate.textContent = `${rate.toFixed(1)}%`;
        }
    }

    displaySuiteResult(suiteResult) {
        const resultsContainer = document.getElementById('test-results');
        if (!resultsContainer) return;
        
        const suiteDiv = document.createElement('div');
        suiteDiv.className = 'test-suite-result';
        
        const headerClass = suiteResult.failed === 0 ? 'passed' : 'failed';
        const statusIcon = suiteResult.failed === 0 ? '✅' : '❌';
        
        suiteDiv.innerHTML = `
            <div class="suite-header ${headerClass}" onclick="this.nextElementSibling.classList.toggle('expanded')">
                <div>
                    <strong>${statusIcon} ${suiteResult.name.toUpperCase()} Tests</strong>
                    <div style="font-size: 10px; color: #666;">
                        ${suiteResult.passed}/${suiteResult.total} passed (${suiteResult.successRate.toFixed(1)}%)
                    </div>
                </div>
                <div class="test-duration">${suiteResult.duration}ms</div>
            </div>
            <div class="suite-details">
                ${suiteResult.error ? 
                    `<div class="test-item failed">
                        <span>Suite Error: ${suiteResult.error}</span>
                    </div>` :
                    suiteResult.results.map(test => `
                        <div class="test-item ${test.status.toLowerCase()}">
                            <span>${test.status === 'PASS' ? '✅' : '❌'} ${test.name}</span>
                            <span class="test-duration">${test.duration}ms</span>
                        </div>
                        ${test.message ? `<div style="font-size: 10px; color: #666; margin-left: 20px;">${test.message}</div>` : ''}
                    `).join('')
                }
            </div>
        `;
        
        resultsContainer.appendChild(suiteDiv);
    }

    clearResults() {
        const resultsContainer = document.getElementById('test-results');
        const summary = document.getElementById('test-summary');
        
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
        
        if (summary) {
            summary.style.display = 'none';
        }
        
        // Reset overall results
        this.overallResults = {
            startTime: null,
            endTime: null,
            totalTests: 0,
            totalPassed: 0,
            totalFailed: 0,
            totalDuration: 0,
            suiteResults: []
        };
        
        this.updateProgress(0, 'Ready to run tests');
        
        // Clear stored test results
        localStorage.removeItem('unit-test-results');
        localStorage.removeItem('integration-test-results');
        localStorage.removeItem('e2e-test-results');
        localStorage.removeItem('visual-regression-test-results');
        
        console.log('🧹 Test results cleared');
    }

    logTestError(type, message, stack) {
        console.error(`${type}: ${message}`);
        if (stack) {
            console.error(stack);
        }
        
        // Store error for reporting
        const errorLog = {
            type,
            message,
            stack,
            timestamp: new Date().toISOString()
        };
        
        const existingErrors = JSON.parse(localStorage.getItem('test-errors') || '[]');
        existingErrors.push(errorLog);
        localStorage.setItem('test-errors', JSON.stringify(existingErrors));
    }

    generateTestReport() {
        const report = {
            timestamp: new Date().toISOString(),
            overallResults: this.overallResults,
            environment: {
                userAgent: navigator.userAgent,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                },
                url: window.location.href
            },
            errors: JSON.parse(localStorage.getItem('test-errors') || '[]')
        };
        
        // Store comprehensive report
        localStorage.setItem('comprehensive-test-report', JSON.stringify(report));
        
        // Generate downloadable report
        const reportBlob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
        const reportUrl = URL.createObjectURL(reportBlob);
        
        const downloadLink = document.createElement('a');
        downloadLink.href = reportUrl;
        downloadLink.download = `test-report-${new Date().toISOString().split('T')[0]}.json`;
        downloadLink.textContent = 'Download Test Report';
        downloadLink.style.display = 'block';
        downloadLink.style.margin = '10px';
        downloadLink.style.padding = '5px 10px';
        downloadLink.style.background = '#007bff';
        downloadLink.style.color = 'white';
        downloadLink.style.textDecoration = 'none';
        downloadLink.style.borderRadius = '3px';
        
        const resultsContainer = document.getElementById('test-results');
        if (resultsContainer) {
            resultsContainer.insertBefore(downloadLink, resultsContainer.firstChild);
        }
        
        return report;
    }

    // Static method to initialize test runner
    static initialize() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                new TestRunner();
            });
        } else {
            new TestRunner();
        }
    }
}

// Auto-initialize if this script is loaded
if (typeof window !== 'undefined') {
    TestRunner.initialize();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TestRunner;
}