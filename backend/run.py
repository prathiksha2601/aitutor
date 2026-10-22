"""
run.py
Entry point for running the EIT Flask backend.
"""

import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
