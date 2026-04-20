#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dialogs Module Example: iOS Native Alert API

This script demonstrates the full dialogs API:
1. input_alert  - Single-line text input (placeholder, secure for passwords)
2. list_dialog  - Single or multi-select list
3. hud_alert    - Lightweight HUD (non-blocking)
4. alert        - Multi-button confirmation

All dialogs use native iOS style. Cancelling raises KeyboardInterrupt.
"""

import dialogs

def main():
    print("=" * 50)
    print("  dialogs Module Example")
    print("=" * 50)

    print("\n[1] input_alert - Enter your nickname")
    try:
        name = dialogs.input_alert("Enter nickname", message="Used for display", placeholder="Your name")
        print(f"  → You entered: {name}")
    except KeyboardInterrupt:
        print("  → Cancelled")

    print("\n[2] list_dialog - Pick a color")
    try:
        colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple"]
        idx = dialogs.list_dialog("Select color", colors)
        if idx and 1 <= idx <= len(colors):
            print(f"  → Selected: {colors[idx - 1]}")
        else:
            print("  → Invalid")
    except KeyboardInterrupt:
        print("  → Cancelled")

    print("\n[3] alert - Confirm action")
    try:
        choice = dialogs.alert("Confirm", "Continue?", "Cancel", "OK")
        print(f"  → Button index: {choice} (1=Cancel, 2=OK)")
    except KeyboardInterrupt:
        print("  → Cancelled")

    print("\n[4] hud_alert - Completion hint")
    dialogs.hud_alert("All done!", duration=2.0)
    print("  → HUD shown 2 sec")

    print("\n" + "=" * 50)
    print("  Example finished")
    print("=" * 50)

if __name__ == "__main__":
    main()