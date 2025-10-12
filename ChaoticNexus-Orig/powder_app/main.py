from __future__ import annotations

import os

from powder_app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1", host="0.0.0.0", port=5000)
