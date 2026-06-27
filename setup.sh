#!/bin/bash
# setup.sh — One-command local setup for SmartHire AI
# Usage: bash setup.sh

set -e  # exit on first error

echo ""
echo "============================================"
echo "  SmartHire AI — Local Setup"
echo "============================================"
echo ""

# 1. Create virtual environment
echo "[1/6] Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
echo "[2/6] Installing Python packages..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# 3. Download spaCy NLP model
echo "[3/6] Downloading spaCy language model (en_core_web_sm)..."
python -m spacy download en_core_web_sm --quiet

# 4. Set up .env
if [ ! -f .env ]; then
    echo "[4/6] Creating .env from template..."
    cp .env.example .env
    # Auto-generate a random secret key
    SECRET=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/your-secret-key-here/$SECRET/" .env
else
    echo "[4/6] .env already exists — skipping."
fi

# 5. Run migrations
echo "[5/6] Running database migrations..."
python manage.py migrate --run-syncdb

# 6. Create superuser (optional)
echo "[6/6] Setup complete!"
echo ""
echo "============================================"
echo "  Optional: create an admin user with:"
echo "  python manage.py createsuperuser"
echo ""
echo "  Start the development server with:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "  Then open: http://127.0.0.1:8000"
echo "============================================"
echo ""
