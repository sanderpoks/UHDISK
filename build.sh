#/bin/bash
pyinstaller -F ./ehl_assistant.py
cp -fR chromedriver dist/
cp -f highlights dist/
