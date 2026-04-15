# 🚀 Get Started with License Uploader

**Simple guide for everyone - no technical experience needed!**

---

## What This Does

License Uploader uses AI to automatically extract license terms from documents and upload them to your Alma library system.

**Before:** Manually type 76+ license terms → Takes hours
**After:** Upload document → AI extracts everything → You review → Submit → Done in minutes

---

## Quick Start (3 Steps)

### 1️⃣ First Time Only: Install

**Windows:**
```batch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Configure API Keys (One Time)

1. Copy `.env.example` to `.env`
2. Edit `.env` with your API keys:
   ```
   ALMA_API_KEY=your_alma_key_here
   LITELLM_API_KEY=your_litellm_key_here
   ```

### 3️⃣ Start the Application

**Easiest way:**

- **Windows:** Double-click `START_HERE.bat`
- **macOS:** Double-click `START_HERE.command`
- **Linux:** Double-click `START_HERE.sh` (or run `./START_HERE.sh`)

> **macOS note:** Use the `.command` file, **not** `START_HERE.sh`. Finder opens `.sh` files in a text editor on double-click — only `.command` files launch in Terminal. If Gatekeeper blocks it the first time, right-click → Open → Open.

**Alternative (command line):**
```bash
python launcher.py
```

Your browser will open automatically to http://localhost:5000

---

## Using the Application

1. **Upload** a license document (PDF, DOCX, or TXT)
2. **Wait** while AI extracts the terms (30-60 seconds)
3. **Review** the extracted terms
4. **Edit** any terms that need correction
5. **Submit** to Alma

Done! No manual data entry needed.

---

## How to Stop

- Click **"Stop Application"** button in the launcher
- Or close the launcher window
- Or press `Ctrl+C` in terminal

---

## Desktop Shortcut (Optional)

**Windows:**
- Right-click `START_HERE.bat` → "Create shortcut" → Drag to Desktop

**Mac:**
- Hold Option+Command, drag `START_HERE.command` to Desktop

**Linux:**
```bash
cp License_Uploader.desktop ~/Desktop/
chmod +x ~/Desktop/License_Uploader.desktop
```

---

## Troubleshooting

### "Port already in use"
The launcher handles this automatically. Just click Start again.

### "Virtual environment not found"
Run Step 1 (Install) above.

### Browser doesn't open
Copy `http://localhost:5000` from the launcher window and paste into your browser.

### Application won't start
1. Check Python is installed (3.11+)
2. Check `.env` file exists with your API keys
3. Try restarting your computer

---

## Need More Help?

- **Detailed instructions:** See `USER_GUIDE.md`
- **Installation issues:** See `INSTALLATION_GUIDE.md`
- **Technical problems:** See `TROUBLESHOOTING_GUIDE.md`
- **Production deployment:** See `docs/` folder

---

## System Requirements

- Python 3.11 or higher
- 2 GB RAM (4 GB recommended)
- Internet connection
- Modern web browser

**Supported systems:** Windows 10+, macOS 12+, Linux (Ubuntu 20.04+)

---

**That's it! Double-click the right START_HERE for your OS to begin.** 🎉
- Windows → `START_HERE.bat`
- macOS → `START_HERE.command`
- Linux → `START_HERE.sh`
