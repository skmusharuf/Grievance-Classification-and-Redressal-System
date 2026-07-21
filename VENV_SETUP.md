# Virtual Environment Setup Guide

## Quick Start with venv

### Step 1: Create Virtual Environment

```bash
# Navigate to project root
cd /vercel/share/v0-project

# Create virtual environment
python3 -m venv venv

# On Windows
python -m venv venv
```

### Step 2: Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

### Step 3: Verify Activation

You should see `(venv)` prefix in your terminal:
```
(venv) user@computer project %
```

### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project requirements
pip install -r requirements.txt
```

### Step 5: Train ML Models

```bash
# Navigate to backend
cd backend

# Train ML models
python ml_trainer.py

# Output should show:
# [ML] Training Department Classification Model...
# [ML] Training Criticality Classification Model...
# Models saved to: backend/models/
```

### Step 6: Initialize Database

```bash
# Create database schema
python init_db.py

# Output should show:
# Database initialized successfully!
```

### Step 7: Seed Multiple Cities

```bash
# Seed 10+ Indian cities with zones, circles, areas
python seed_multiple_cities.py

# Output should show:
# [SEED] Seeding 10 cities with zones, circles, areas...
# ✓ Database seeded successfully!
```

### Step 8: Run Backend

```bash
# Start Flask server
python run.py

# Output should show:
# ============================================================
# GRIEVANCE SYSTEM - PRODUCTION API
# ============================================================
# Environment: Development
# Port: 5000
# Debug: True
# ============================================================
# 
# * Running on http://0.0.0.0:5000
```

### Step 9: Run Frontend (New Terminal)

```bash
# Open NEW terminal window/tab
# Keep backend terminal open

# Navigate to project root
cd /vercel/share/v0-project

# Install frontend dependencies
npm install

# Start development server
npm run dev

# Output should show:
# Local:        http://localhost:3000
```

---

## Complete Setup Script (Automated)

Create a file `setup-with-venv.sh`:

```bash
#!/bin/bash

echo "=========================================="
echo "Setting up Grievance System with venv"
echo "=========================================="

# Step 1: Create venv
echo "[1/7] Creating virtual environment..."
python3 -m venv venv

# Step 2: Activate venv
echo "[2/7] Activating virtual environment..."
source venv/bin/activate

# Step 3: Install dependencies
echo "[3/7] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Step 4: Train ML models
echo "[4/7] Training ML models..."
cd backend
python ml_trainer.py

# Step 5: Initialize database
echo "[5/7] Initializing database..."
python init_db.py

# Step 6: Seed cities
echo "[6/7] Seeding cities..."
python seed_multiple_cities.py

# Step 7: Summary
cd ..
echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the system:"
echo ""
echo "Terminal 1 (Backend):"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  python run.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  npm install"
echo "  npm run dev"
echo ""
echo "Access: http://localhost:3000"
echo "=========================================="
```

Run it:
```bash
chmod +x setup-with-venv.sh
./setup-with-venv.sh
```

---

## Troubleshooting venv

### Issue: Command not found (python3)

**Solution:**
```bash
# Check if Python is installed
which python
python --version

# If not found, install Python 3.9+
# macOS: brew install python3
# Ubuntu: sudo apt-get install python3
# Windows: Download from python.org
```

### Issue: venv not activating

**Solution:**
```bash
# Check file permissions
ls -la venv/bin/activate

# Make executable
chmod +x venv/bin/activate

# Try activating again
source venv/bin/activate
```

### Issue: Permission denied when installing packages

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Try installation again
pip install -r requirements.txt
```

### Issue: Module not found after installation

**Solution:**
```bash
# Verify venv is activated (should see (venv) prefix)
source venv/bin/activate

# Check installed packages
pip list

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: Port 5000 already in use

**Solution:**
```bash
# Use different port
export PORT=5001
python run.py

# Or kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

---

## Folder Structure After Setup

```
/vercel/share/v0-project/
├── venv/                          # Virtual environment (created)
│   ├── bin/                       # Executables
│   ├── lib/                       # Installed packages
│   └── include/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── middleware/
│   │   └── models/
│   ├── models/                    # ML models (trained)
│   │   ├── department_classifier.pkl
│   │   ├── criticality_classifier.pkl
│   │   └── category_encoder.pkl
│   ├── data/
│   │   └── grievances.db          # Database (created)
│   ├── ml_trainer.py
│   ├── init_db.py
│   ├── seed_multiple_cities.py
│   ├── run.py
│   └── requirements.txt
├── frontend/
│   └── ...React components
├── npm dependencies installed
└── Documentation
    ├── API_DOCUMENTATION.md
    ├── PRODUCTION_SETUP.md
    ├── README_PRODUCTION.md
    └── VENV_SETUP.md
```

---

## Deactivating venv

When done, deactivate the virtual environment:

```bash
deactivate
```

The `(venv)` prefix will disappear.

---

## Tips & Best Practices

1. **Always activate venv before working**
   ```bash
   source venv/bin/activate
   ```

2. **Keep venv out of git** (already in .gitignore)
   ```bash
   # Check .gitignore
   cat .gitignore | grep venv
   ```

3. **Recreate venv if issues occur**
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Update requirements.txt if adding packages**
   ```bash
   pip install new-package
   pip freeze > requirements.txt
   ```

5. **Keep separate terminals open**
   - Terminal 1: Backend (running)
   - Terminal 2: Frontend (running)
   - Terminal 3: Other commands/git

---

## What Next?

After setup:

1. ✅ Access frontend: http://localhost:3000
2. ✅ Test API: http://localhost:5000/health
3. ✅ Check documentation: API_DOCUMENTATION.md
4. ✅ Run verification: VERIFICATION_CHECKLIST.md
5. ✅ Deploy to production: PRODUCTION_SETUP.md

