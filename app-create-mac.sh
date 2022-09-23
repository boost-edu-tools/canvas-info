#!/bin/bash

# To create the CLI and GUI apps for the canvas-info app,
# execute one of the following commands:
# bash create.sh or ./create.sh

# Assume we are in the root folder of the repository
if [[ ! -e app-create-mac.sh ]]; then
    echo >&2 "Script should be called from the repo's root folder."
    exit 1
fi

echo Creating GUI apps and CLI executables for macOS
echo "Deleting old app directories"
rm -rf app
rm -rf build
echo
echo "Creating CLI executable canvas-info"
echo
pyinstaller --distpath=app/mac app-spec-cli-file.spec
echo
echo "Creating CLI bundle canvas-info"
echo
pyinstaller --distpath=app/mac app-spec-cli-bundle.spec
echo
echo "Creating GUI apps canvas-info"
echo
pyinstaller --distpath=app/mac app-spec-gui.spec
echo
echo "Done, GUI apps and CLI executables are in directory app/mac:"
echo "CanvasInfoGUI.app     : macOS GUI app."
echo "canvas-info-cli       : macOS CLI executable for CLI input and output."
echo "canvas-info-cli2gui   : macOS CLI executable that starts up the GUI app, normally not needed."
echo "bundle/canvas-info-cli: macOS CLI bundel     for CLI input and output."

# Note that even though we have the setting upx=False in all apps-spec-xxx-xxx.spec
# files, we still get from pyinstaller:
# INFO: UPX is not available.
