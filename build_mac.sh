#/bin/bash
rm -rf __pycache__
rm -rf dist/ build/
rm -rf dist_mac/
rm -rf ehl_assistant_mac*.zip

# Mac version
pyinstaller -F ./ehl_assistant.py
mkdir dist/chromedriver
cp chromedriver/chromedriver_mac dist/chromedriver/
cp -f highlights dist/
cp -f version dist/
mv dist dist_mac
rm -rf build/

mv dist_mac ehl_assistant
version=$(head -n 1 version)
zip -r ehl_assistant_mac_$version.zip ehl_assistant/
mv ehl_assistant dist_mac
