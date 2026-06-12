#!/bin/bash
# Double-click this file in Finder to play, or run ./run.command in a terminal.
# It cd's to its own folder (handles the trailing space in the path) and launches.

cd "$(dirname "$0")" || exit 1

# Make sure the game library is installed (pygame-ce has prebuilt macOS wheels).
if ! python3 -c "import pygame" >/dev/null 2>&1; then
    echo "First-time setup: installing pygame-ce..."
    pip3 install pygame-ce || {
        echo "Could not install pygame-ce. Try:  pip3 install pygame-ce"
        read -r -p "Press Return to close..."
        exit 1
    }
fi

echo "Launching Party Bird..."
python3 main.py
status=$?

# Keep the terminal window open if it crashed, so the error stays readable.
if [ $status -ne 0 ]; then
    echo
    echo "The game exited with an error (code $status)."
    read -r -p "Press Return to close..."
fi
