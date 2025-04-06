# xfce-shibui

A minimal, keyboard-driven workspace navigation overlay for XFCE.

Inspired by the Japanese concept of *shibui* — the beauty of quiet, functional simplicity — this script displays a clean, non-intrusive grid of workspaces when you hold the Super key, and hides it as soon as you release. Navigate naturally using arrow keys, without ever needing a persistent panel.

## Features

- Minimal transient overlay
- Super + arrow key workspace switching
- Visual grid representation (when you want it, not before)
- No distractions. Just function.

## How to run in XFCE

Open "Session and startup", then "Application autostart", and add it there on login with regular user privileges.

## How to run with crontab

Run crontab -e, then add the following line:
@reboot python3 /usr/local/bin/ws-feedback-pynput.py
