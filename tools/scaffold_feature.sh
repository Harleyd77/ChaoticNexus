#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <feature-name>" >&2
  exit 1
fi

FEATURE_RAW="$1"
FEATURE_SLUG="$(echo "$FEATURE_RAW" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr '-' '_')"
FEATURE_CLASS="$(python3 - <<PY
import re
raw = "${FEATURE_SLUG}"
parts = [p for p in re.split(r"[_\-]", raw) if p]
print(''.join(s.title() for s in parts) or 'Feature')
PY
)"

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BLUEPRINT_DIR="$BASE_DIR/app/blueprints/${FEATURE_SLUG}"
TEMPLATE_DIR="$BLUEPRINT_DIR/templates/${FEATURE_SLUG}"
STATIC_DIR="$BLUEPRINT_DIR/static/${FEATURE_SLUG}"

mkdir -p "$BLUEPRINT_DIR" "$TEMPLATE_DIR" "$STATIC_DIR"

# __init__.py
cat > "$BLUEPRINT_DIR/__init__.py" <<PY
"""${FEATURE_CLASS} blueprint package."""
from flask import Blueprint

bp = Blueprint(
    "${FEATURE_SLUG}",
    __name__,
    url_prefix="/${FEATURE_SLUG}",
    template_folder="templates",
    static_folder="static",
)

from . import views  # noqa: E402,F401
PY

# views.py
cat > "$BLUEPRINT_DIR/views.py" <<PY
"""HTTP endpoints for the ${FEATURE_CLASS} blueprint."""
from flask import render_template

from . import bp


@bp.get("/")
def index():
    """Landing page for ${FEATURE_SLUG}."""
    return render_template("${FEATURE_SLUG}/index.html")
PY

# service.py (stub)
cat > "$BLUEPRINT_DIR/service.py" <<PY
"""Service layer for ${FEATURE_CLASS}."""

from app.services.base import Service


class ${FEATURE_CLASS}Service(Service):
    """Domain-specific behaviour for ${FEATURE_SLUG}."""

    def example(self) -> str:
        return "${FEATURE_CLASS} placeholder"
PY

# forms.py (optional stub)
cat > "$BLUEPRINT_DIR/forms.py" <<PY
"""Flask-WTF forms for ${FEATURE_CLASS}. Add form classes as needed."""

# from flask_wtf import FlaskForm
# from wtforms import StringField
# from wtforms.validators import DataRequired


# class ExampleForm(FlaskForm):
#     name = StringField("Name", validators=[DataRequired()])
PY

# Template stub
cat > "$TEMPLATE_DIR/index.html" <<HTML
{% extends "_layouts/base.html" %}

{% block title %}${FEATURE_CLASS}{% endblock %}

{% block content %}
<section class="space-y-4">
  <header>
    <h1 class="text-2xl font-semibold">${FEATURE_CLASS}</h1>
    <p class="text-muted-foreground">Scaffolded feature placeholder.</p>
  </header>
  <div class="rounded border border-dashed border-slate-400/50 p-6 text-sm">
    Customize this template under <code>${FEATURE_SLUG}/index.html</code>.
  </div>
</section>
{% endblock %}
HTML

# Static placeholder
cat > "$STATIC_DIR/README.md" <<MD
# ${FEATURE_CLASS} static assets

Place CSS/JS specific to this feature in this directory.
MD

chmod -R u+rw "$BLUEPRINT_DIR"

echo "Add the following to app/__init__.py:" >&2
echo "from app.blueprints.${FEATURE_SLUG} import bp as ${FEATURE_SLUG}_bp" >&2
echo "    app.register_blueprint(${FEATURE_SLUG}_bp)" >&2
