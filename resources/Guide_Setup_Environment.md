# Python Flask Development Environment Setup Guide

## Introduction
This guide will help you set up a professional Python development environment for working with Flask applications. This setup is specifically designed for the Generative AI module and will ensure you have all the necessary tools to complete your coursework and projects.

## Prerequisites
- A computer running Windows, macOS, or Linux
- Administrator/root access to install software
- At least 4GB of RAM (8GB recommended)
- At least 10GB of free disk space

## 1. Install Git
Git is essential for version control and collaboration.

### Windows/macOS:
- **Download**: Go to the [Git website](https://git-scm.com/) and download the installer for your operating system.
- **Install**: Run the installer and follow the on-screen instructions.
  - **Important**: Check the option "Add Git to PATH" during installation.
  - **macOS users**: You can also install Git using Homebrew: `brew install git`

### Verification:
Open a terminal/command prompt and run:
```bash
git --version
```
You should see the installed Git version.

## 2. Install Cursor IDE
Cursor is a modern IDE with built-in AI features that will help you throughout the course.

- **Download**: Go to the [Cursor website](https://www.cursor.com/) and download the installer for your operating system.
- **Note**: You have 14 days of premium usage of Cursor. After this period, you can continue using the free version.

## 3. Install Python
We'll use Python 3.12 for this course.

### Windows/macOS:
- **Download**: Visit the [Python website](https://www.python.org/downloads/) and download Python 3.12.
- **Install**: Run the installer with these important steps:
  - Check "Add Python 3.12 to PATH"
  - Choose "Customize installation"
  - Select all optional features
  - Choose "Install for all users" (recommended)

### Verification:
Open a terminal/command prompt and run:
```bash
python --version
```
You should see "Python 3.12.x"

## 4. Set Up Your Development Environment

You have two options for managing your Python environment:

### Option 1: Using Python's built-in venv (Recommended for beginners)
```bash
# Create a new virtual environment
python -m venv flask_env

# Activate the environment
# On Windows:
flask_env\Scripts\activate
# On macOS/Linux:
source flask_env/bin/activate
```

### Option 2: Using Anaconda (Optional)
Anaconda provides a more comprehensive environment management system with additional scientific computing packages.

#### Installation:
- **Download**: Go to the [Anaconda website](https://www.anaconda.com/products/individual) and download Anaconda for Python 3.12.
- **Install**: Run the installer and follow the on-screen instructions.
  - Choose "Install for all users" (recommended)
  - Add Anaconda to PATH (recommended)

#### Create and Activate Environment:
```bash
# Create a new environment
conda create -n flask_env python=3.12

# Activate the environment
conda activate flask_env
```

### Verification (for both options):
```bash
# Verify Python version
python --version

# Verify environment is active (should show flask_env)
which python  # On macOS/Linux
where python  # On Windows
```

### Install Required Packages
In your activated environment (using either venv or conda), run:
```bash
pip install pandas numpy flask openai chromadb jupyter ipykernel
```

### Verify Package Installation:
```bash
# Test Flask installation
python -c "import flask; print(flask.__version__)"
# Test other packages
python -c "import pandas as pd; import numpy as np; import openai; print('All packages installed successfully')"
```

## 5. Configure Cursor IDE

### Install Required Extensions
1. Open Cursor
2. Go to Extensions (sidebar)
3. Install these essential extensions:
   - Python
   - Jupyter

### Configure Python Interpreter
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose the `flask_env` environment you created

## 6. Best Practices

### Version Control
- Initialize Git in your project directory
- Create a `.gitignore` file
- Make regular commits with meaningful messages

### Virtual Environment
- Always work in your virtual environment
- Keep `requirements.txt` up to date
- Document all dependencies

### Code Organization
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add comments and docstrings
- Write tests for your code

## Need Help?
If you encounter any issues during setup:
1. Ask Cursor or ChatGPT
2. Search for similar issues online
3. Contact your instructor
