#!/bin/bash

# ==============================================================================
# UE5 Documentation Scraper - Arch Linux Setup Script
# This script sets up the complete environment for the UE5 documentation scraper
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
readonly LOG_FILE="${SCRIPT_DIR}/setup.log"
readonly REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"
readonly VENV_DIR="${SCRIPT_DIR}/venv"

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
    log_error "Setup failed with exit code: ${exit_code}"
    echo
    echo "Setup was interrupted. Check the log file for details: ${LOG_FILE}"
    exit "${exit_code}"
}

trap cleanup_on_error ERR

# Initialize setup
initialize_setup() {
    cd "${SCRIPT_DIR}"
    
    # Initialize log file
    echo "=============================================================================" > "${LOG_FILE}"
    echo "UE5 Documentation Scraper Setup Log - $(date)" >> "${LOG_FILE}"
    echo "=============================================================================" >> "${LOG_FILE}"
    
    echo
    echo "==============================================================================="
    echo "        UE5 Documentation Scraper - Arch Linux Setup"
    echo "==============================================================================="
    echo
    
    log_info "Starting setup process..."
    log_info "Script directory: ${SCRIPT_DIR}"
    log_info "Log file: ${LOG_FILE}"
}

# Check if running on Arch Linux
check_arch_linux() {
    log_info "[1/8] Checking operating system..."
    
    if [[ ! -f /etc/arch-release ]]; then
        log_warning "This script is designed for Arch Linux"
        log_warning "Current OS: $(uname -s) $(uname -r)"
        echo
        read -p "Continue anyway? [y/N]: " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Setup cancelled by user"
            exit 0
        fi
    else
        log_success "Arch Linux detected"
    fi
}

# Check if script is run with appropriate privileges
check_privileges() {
    log_info "[2/8] Checking system privileges..."
    
    if ! sudo -n true 2>/dev/null; then
        log_info "This script requires sudo privileges for system package installation"
        echo "You may be prompted for your password..."
        sudo -v || {
            log_error "Failed to obtain sudo privileges"
            exit 1
        }
    fi
    
    log_success "Sudo privileges confirmed"
}

# Install system dependencies
install_system_dependencies() {
    log_info "[3/8] Installing system dependencies..."
    
    local packages=(
        "python"
        "python-pip" 
        "python-virtualenv"
        "chromium"
        "wkhtmltopdf"
        "base-devel"  # Often needed for compiling Python packages
    )
    
    log_info "Updating package database..."
    sudo pacman -Sy --noconfirm || {
        log_error "Failed to update package database"
        exit 1
    }
    
    log_info "Installing packages: ${packages[*]}"
    sudo pacman -S --needed --noconfirm "${packages[@]}" || {
        log_error "Failed to install system dependencies"
        log_error "Try running: sudo pacman -S ${packages[*]}"
        exit 1
    }
    
    log_success "System dependencies installed successfully"
}

# Verify Python installation
verify_python() {
    log_info "[4/8] Verifying Python installation..."
    
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        log_error "Python not found after installation"
        exit 1
    fi
    
    # Prefer python3 if available, fall back to python
    local python_cmd="python3"
    if ! command -v python3 &> /dev/null; then
        python_cmd="python"
    fi
    
    local python_version
    python_version=$($python_cmd --version 2>&1)
    log_success "Python found: ${python_version}"
    
    # Check if version is 3.8+
    local version_check
    if $python_cmd -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        log_success "Python version is compatible (3.8+)"
    else
        log_warning "Python version may be too old. Python 3.8+ is recommended."
    fi
    
    # Store python command for later use
    echo "PYTHON_CMD=${python_cmd}" > "${SCRIPT_DIR}/.python_cmd"
}

