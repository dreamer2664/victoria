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

# the headless build still links libxkbcommon even without a display
if ! ldconfig -p | grep -q libxkbcommon.so.0; then
    echo "note: libxkbcommon is missing; install it or supply it on LD_LIBRARY_PATH" >&2
fi

echo "Blender $VERSION installed at $DIR"
echo "run with:  LD_LIBRARY_PATH=$DIR/lib $DIR/blender -b --python <script>"
