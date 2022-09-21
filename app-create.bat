@echo OFF

if not exist app-create.bat (
    echo Script should be called from the repo's root folder.
    exit /b 1
)

echo Creating GUI apps and CLI executables for macOS
echo Deleting old app directories
if exist app\ (
    rmdir /s /q app
)
if exist build\ (
    rmdir /s /q build
)
echo Creating CLI executable canvas-info
pyinstaller --distpath=app app-spec-cli-file.spec
echo Creating CLI bundle canvas-info
pyinstaller --distpath=app app-spec-cli-bundle.spec
echo Creating GUI apps canvas-info
pyinstaller --distpath=app app-spec-gui.spec
echo Done, GUI apps and CLI executables are in directory app:
echo canvas-info-app.exe                  : Windows GUI app.
echo canvas-info.exe                      : Windows CLI executable for CLI input and output.
echo canvas-info-bundle/gitinsp-bundle.exe: Windows CLI bundel     for CLI input and output.
