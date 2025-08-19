#!/bin/bash

# ==============================================================================
# UE5 Documentation Scraper - Run Script (Linux/Unix)
# This script activates the virtual environment and runs the UE5 docs scraper
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
readonly LOG_FILE="${SCRIPT_DIR}/scraper.log"
readonly VENV_DIR="${SCRIPT_DIR}/venv"
readonly MAIN_SCRIPT="${SCRIPT_DIR}/ue5_docs_scraper.py"

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

# Error handling
cleanup_on_error() {
    local exit_code=$?
    log_error "Scraper execution failed with exit code: ${exit_code}"
    exit "${exit_code}"
}

trap cleanup_on_error ERR

# Display banner
display_banner() {
    echo
    echo "==============================================================================="
    echo "                    UE5 Documentation Scraper"
    echo "==============================================================================="
    echo
}

# Validate environment
validate_environment() {
    log_info "Validating environment..."
    
    # Change to script directory
    cd "${SCRIPT_DIR}"
    
    # Check if virtual environment exists
    if [[ ! -f "${VENV_DIR}/bin/activate" ]]; then
        log_error "Virtual environment not found!"
        log_error "Expected location: ${VENV_DIR}/bin/activate"
        echo
        echo "Please run the setup script first:"
        echo "  ./setup_arch.sh    (for Arch Linux)"
        echo "  or manually create the virtual environment"
        exit 1
    fi
    
    # Check if main script exists
    if [[ ! -f "${MAIN_SCRIPT}" ]]; then
        log_error "Main scraper script not found!"
        log_error "Expected location: ${MAIN_SCRIPT}"
        echo "Please ensure all files are in the correct directory."
        exit 1
    fi
    
    log_success "Environment validation passed"
}

# Activate virtual environment
activate_virtual_environment() {
    log_info "Activating virtual environment..."
    
    # shellcheck source=/dev/null
    source "${VENV_DIR}/bin/activate" || {
        log_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Verify Python is available
    if ! command -v python &> /dev/null; then
        log_error "Python not available in virtual environment"
        exit 1
    fi
    
    local python_version
    python_version=$(python --version 2>&1)
    log_success "Virtual environment activated"
    log_info "Using: ${python_version}"
}

# Check dependencies
check_dependencies() {
    log_info "Checking critical dependencies..."
    
    local packages=("requests" "beautifulsoup4" "selenium" "lxml" "aiohttp")
    local missing_packages=()
    
    for package in "${packages[@]}"; do
        if python -c "import ${package}" 2>/dev/null; then
            log_info "  ✓ ${package}"
        else
            log_warning "  ✗ ${package} - missing or failed to import"
            missing_packages+=("${package}")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        log_warning "Missing dependencies: ${missing_packages[*]}"
        log_warning "Run setup script to install missing dependencies"
        echo
        read -p "Continue anyway? [y/N]: " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Execution cancelled by user"
            exit 0
        fi
    else
        log_success "All critical dependencies verified"
    fi
}

# Run the scraper
run_scraper() {
    log_info "Starting UE5 Documentation Scraper..."
    echo
    echo "Script location: ${MAIN_SCRIPT}"
    echo "Log file: ${LOG_FILE}"
    echo "Press Ctrl+C to stop the scraper at any time."
    echo
    
    # Run the main script and capture exit code
    python "${MAIN_SCRIPT}"
    local scraper_exit_code=$?
    
    # Log completion status
    if [[ ${scraper_exit_code} -eq 0 ]]; then
        log_success "Scraper completed successfully"
    else
        log_error "Scraper exited with error code ${scraper_exit_code}"
    fi
    
    return ${scraper_exit_code}
}

# Display results
display_results() {
    local exit_code=$1
    
    echo
    echo "==============================================================================="
    if [[ ${exit_code} -eq 0 ]]; then
        echo -e "${GREEN}                   SCRAPING COMPLETED SUCCESSFULLY${NC}"
    else
        echo -e "${RED}                   SCRAPING COMPLETED WITH ERRORS${NC}"
        echo "                   Exit Code: ${exit_code}"
    fi
    echo "==============================================================================="
    echo
    echo "Output locations:"
    echo "  - Downloaded PDFs: ue5_docs folder"
    echo "  - Detailed logs: ${LOG_FILE}"
    echo "  - Script directory: ${SCRIPT_DIR}"
    echo
    
    # Check output directory and show file count
    if [[ -d "ue5_docs" ]]; then
        local pdf_count
        pdf_count=$(find ue5_docs -name "*.pdf" -type f 2>/dev/null | wc -l)
        echo "Downloaded PDF files: ${pdf_count}"
    else
        echo "Note: ue5_docs folder not found - no PDFs were downloaded"
    fi
    
    echo
}

# Main execution
main() {
    display_banner
    
    # Initialize log
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting UE5 Documentation Scraper" >> "${LOG_FILE}"
    echo "===============================================================================" >> "${LOG_FILE}"
    
    validate_environment
    activate_virtual_environment
    check_dependencies
    
    local scraper_exit_code=0
    if run_scraper; then
        scraper_exit_code=0
    else
        scraper_exit_code=$?
    fi
    
    display_results ${scraper_exit_code}
    
    # Deactivate virtual environment
    if command -v deactivate &> /dev/null; then
        deactivate
    fi
    
    exit ${scraper_exit_code}
}

# Execute main function
main "$@"