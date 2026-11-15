#!/usr/bin/env bash
# Fetch the Blender used to build these boats, outside the workspace.
#
# Blender is ~1.3 GB unpacked.  Do not install it inside a synced/snapshotted
# working tree: the snapshot cap silently truncates large trees, and a
# truncated Blender fails in confusing ways (missing shared libraries, a
# half-written 4.2 tree).  Keep it in /var/tmp and point LD_LIBRARY_PATH at it.
set -euo pipefail

PREFIX="${PREFIX:-/var/tmp}"
VERSION="${VERSION:-4.2.3}"
DIR="$PREFIX/blender"

if [ -x "$DIR/blender" ]; then
    echo "Blender already at $DIR ($("$DIR/blender" --version | head -1))"
    exit 0
fi

TARBALL="$PREFIX/blender-$VERSION-linux-x64.tar.xz"
curl -fsSL -o "$TARBALL" \
    "https://download.blender.org/release/Blender${VERSION%.*}/blender-$VERSION-linux-x64.tar.xz"
tar -xf "$TARBALL" -C "$PREFIX"
mv "$PREFIX/blender-$VERSION-linux-x64" "$DIR"
rm -f "$TARBALL"

# The headless build still links libxkbcommon even though it never opens a
# window.  If the distro package is absent, unpack the .deb into Blender's lib
# directory so LD_LIBRARY_PATH finds it.
if ! ldconfig -p | grep -q libxkbcommon.so.0; then
    echo "fetching libxkbcommon ..."
    tmp="$(mktemp -d)"
    (cd "$tmp" && apt-get download libxkbcommon0 >/dev/null 2>&1) ||         echo "warning: could not download libxkbcommon0; Blender may not start" >&2
    deb="$(ls "$tmp"/libxkbcommon0_*.deb 2>/dev/null | head -1)"
    if [ -n "$deb" ]; then
        dpkg -x "$deb" "$tmp/x"
        cp -a "$tmp"/x/usr/lib/x86_64-linux-gnu/libxkbcommon.so* "$DIR/lib/" 2>/dev/null || true
    fi
    rm -rf "$tmp"
fi

echo "Blender $VERSION installed at $DIR"
echo "run with:  LD_LIBRARY_PATH=$DIR/lib $DIR/blender -b --python <script>"
