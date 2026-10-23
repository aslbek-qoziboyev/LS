#!/usr/bin/env bash
set -Eeuo pipefail

ARCHIVE="https://codeload.github.com/aslbek-qoziboyev/LS/tar.gz/refs/heads/main"
WORKDIR="$(mktemp -d -t ls-linux-tools.XXXXXX)"
trap 'rm -rf "$WORKDIR"' EXIT

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run this installer as root, for example:"
  echo "curl -fsSL https://raw.githubusercontent.com/aslbek-qoziboyev/LS/main/install.sh | sudo bash"
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "Error: this installer supports Debian-based systems with apt-get (Kali, Debian, Ubuntu)." >&2
  exit 1
fi

echo "[1/5] Updating package lists and installing download tools..."
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl tar python3

echo "[2/5] Downloading LS-Linux Tools source from GitHub..."
mkdir -p "$WORKDIR/source"
curl --fail --location --silent --show-error "$ARCHIVE" | tar -xz --strip-components=1 -C "$WORKDIR/source"

SRC="$WORKDIR/source"
PKG="$WORKDIR/pkg"
DEBIAN="$PKG/DEBIAN"

for file in \
  src/ls_tools.py \
  usr/bin/ls-linux-tools \
  usr/lib/ls-linux-tools/display-cycle \
  usr/share/applications/ls-linux-tools.desktop \
  usr/share/icons/hicolor/scalable/apps/ls-linux-tools.svg; do
  if [[ ! -f "$SRC/$file" ]]; then
    echo "Error: required project file is missing: $file" >&2
    exit 1
  fi
done

echo "[3/6] Installing Touchégg from its official GitHub release..."
ARCH="$(dpkg --print-architecture)"
curl --fail --location --silent --show-error \
  "https://api.github.com/repos/JoseExposito/touchegg/releases/latest" \
  -o "$WORKDIR/touchegg-release.json"
TOUCHEGG_URL="$(python3 - "$WORKDIR/touchegg-release.json" "$ARCH" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as file:
    release = json.load(file)

arch = sys.argv[2]
assets = release.get("assets", [])
asset = next(
    (item for item in assets
     if item.get("name", "").endswith(f"_{arch}.deb")
     and item.get("name", "").startswith("touchegg_")),
    None,
)
if asset is None:
    print(f"No official Touchégg .deb asset found for architecture: {arch}", file=sys.stderr)
    sys.exit(1)
print(asset["browser_download_url"])
PY
)"
curl --fail --location --silent --show-error "$TOUCHEGG_URL" -o "$WORKDIR/touchegg.deb"
apt-get install -y "$WORKDIR/touchegg.deb"

echo "[4/6] Preparing the Debian package..."
mkdir -p "$DEBIAN" \
  "$PKG/usr/bin" \
  "$PKG/usr/lib/ls-linux-tools" \
  "$PKG/usr/share/applications" \
  "$PKG/usr/share/icons/hicolor/scalable/apps"

install -m 0755 "$SRC/usr/bin/ls-linux-tools" "$PKG/usr/bin/ls-linux-tools"
install -m 0644 "$SRC/src/ls_tools.py" "$PKG/usr/lib/ls-linux-tools/ls_tools.py"
install -m 0755 "$SRC/usr/lib/ls-linux-tools/display-cycle" "$PKG/usr/lib/ls-linux-tools/display-cycle"
install -m 0644 "$SRC/usr/share/applications/ls-linux-tools.desktop" "$PKG/usr/share/applications/ls-linux-tools.desktop"
install -m 0644 "$SRC/usr/share/icons/hicolor/scalable/apps/ls-linux-tools.svg" "$PKG/usr/share/icons/hicolor/scalable/apps/ls-linux-tools.svg"

cat > "$DEBIAN/control" <<'CONTROL'
Package: ls-linux-tools
Version: 0.1.0
Section: utils
Priority: optional
Architecture: all
Maintainer: LS Linux Tools <noreply@github.com>
Depends: python3, python3-gi, gir1.2-gtk-3.0, touchegg, xinput, x11-xserver-utils
Description: LS-Linux touchpad gesture settings
 GTK settings utility for configuring selected touchpad gestures.
CONTROL

chmod 0755 "$DEBIAN"
chmod 0644 "$DEBIAN/control"
DEB="$WORKDIR/ls-linux-tools_0.1.0_all.deb"
dpkg-deb --build --root-owner-group "$PKG" "$DEB"

echo "[5/6] Installing LS-Linux Tools and resolving dependencies..."
apt-get install -y "$DEB"

echo "[6/6] Installation complete."
echo "Launch it from your application menu or run: ls-linux-tools"
echo "If Touchégg was just installed, log out and back in if gestures do not work yet."
