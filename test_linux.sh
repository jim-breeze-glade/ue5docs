#!/bin/bash

# ==============================================================================
# UE5 Documentation Scraper - Test Script (Linux/Unix)
# This script runs comprehensive tests to validate the installation and setup
# ==============================================================================

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/test_results.log"
readonly VENV_DIR="${SCRIPT_DIR}/venv"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_EXIT_CODE=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" >> "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1" >> "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "${LOG_FILE}"
}

# Test result functions
test_passed() {
    local test_name="$1"
    log_success "${test_name}: PASSED"
    ((TESTS_PASSED++))
}

test_failed() {
    local test_name="$1"
    local exit_code="${2:-1}"
    log_error "${test_name}: FAILED (Exit code: ${exit_code})"
    ((TESTS_FAILED++))
    TOTAL_EXIT_CODE=1
}

test_warning() {
    local test_name="$1"
    local message="$2"
    log_warning "${test_name}: ${message}"
}

# Error handling
cleanup_on_error() {
    local exit_code=$?
    log_error "Testing failed with exit code: ${exit_code}"
    echo
    echo "Testing was interrupted. Check the log file for details: ${LOG_FILE}"
    exit "${exit_code}"
}

trap cleanup_on_error ERR

# Display banner
display_banner() {
    echo
    echo "==============================================================================="
    echo "                 UE5 Documentation Scraper - Testing"
    echo "==============================================================================="
    echo
}

# Initialize testing
initialize_testing() {
    cd "${SCRIPT_DIR}"
    
    # Initialize log file
    echo "===============================================================================" > "${LOG_FILE}"
    echo "UE5 Documentation Scraper Test Results - $(date)" >> "${LOG_FILE}"
    echo "===============================================================================" >> "${LOG_FILE}"
    
    log_info "Starting test suite..."
    log_info "Script directory: ${SCRIPT_DIR}"
    log_info "Log file: ${LOG_FILE}"
}

# Test 1: Virtual environment validation
test_virtual_environment() {
    log_info "[1/4] Testing virtual environment..."
    
    if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
        test_failed "Virtual Environment Check"
        log_error "Virtual environment not found at: ${VENV_DIR}/bin/activate"
        log_error "Please run setup script first"
        return 1
    fi
    
    # Try to activate virtual environment
    # shellcheck source=/dev/null
    if source "${VENV_DIR}/bin/activate"; then
        # Verify Python is available
        if command -v python &> /dev/null; then
            local python_version
            python_version=$(python --version 2>&1)
            test_passed "Virtual Environment Check"
            log_info "Python version: ${python_version}"
            
            # Keep environment activated for subsequent tests
            return 0
        else
            test_failed "Virtual Environment Check"
            log_error "Python not available in virtual environment"
            return 1
        fi
    else
        test_failed "Virtual Environment Check"
        log_error "Failed to activate virtual environment"
        return 1
    fi
}

# Test 2: Python test files
test_python_scripts() {
    log_info "[2/4] Testing Python test scripts..."
    
    local test_files=("test_setup.py" "test_scraper.py")
    local tests_run=0
    
    for test_file in "${test_files[@]}"; do
        if [[ -f "${test_file}" ]]; then
            log_info "Running ${test_file}..."
            
            if python "${test_file}"; then
                test_passed "${test_file}"
                ((tests_run++))
            else
                local exit_code=$?
                test_failed "${test_file}" "${exit_code}"
                ((tests_run++))
            fi
        else
            test_warning "${test_file}" "File not found, skipping"
        fi
    done
    
    if [[ ${tests_run} -eq 0 ]]; then
        test_warning "Python Test Scripts" "No Python test files found"
    fi
}

# Test 3: Dependency validation
test_dependencies() {
    log_info "[3/4] Testing Python dependencies..."
    
    local packages=("requests" "beautifulsoup4" "selenium" "lxml" "aiohttp" "fake_useragent")
    local failed_packages=()
    local optional_packages=("weasyprint")  # Optional packages that might not be in all environments
    
    log_info "Checking required packages..."
    for package in "${packages[@]}"; do
        if python -c "import ${package}" 2>/dev/null; then
            log_info "  ✓ ${package}"
        else
            log_warning "  ✗ ${package} - import failed"
            failed_packages+=("${package}")
        fi
    done
    
    log_info "Checking optional packages..."
    for package in "${optional_packages[@]}"; do
        if python -c "import ${package}" 2>/dev/null; then
            log_info "  ✓ ${package} (optional)"
        else
            log_info "  - ${package} (optional) - not available"
        fi
    done
    
    if [[ ${#failed_packages[@]} -eq 0 ]]; then
        test_passed "Dependency Validation"
    else
        test_failed "Dependency Validation"
        log_error "Missing required packages: ${failed_packages[*]}"
    fi
}

# Test 4: System dependencies
test_system_dependencies() {
    log_info "[4/4] Testing system dependencies..."
    
    local tools=("chromium" "google-chrome" "firefox")
    local found_browser=false
    
    log_info "Checking for web browsers..."
    for tool in "${tools[@]}"; do
        if command -v "${tool}" &> /dev/null; then
            log_info "  ✓ ${tool} found"
            found_browser=true
        else
            log_info "  - ${tool} not found"
        fi
    done
    
    if [[ "${found_browser}" == true ]]; then
        test_passed "Browser Check"
    else
        test_warning "Browser Check" "No supported browsers found (chromium, chrome, firefox)"
    fi
    
    # Check for other optional tools
    local optional_tools=("wkhtmltopdf")
    for tool in "${optional_tools[@]}"; do
        if command -v "${tool}" &> /dev/null; then
            log_info "  ✓ ${tool} (optional) found"
        else
            log_info "  - ${tool} (optional) not found"
        fi
    done
    
    test_passed "System Dependencies Check"
}

# Display final results
display_results() {
    echo
    echo "==============================================================================="
    if [[ ${TOTAL_EXIT_CODE} -eq 0 ]]; then
        echo -e "${GREEN}                   TESTING COMPLETED SUCCESSFULLY${NC}"
    else
        echo -e "${RED}                   TESTING COMPLETED WITH FAILURES${NC}"
    fi
    echo "==============================================================================="
    echo
    echo "Test Summary:"
    echo "  Tests Passed: ${TESTS_PASSED}"
    echo "  Tests Failed: ${TESTS_FAILED}"
    local total_tests=$((TESTS_PASSED + TESTS_FAILED))
    echo "  Total Tests:  ${total_tests}"
    echo
    echo "Log file: ${LOG_FILE}"
    echo
    
    # Log final summary
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Test Summary: ${TESTS_PASSED} passed, ${TESTS_FAILED} failed" >> "${LOG_FILE}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Testing completed with exit code: ${TOTAL_EXIT_CODE}" >> "${LOG_FILE}"
    
    if [[ ${TOTAL_EXIT_CODE} -ne 0 ]]; then
        echo -e "${YELLOW}RECOMMENDATION:${NC} Run setup script to fix any missing dependencies"
        echo "  ./setup_arch.sh (for Arch Linux)"
        echo
    fi
}

# Main execution
main() {
    display_banner
    initialize_testing
    
    # Run tests in sequence
    if test_virtual_environment; then
        test_python_scripts
        test_dependencies
        test_system_dependencies
        
        # Deactivate virtual environment
        if command -v deactivate &> /dev/null; then
            deactivate
        fi
    else
        log_error "Cannot continue testing without valid virtual environment"
        TOTAL_EXIT_CODE=1
    fi
    
    display_results
    exit ${TOTAL_EXIT_CODE}
}

# Execute main function
main "$@"