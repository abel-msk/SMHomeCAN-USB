#!/bin/bash
source venv/bin/activate
pyinstaller --windowed --name="SMHomeCAN-USB" --icon="icons/app5.icns"  \
      main.py
