# License Uploader - Windows Quick Start Guide

**For Windows 10 and Windows 11 Users**

This guide will get you up and running in under 10 minutes, even if you've never used Python before.

---

## Table of Contents

1. [Before You Begin](#before-you-begin)
2. [Quick Installation (Recommended)](#quick-installation-recommended)
3. [Running the Application](#running-the-application)
4. [Configuration](#configuration)
5. [Common Issues & Fixes](#common-issues--fixes)
6. [Getting Help](#getting-help)

---

## Before You Begin

### What You'll Need

- **Windows 10 or 11** (64-bit)
- **10 minutes** of your time
- **Internet connection** for downloading dependencies
- **Your API keys** (Alma API key and LiteLLM API key)

### Required Software

**Python 3.11 or higher** - Download from [python.org/downloads](https://www.python.org/downloads/)

⚠️ **IMPORTANT**: When installing Python, make sure to check the box that says **"Add Python to PATH"**!

![Python Installation](https://docs.python.org/3/_images/win_installer.png)

If you already have Python installed, check your version:
1. Open Command Prompt (press `Win + R`, type `cmd`, press Enter)
2. Type: `python --version`
3. If you see Python 3.11 or higher, you're good to go!

---

## Quick Installation (Recommended)

### Option 1: One-Click Installer (Easiest!)

1. **Download License Uploader**
   - Extract the ZIP file to a location like `C:\LicenseUploader`

2. **Run the Installer**
   - Double-click: `INSTALL_WINDOWS.bat`
   - Follow the on-screen prompts
   - Wait for installation to complete (2-5 minutes)

3. **Configure API Keys**
   - The installer will open the `.env` file in Notepad
   - Replace the placeholder values with your actual API keys:
     - `ALMA_API_KEY`: Your Alma API key
     - `LITELLM_API_KEY`: Your LiteLLM API key
     - `SECRET_KEY`: Leave as-is or generate a new one
   - Save and close Notepad

4. **Done!**
   - If installation succeeded, you'll see a green "SUCCESS" message
   - Skip to [Running the Application](#running-the-application)

### Option 2: Manual Installation

If the automatic installer doesn't work, follow these steps:

1. **Open Command Prompt in Project Directory**
   - Navigate to the License Uploader folder
   - Hold `Shift`, right-click in the folder, select "Open PowerShell window here" or "Open Command Prompt here"

2. **Create Virtual Environment**
   ```cmd
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   ```cmd
   venv\Scripts\activate
   ```

   You should see `(venv)` appear at the beginning of your command prompt.

   **Having trouble?** If you see an error about execution policies:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install Dependencies**
   ```cmd
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   This will take 2-5 minutes. Be patient!

5. **Configure Environment**
   ```cmd
   copy .env.example .env
   notepad .env
   ```

   Edit the file as described in Step 3 of Option 1 above.

6. **Verify Installation**
   ```cmd
   python diagnose_windows.py
   ```

   This will check if everything is set up correctly.

---

## Running the Application

### Method 1: Double-Click Launcher (Easiest)

1. **Double-click**: `START_HERE.bat`
2. A window will open showing the application starting
3. Your web browser will automatically open to `http://localhost:5000`
4. Start uploading license documents!

### Method 2: GUI Launcher

1. **Double-click**: `START_HERE.bat` (it will try GUI launcher first)
2. A graphical window appears with Start/Stop buttons
3. Click **"▶ Start Application"**
4. Click **"🌐 Open in Browser"** or it will open automatically
5. The application is running!

### Method 3: Command Line

1. Open Command Prompt in the project directory
2. Activate virtual environment: `venv\Scripts\activate`
3. Run: `python app.py`
4. Open browser to: `http://localhost:5000`

---

## Configuration

### Required API Keys

You need two API keys to use License Uploader:

#### 1. Alma API Key

**Where to get it:**
1. Log in to [Ex Libris Developer Network](https://developers.exlibrisgroup.com/)
2. Go to "API Keys"
3. Create new API key with permissions:
   - **Acquisitions**: Read/Write
   - **Vendors**: Read
4. Copy the API key

**Where to enter it:**
- Open `.env` file in Notepad
- Find the line: `ALMA_API_KEY=your_alma_api_key_here`
- Replace `your_alma_api_key_here` with your actual key
- Save the file

**Which region?**
Set `ALMA_API_BASE_URL` to match your region:
- North America: `https://api-na.hosted.exlibrisgroup.com`
- Europe: `https://api-eu.hosted.exlibrisgroup.com`
- Asia Pacific: `https://api-ap.hosted.exlibrisgroup.com`

#### 2. LiteLLM API Key

**Where to get it:**
- Contact your institution's IT administrator
- They will provide:
  - `LITELLM_API_KEY`: Your API key
  - `LITELLM_BASE_URL`: Your institution's AI gateway URL
  - `LITELLM_MODEL`: Model to use (e.g., `gpt-4`, `gpt-5`)

**Where to enter it:**
- Open `.env` file in Notepad
- Find the LiteLLM section
- Replace placeholder values with actual values from your admin
- Save the file

#### 3. Secret Key (Auto-Generated)

The `.env.example` includes a pre-generated secret key. This is fine for most users.

**To generate a new one:**
1. Open Command Prompt
2. Run:
   ```cmd
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Copy the output
4. Paste into `.env` file as `SECRET_KEY=<output>`

---

## Common Issues & Fixes

### Issue: "Python is not recognized..."

**Problem**: Python not in PATH

**Fix**:
1. Reinstall Python from python.org
2. **Make sure to check "Add Python to PATH"**
3. Or use the `py` command instead:
   ```cmd
   py -m venv venv
   ```

---

### Issue: "cannot be loaded because running scripts is disabled"

**Problem**: PowerShell execution policy

**Fix**:
1. Open PowerShell as Administrator
2. Run:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Try activation again

---

### Issue: Installation Takes Forever or Fails

**Problem**: Windows Defender or antivirus blocking pip

**Fix**:
1. Temporarily disable Windows Defender Real-time Protection
2. Run installation again
3. Re-enable Windows Defender
4. Or add project folder to exclusions:
   ```powershell
   Add-MpPreference -ExclusionPath "C:\path\to\license_uploader"
   ```

---

### Issue: "ImportError: No module named 'magic'"

**Problem**: Wrong python-magic package installed

**Fix**:
```cmd
venv\Scripts\activate
pip uninstall python-magic python-magic-bin
pip install python-magic-bin
```

---

### Issue: Port 5000 Already in Use

**Problem**: Another application using port 5000

**Fix**:
The launcher scripts automatically find an available port. If you see this error:
1. Close other applications using port 5000
2. Or just let it use an alternative port (it will tell you which one)

---

### Issue: GUI Launcher Won't Start (Tkinter Error)

**Problem**: Tkinter not included with your Python

**Fix**:
1. Use the command-line launcher instead
2. Or reinstall Python from python.org (includes Tkinter)

The `START_HERE.bat` script automatically falls back to command-line if GUI fails.

---

### Issue: Application Starts But Can't Upload Files

**Problem**: File type detection not working

**Fix**:
```cmd
python diagnose_windows.py --fix
```

This will detect and fix the issue automatically.

---

### Still Having Problems?

**Run the Diagnostic Tool**:
```cmd
DIAGNOSE_WINDOWS.bat
```

This will:
- Check your Python installation
- Verify all dependencies
- Test your configuration
- Identify any issues
- Offer to fix problems automatically

A detailed report will be saved to `diagnostic_report.txt`.

---

## Getting Help

### Quick Troubleshooting Checklist

- [ ] Python 3.11+ installed with "Add to PATH" checked
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Dependencies installed (run `pip list` to check)
- [ ] `.env` file exists with valid API keys
- [ ] Antivirus not blocking Python/pip
- [ ] No other application using port 5000

### Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - How to use the application
- **[TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md)** - Detailed troubleshooting
- **[WINDOWS_DEPLOYMENT_ANALYSIS.md](WINDOWS_DEPLOYMENT_ANALYSIS.md)** - Technical Windows issues

### Tools

- **DIAGNOSE_WINDOWS.bat** - Comprehensive diagnostic tool
- **INSTALL_WINDOWS.bat** - Reinstall or fix installation
- **START_HERE.bat** - Launch application

### Support

1. **Run diagnostics**: `DIAGNOSE_WINDOWS.bat`
2. **Check logs**: `logs\license_uploader.log`
3. **Review report**: `diagnostic_report.txt`
4. **Contact IT**: Provide the diagnostic report

---

## What's Next?

Once installed and running:

1. **Open your browser** to `http://localhost:5000`
2. **Upload a license document** (PDF, DOCX, or TXT)
3. **Review extracted terms** - AI does the heavy lifting!
4. **Edit if needed** - Make any corrections
5. **Submit to Alma** - One click!

**First time?** See [USER_GUIDE.md](USER_GUIDE.md) for a detailed walkthrough.

---

## Tips for Windows Users

### Performance Tips

- **Use an SSD** instead of HDD for better performance
- **Add antivirus exclusion** for the project folder
- **Close unnecessary programs** to free up RAM

### Security Tips

- **Never share your `.env` file** - it contains secret keys
- **Keep `.env` out of version control** (already in `.gitignore`)
- **Rotate API keys periodically**

### Maintenance

**Update License Uploader**:
1. Download new version
2. Copy your `.env` file to the new folder
3. Run `INSTALL_WINDOWS.bat` again

**Uninstall**:
1. Delete the project folder
2. Remove Python (optional) from "Add or Remove Programs"

---

## Frequently Asked Questions

**Q: Do I need Administrator rights?**
A: Not usually. Only if changing PowerShell execution policy or adding antivirus exclusions.

**Q: Can I install this on a shared/network drive?**
A: Yes, but it may be slower. Local installation is recommended.

**Q: Will this work on Windows 7/8?**
A: Not officially supported. Windows 10+ is required.

**Q: How much disk space do I need?**
A: About 500 MB to 1 GB including Python and dependencies.

**Q: Can I run multiple instances?**
A: Yes, but they need to use different ports.

**Q: Is my data secure?**
A: Yes. Data is processed locally and only API calls go to Alma/LiteLLM servers. See [SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md).

---

**Last Updated**: 2026-02-02
**Version**: 1.0
**For**: Windows 10/11 Users
