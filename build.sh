#/bin/bash
rm -rf __pycache__
rm -rf dist/ build/
rm -rf dist_linux dist_windows
rm -f ehl_assistant*.zip

# Linux version
pyinstaller -F ./ehl_assistant.py
mkdir dist/chromedriver
cp chromedriver/chromedriver_linux dist/chromedriver/
cp -f highlights dist/
cp -f version dist/
mv dist dist_linux
rm -rf build/

# Windows version
wine pyinstaller -F --hidden-import redcap ./ehl_assistant.py
mkdir dist/chromedriver
cp chromedriver/chromedriver_windows.exe dist/chromedriver/
cp -f highlights dist/
cp -f version dist/
mv dist ehl_assistant
version=$(head -n 1 version)
zip -r ehl_assistant_$version.zip ehl_assistant/
mv ehl_assistant dist_windows
rm -rf build/
