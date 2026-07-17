#!/bin/bash
set -e

INSTALL_DIR="$HOME/Projeler/qr-kod-uygulamasi"
REPO_URL="https://raw.githubusercontent.com/ByteChesterX/CoQr/main"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

banner() {
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║     QR Kod Üretici & Okuyucu          ║"
    echo "  ║           Installer v1.0              ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

check_root() {
    if [ "$EUID" -eq 0 ]; then
        error "Root olarak çalıştırma. Normal kullanıcı olarak devam et."
    fi
}

detect_distro() {
    if [ -f /etc/arch-release ]; then
        DISTRO="arch"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    elif [ -f /etc/fedora-release ]; then
        DISTRO="fedora"
    elif command -v brew &>/dev/null; then
        DISTRO="macos"
    else
        DISTRO="unknown"
    fi
    log "Tespit edilen distro: $DISTRO"
}

install_system_deps() {
    log "Sistem bağımlılıkları kuruluyor..."
    case $DISTRO in
        arch)
            sudo pacman -S --needed --noconfirm python tk zbar 2>/dev/null || \
            sudo pacman -S --needed --noconfirm tkinter zbar
            ;;
        debian)
            sudo apt update -qq
            sudo apt install -y python3-tk python3-pip libzbar0
            ;;
        fedora)
            sudo dnf install -y python3-tkinter zbar
            ;;
        macos)
            brew install zbar tcl-tk
            ;;
        *)
            warn "Distro tanınamadı. Manuel kurulum gerekebilir."
            warn "Gerekli paketler: python3, python3-tk, libzbar0"
            ;;
    esac
    log "Sistem bağımlılıkları kuruldu"
}

setup_venv() {
    log "Sanal ortam oluşturuluyor: $INSTALL_DIR/venv"
    mkdir -p "$INSTALL_DIR"
    python3 -m venv "$INSTALL_DIR/venv"
    log "Sanal ortam hazır"
}

install_python_deps() {
    log "Python bağımlılıkları kuruluyor..."
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
    "$INSTALL_DIR/venv/bin/pip" install -q \
        customtkinter \
        "qrcode[pil]" \
        Pillow \
        opencv-python \
        pyzbar
    log "Python bağımlılıkları kuruldu"
}

download_app() {
    log "Uygulama dosyaları indiriliyor..."
    mkdir -p "$INSTALL_DIR"

    if curl -sf "$REPO_URL/qr_kod_app.py" -o "$INSTALL_DIR/qr_kod_app.py"; then
        log "qr_kod_app.py indirildi"
    else
        warn "İndirme başarısız, mevcut dosya kullanılıyor"
        if [ ! -f "$INSTALL_DIR/qr_kod_app.py" ]; then
            error "qr_kod_app.py bulunamadı!"
        fi
    fi
}

create_launcher() {
    log "Başlatıcı oluşturuluyor..."
    cat > "$INSTALL_DIR/qr-kod" << 'LAUNCHER'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/qr_kod_app.py" "$@"
LAUNCHER
    chmod +x "$INSTALL_DIR/qr-kod"

    if [ ! -d "$HOME/.local/bin" ]; then
        mkdir -p "$HOME/.local/bin"
    fi
    ln -sf "$INSTALL_DIR/qr-kod" "$HOME/.local/bin/qr-kod" 2>/dev/null || true
    log "Başlatıcı hazır"
}

create_uninstaller() {
    cat > "$INSTALL_DIR/uninstall.sh" << 'UNINSTALL'
#!/bin/bash
INSTALL_DIR="$HOME/Projeler/qr-kod-uygulamasi"
echo "Kaldırılıyor: $INSTALL_DIR"
rm -rf "$INSTALL_DIR"
rm -f "$HOME/.local/bin/qr-kod"
echo "QR Kod uygulaması kaldırıldı."
UNINSTALL
    chmod +x "$INSTALL_DIR/uninstall.sh"
}

summary() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Kurulum tamamlandı!${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Uygulamayı başlatmak için:"
    echo -e "  ${YELLOW}~/Projeler/qr-kod-uygulamasi/qr-kod${NC}"
    echo ""
    echo -e "  Veya manuel:"
    echo -e "  ${YELLOW}~/Projeler/qr-kod-uygulamasi/venv/bin/python ~/Projeler/qr-kod-uygulamasi/qr_kod_app.py${NC}"
    echo ""
    echo -e "  Kaldırmak için:"
    echo -e "  ${YELLOW}~/Projeler/qr-kod-uygulamasi/uninstall.sh${NC}"
    echo ""
}

main() {
    banner
    check_root
    detect_distro
    install_system_deps
    setup_venv
    install_python_deps
    download_app
    create_launcher
    create_uninstaller
    summary
}

main "$@"
