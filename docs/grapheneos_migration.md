# GrapheneOS Migration Plan

## Why
- No Google services tracking
- App sandboxing + hardened malloc
- Profile isolation (Personal / Work / AETHORFORGE)
- Verified boot chain

## Hardware
- Pixel 6a (~$150 used) — best value
- Pixel 7 — better NPU for local models
- Pixel 8 — latest, most support

## Steps
1. Buy supported Pixel
2. Go to grapheneos.org/install/web
3. Follow web installer (Chrome required)
4. Install F-Droid from grapheneos.org/apps
5. Install Termux from F-Droid
6. git clone your AETHORFORGE repo
7. export GROQ_API_KEY and run main.py

## AETHORFORGE Profile Setup
- Create isolated "AETHORFORGE" profile
- Only Termux + browser in that profile
- Main profile: daily use
- Work profile: bug bounty submissions

## Current Moto G path
- Termux + AETHORFORGE works fine now
- GrapheneOS is an upgrade path, not required today

