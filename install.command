#!/bin/bash
# License Uploader - macOS Installer
#
# Double-click this file in Finder to install License Uploader on macOS.
# This wraps install.sh so Finder executes it in Terminal instead of
# opening it in a text editor (which is Finder's default for .sh files).

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

bash ./install.sh
status=$?

echo ""
read -p "Press Enter to close this window..."
exit $status