# Check requirements file
check_requirements() {
    log_info "[5/8] Checking requirements file..."
    
    if [[ ! -f "${REQUIREMENTS_FILE}" ]]; then
        log_error "Requirements file not found: ${REQUIREMENTS_FILE}"
        exit 1
    fi
    
    log_success "Requirements file found: ${REQUIREMENTS_FILE}"
    log_info "Required packages:"
    while IFS= read -r line; do
        [[ -n "$line" && ! "$line" =~ ^# ]] && log_info "  - $line"
    done < "${REQUIREMENTS_FILE}"
}

# Handle existing virtual environment
handle_existing_venv() {
    log_info "[6/8] Checking virtual environment..."
    
    if [[ -d "${VENV_DIR}" ]]; then
        log_warning "Existing virtual environment found: ${VENV_DIR}"
        echo
        read -p "Remove existing virtual environment and create new one? [y/N]: " -r
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing existing virtual environment..."
            rm -rf "${VENV_DIR}" || {
                log_error "Failed to remove existing virtual environment"
                exit 1
            }
            log_success "Existing virtual environment removed"
        else
            log_info "Keeping existing virtual environment"
            return 0
        fi
    fi
    
    return 1  # Indicate that we need to create a new venv
}

# Create virtual environment
create_virtual_environment() {
    log_info "[7/8] Creating Python virtual environment..."
    
    # Source the python command
    source "${SCRIPT_DIR}/.python_cmd" 2>/dev/null || PYTHON_CMD="python3"
    
    $PYTHON_CMD -m venv "${VENV_DIR}" || {
        log_error "Failed to create virtual environment"
        log_error "Make sure python3-venv is installed: sudo pacman -S python-virtualenv"
        exit 1
    }
    
    log_success "Virtual environment created successfully"
}

# Install Python dependencies
install_python_dependencies() {
    log_info "[8/8] Installing Python dependencies..."
    
    # Activate virtual environment
    # shellcheck source=/dev/null
    source "${VENV_DIR}/bin/activate" || {
        log_error "Failed to activate virtual environment"
        exit 1
    }
    
    log_info "Virtual environment activated"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip --quiet || {
        log_warning "Failed to upgrade pip, continuing with current version"
    }
    
    # Display pip and python versions
    local pip_version python_version
    pip_version=$(pip --version 2>/dev/null || echo "unknown")
    python_version=$(python --version 2>&1 || echo "unknown")
    log_info "Using: ${python_version}"
    log_info "Using: ${pip_version}"
    
    # Install dependencies
    log_info "Installing packages from: ${REQUIREMENTS_FILE}"
    pip install -r "${REQUIREMENTS_FILE}" || {
        log_error "Failed to install Python dependencies"
        log_error "Try running manually:"
        log_error "  source venv/bin/activate"
        log_error "  pip install -r requirements.txt"
        exit 1
    }
    
    log_success "Python dependencies installed successfully"
    
    # Verify critical packages
    log_info "Verifying package installation..."
    local packages=("requests" "beautifulsoup4" "selenium" "lxml" "aiohttp")
    local failed_packages=()
    
    for package in "${packages[@]}"; do
        if python -c "import ${package}" 2>/dev/null; then
            log_info "  ✓ ${package}"
        else
            log_warning "  ✗ ${package} - import failed"
            failed_packages+=("${package}")
        fi
    done
    
    if [[ ${#failed_packages[@]} -gt 0 ]]; then
        log_warning "Some packages failed to import: ${failed_packages[*]}"
        log_warning "The scraper may not work properly"
    else
        log_success "All critical packages verified"
    fi
    
    deactivate
}

# Run installation tests
run_tests() {
    log_info "Running installation validation..."
    
    if [[ -f "${SCRIPT_DIR}/test_setup.py" ]]; then
        # shellcheck source=/dev/null
        source "${VENV_DIR}/bin/activate"
        
        if python test_setup.py; then
            log_success "Installation validation: PASSED"
        else
            log_warning "Installation validation: FAILED"
            log_warning "The setup may still work, but some functionality might be limited"
        fi
        
        deactivate
    else
        log_info "test_setup.py not found, skipping validation tests"
    fi
}

# Display final results and instructions
display_results() {
    echo
    echo "==============================================================================="
    echo -e "${GREEN}                    SETUP COMPLETED SUCCESSFULLY!${NC}"
    echo "==============================================================================="
    echo
    echo "NEXT STEPS:"
    echo
    echo "To run the UE5 Documentation Scraper:"
    echo "  1. Activate the virtual environment:"
    echo "     source venv/bin/activate"
    echo
    echo "  2. Run the scraper:"
    echo "     python ue5_docs_scraper.py"
    echo
    echo "  3. When done, deactivate the environment:"
    echo "     deactivate"
    echo
    echo "USEFUL COMMANDS:"
    echo "  - Check installation: python test_setup.py (if available)"
    echo "  - View logs: cat ${LOG_FILE}"
    echo "  - Reinstall deps: pip install -r requirements.txt"
    echo
    echo "Files created:"
    echo "  - Virtual environment: ${VENV_DIR}"
    echo "  - Setup log: ${LOG_FILE}"
    echo
    
    log_success "Setup completed successfully!"
}

# Main execution
main() {
    initialize_setup
    check_arch_linux
    check_privileges
    install_system_dependencies
    verify_python
    check_requirements
    
    # Handle virtual environment creation
    if ! handle_existing_venv; then
        create_virtual_environment
    fi
    
    install_python_dependencies
    run_tests
    display_results
    
    # Cleanup temporary files
    rm -f "${SCRIPT_DIR}/.python_cmd"
}

# Execute main function
main "$@"