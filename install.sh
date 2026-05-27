#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/frgardin/transcribe-videos"
PACKAGE_NAME="transcribe-yt"
CMD_NAME="trs"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

ok()   { echo -e "${GREEN}[✓]${RESET} $*"; }
warn() { echo -e "${YELLOW}[!]${RESET} $*"; }
fail() { echo -e "${RED}[✗]${RESET} $*"; exit 1; }

# ── Uninstall mode ────────────────────────────────────────────────────────────
if [[ "${1}" == "--uninstall" ]]; then
    echo "Uninstalling ${CMD_NAME}..."
    if command -v pipx &>/dev/null; then
        pipx uninstall "${PACKAGE_NAME}"
        ok "${CMD_NAME} has been uninstalled."
    else
        fail "pipx not found — ${CMD_NAME} was likely never installed via this script."
    fi
    exit 0
fi

echo ""
echo "  trs installer"
echo "  ─────────────"
echo ""

# ── OS check ──────────────────────────────────────────────────────────────────
if [[ "$(uname -s)" != "Linux" ]]; then
    warn "This script targets Linux. Continuing anyway, but it may not work correctly."
fi

# ── Python 3.10+ check ────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3 python3.12 python3.11 python3.10; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        major=${version%%.*}
        minor=${version##*.}
        if [[ "$major" -ge 3 && "$minor" -ge 10 ]]; then
            PYTHON="$candidate"
            ok "Python ${version} found (${PYTHON})"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    fail "Python 3.10 or higher is required but was not found. Install it with: sudo apt install python3"
fi

# ── pipx install ──────────────────────────────────────────────────────────────
if command -v pipx &>/dev/null; then
    ok "pipx $(pipx --version) already installed"
else
    echo "Installing pipx..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y pipx
    else
        "$PYTHON" -m pip install --user pipx
        "$PYTHON" -m pipx ensurepath
    fi
    ok "pipx installed"
fi

# ── Ensure ~/.local/bin is on PATH ────────────────────────────────────────────
pipx ensurepath --force &>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"

# ── Install trs ───────────────────────────────────────────────────────────────
if [[ -f "pyproject.toml" ]]; then
    warn "pyproject.toml detected — installing from local source."
    SOURCE="."
else
    SOURCE="git+${REPO_URL}"
fi

echo "Installing ${CMD_NAME} via pipx..."

if pipx list 2>/dev/null | grep -q "${PACKAGE_NAME}"; then
    warn "${CMD_NAME} already installed — reinstalling to update."
    pipx reinstall "${PACKAGE_NAME}" &>/dev/null \
        || pipx install --force "${SOURCE}" &>/dev/null
else
    pipx install "${SOURCE}"
fi

ok "${CMD_NAME} installed successfully!"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "  You can now run:"
echo ""
echo "    ${CMD_NAME} --help"
echo "    ${CMD_NAME} youtube \"<url>\" -o transcript.txt"
echo "    ${CMD_NAME} file audio.mp3 -o transcript.txt"
echo ""

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    warn "~/.local/bin is not yet in your PATH for this session."
    warn "Open a new terminal or run: source ~/.bashrc"
fi
