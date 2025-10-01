# 310-Ai-Security-System

# Project Setup Guide

This guide explains how to set up a Python virtual environment for this project and how to activate it on different operating systems.

---

## 1. Create a Virtual Environment

Run the following command to create a virtual environment named `.venv`:

```bash
python -m venv .venv
```

---

## 2. Activate the Virtual Environment

### On **Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
```

### On **Windows (Command Prompt)**
```cmd
.venv\Scripts\activate.bat
```

### On **macOS / Linux (Bash/Zsh)**
```bash
source .venv/bin/activate
```

---

## 3. Deactivate the Virtual Environment

To deactivate, simply run:

```bash
deactivate
```

---

## 4. Git Ignore Configuration

A `.gitignore` file is included to ensure the virtual environment is not committed to version control.

```
.venv/
```

---

## 5. Installing Dependencies

Once the virtual environment is active, install dependencies with:

```bash
pip install -r requirements.txt
```

---

## 6. Freezing Dependencies

To save newly installed packages into `requirements.txt`:

```bash
pip freeze > requirements.txt
```
