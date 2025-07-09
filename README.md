# Canvas Info

A Python application for managing Canvas course information and generating student files for educational workflows.

---

## Features

- **Canvas Integration** – Connect to any Canvas LMS with a personal access token.
- **Student Data Export** – Generate CSV, Excel, and YAML files.
- **Multiple Output Formats**\
  ▸ CSV/Excel files with enrolment data\
  ▸ YAML files for RepoBee integration\
  ▸ Teammates‑compatible Excel files
---

## Installation

### Requirements

- Python 3.8 or newer
- Canvas API access token
- [Briefcase](https://briefcase.beeware.org) for building and running the app

### Setup development environment

```bash
# Install Briefcase
pip install briefcase

# Clone the repository
git clone -b Briefcase-PySide6-canvasinfo https://github.com/boost-edu-tools/canvas-info.git
cd canvasinfo

# 1️⃣  Create/refresh the managed environment (first run *or* after editing pyproject.toml)
briefcase dev -r --no-run

# 2️⃣  Launch the GUI in dev mode
briefcase dev
```
## Usage

### Development mode

```bash
# Run the GUI application
briefcase dev
```

### Building & packaging

```bash
# Build native bundle for the current platform
briefcase build

# Create an installer (MSI, DMG, AppImage, …)
briefcase package

# Run the packaged app
briefcase run
```

---

## Configuration

### Canvas setup

1. Generate an access token in Canvas → *Account ▸ Settings ▸ New Access Token*.
2. Note your Canvas base URL (e.g. `https://canvas.tue.nl`).
3. Copy the course ID from the course URL.

### First‑run wizard

1. Launch the application.
2. Enter your Canvas credentials (Step 1).
3. Select or create a course configuration (Step 2).
4. Click **Verify Course** to test the settings.
5. Configure output options (Step 3).
6. Click **Execute** to generate files.

---

## Contributing

This project builds upon work by Huub de Beer. 


