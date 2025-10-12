from __future__ import annotations

import json
import os
import re
from datetime import datetime
from types import SimpleNamespace

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from ..core.branding import get_branding_settings, save_branding_settings
from ..core.config import DB_PATH, PGDATABASE, PGHOST, PGPASSWORD, PGPORT, PGUSER, UPLOADS_DIR
from ..core.templates import STATIC_ROOT
from ..core.db import (
    INTEGRITY_ERRORS,
    connect,
    db_execute,
    db_query_all,
    db_query_one,
    get_ui_settings,
    is_postgres,
    save_ui_settings,
)
from ..core.options import (
    get_intake_config_payload,
    get_powder_options,
    get_railing_config_payload,
    get_work_order_options,
    save_intake_config_payload,
    save_powder_options,
    save_railing_config_payload,
    save_work_order_options,
)
from ..core.security import PERM_DEFAULTS, is_admin, require_admin

bp = Blueprint("admin", __name__)


def _parse_list_field(name: str) -> list[str]:
    raw = request.form.get(name) or ""
    parts = re.split(r"[\r\n,]+", raw)
    output: list[str] = []
    seen = set()
    for token in parts:
        value = (token or "").strip()
        if not value:
            continue
        lower = value.lower()
        if lower in seen:
            continue
        seen.add(lower)
        output.append(value)
    return output


@bp.route("/admin/dbinfo")
def admin_dbinfo():
    if not is_admin():
        return require_admin()
    meta = {
        "backend": "postgres",
        "host": PGHOST,
        "port": PGPORT,
        "database": PGDATABASE,
        "user": PGUSER,
    }
    counts = {}
    try:
        conn = connect()
        cursor = conn.cursor()
        for table in ("jobs", "customers", "powders", "settings", "users"):
            try:
                row = cursor.execute(f"SELECT COUNT(*) AS total FROM {table}").fetchone()
                counts[table] = row["total"] if row is not None else 0
            except Exception:
                counts[table] = "n/a"
        conn.close()
    except Exception:
        pass
    return jsonify({"meta": meta, "counts": counts})


@bp.route("/admin/logos/list")
def admin_logos_list():
    """Return list of logos from static/logos folder"""
    if not is_admin():
        return jsonify({"error": "Admin access required"}), 403
    logos_dir = STATIC_ROOT / "logos"
    logos = []
    if logos_dir.exists():
        allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".gif"}
        for file in sorted(logos_dir.iterdir()):
            if file.is_file() and file.suffix.lower() in allowed_exts:
                logos.append({
                    "name": file.name,
                    "url": url_for("static", filename=f"logos/{file.name}"),
                    "size": file.stat().st_size,
                })
    return jsonify({"logos": logos})


@bp.route("/admin/branding/select_logo", methods=["POST"])
def admin_branding_select_logo():
    """Select an existing logo from static/logos folder"""
    guard = require_admin()
    if guard:
        return guard
    logo_type = request.form.get("logo_type")  # 'favicon' or 'page_logo'
    logo_name = request.form.get("logo_name")
    
    if logo_type not in ["favicon", "page_logo"]:
        flash("Invalid logo type.", "error")
        return redirect(url_for("admin_panel"))
    
    if not logo_name:
        flash("No logo selected.", "error")
        return redirect(url_for("admin_panel"))
    
    # Verify the logo exists
    logo_path = STATIC_ROOT / "logos" / logo_name
    if not logo_path.exists() or not logo_path.is_file():
        flash("Selected logo not found.", "error")
        return redirect(url_for("admin_panel"))
    
    # Save as static reference (not uploaded file)
    data = get_branding_settings()
    data[logo_type] = f"static:logos/{logo_name}"
    save_branding_settings(data)
    flash(f"{'Favicon' if logo_type == 'favicon' else 'Page logo'} updated.", "success")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/print-templates")
def print_templates_admin():
    """Admin page for managing print templates."""
    if not is_admin():
        return redirect(url_for("login", next=url_for("admin.print_templates_admin")))
    return render_template("print_templates_admin.html")


@bp.route("/admin")
def admin_panel():
    if not is_admin():
        return redirect(url_for("login", next=url_for("admin_panel")))
    ui = get_ui_settings()
    branding = get_branding_settings()
    saved = request.args.get("saved") == "1"
    inline = """
    <!doctype html><html><head><meta charset=\"utf-8\"><title>Admin Panel</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>
    <style>
      body{margin:0;font-family:system-ui,Segoe UI,Roboto,Arial;background:#0e141b;color:#e6edf3;padding:20px}
      .wrap{max-width:900px;margin:0 auto}
      .btn{display:inline-block;padding:8px 12px;border-radius:10px;border:1px solid #1f2a37;
           background:#0f1720;color:#9fb0c0;text-decoration:none}
      .btn.primary{background:#3b82f6;border-color:transparent;color:#fff}
      .card{background:linear-gradient(180deg,#111923,#0f1720);border:1px solid #1f2a37;border-radius:14px;padding:18px;margin-bottom:12px}
      .ok{color:#cff7e1;background:#0b3a2a;border:1px solid #135a3f;padding:8px;border-radius:10px;margin-bottom:12px}
      label span{color:#9fb0c0;font-size:13px;display:block;margin-top:4px}
      .row{display:flex;justify-content:space-between;align-items:center;gap:12px}
      .preview{display:flex;align-items:center;gap:12px}
      .pill{background:#1b2430;color:#c6d4e2;padding:2px 8px;border-radius:999px;font-size:12px;border:1px solid #2a3b58}
      .flash-messages{position:fixed;top:20px;right:20px;z-index:1000;display:flex;flex-direction:column;gap:10px}
      .flash-message{background:#111923;border:1px solid #3b82f6;color:#e6edf3;padding:10px 14px;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15)}
      .logo-gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:12px;margin:16px 0;max-height:300px;overflow-y:auto;padding:12px;background:#0a0e13;border:1px solid #1f2a37;border-radius:8px}
      .logo-item{position:relative;border:2px solid #1f2a37;border-radius:8px;padding:8px;cursor:pointer;transition:all 0.2s;background:#0f1720}
      .logo-item:hover{border-color:#3b82f6;background:#152233}
      .logo-item.selected{border-color:#3b82f6;background:#1a2b4a}
      .logo-item img{width:100%;height:80px;object-fit:contain;display:block;margin-bottom:6px}
      .logo-item .name{font-size:11px;color:#9fb0c0;text-align:center;word-break:break-all}
      .toggle-gallery{cursor:pointer;color:#3b82f6;font-size:13px;margin:8px 0;display:inline-block}
      .toggle-gallery:hover{text-decoration:underline}
      .hidden{display:none}
    </style></head><body>
    <div class=\"wrap\">\n      <div class=\"flash-messages\">{% with messages = get_flashed_messages(with_categories=true) %}{% if messages %}{% for category, message in messages %}<div class=\"flash-message {{ category }}\" role=\"alert\">{{ message }}</div>{% endfor %}{% endif %}{% endwith %}</div>
      <div style=\"display:flex;justify-content:space-between;margin-bottom:12px\">
        <a class=\"btn\" href=\"/nav\">Back to Nav</a>
        <a class=\"btn\" href=\"/logout\">Logout (Admin)</a>
      </div>
      {% if saved %}<div class=\"ok\">Settings saved.</div>{% endif %}
      <div class=\"card\">
        <h2 style=\"margin:0 0 10px 0\">Site Logos</h2>
        <div style=\"margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid #1f2a37\">
          <div class=\"preview\" style=\"gap:16px;margin-bottom:10px\">
            <div>
              <div class=\"pill\">Favicon (Browser Tab Icon)</div>
              <div style=\"color:#9fb0c0;font-size:13px\">PNG, JPG, WEBP, ICO, or SVG · Recommended: 32x32px</div>
            </div>
            {% if branding.favicon_url %}
              <img src=\"{{ branding.favicon_url }}\" alt=\"favicon\" style=\"width:32px;height:32px;object-fit:contain;border:1px solid #2a3b58;border-radius:4px;background:#0b1118\">
            {% else %}
              <div class=\"pill\">Using default</div>
            {% endif %}
          </div>
          <a class=\"toggle-gallery\" onclick=\"toggleGallery('favicon-gallery')\">▼ Choose from existing logos</a>
          <div id=\"favicon-gallery\" class=\"hidden\">
            <div class=\"logo-gallery\" id=\"favicon-logos-grid\">Loading...</div>
            <form method=\"post\" action=\"/admin/branding/select_logo\" id=\"favicon-select-form\" style=\"margin-top:8px\">
              <input type=\"hidden\" name=\"logo_type\" value=\"favicon\">
              <input type=\"hidden\" name=\"logo_name\" id=\"favicon-selected\" value=\"\">
              <button class=\"btn primary\" type=\"submit\" id=\"favicon-select-btn\" disabled>Select This Logo</button>
            </form>
          </div>
          <div style=\"margin-top:12px\">
            <div style=\"color:#9fb0c0;font-size:13px;margin-bottom:6px\">Or upload a new logo:</div>
            <form method=\"post\" action=\"/admin/branding/favicon\" enctype=\"multipart/form-data\" style=\"display:flex;gap:8px;align-items:center\">
              <input type=\"file\" name=\"file\" accept=\"image/png,image/jpeg,image/webp,image/svg+xml,.ico\">
              <button class=\"btn primary\" type=\"submit\">Upload New</button>
            </form>
          </div>
          {% if branding.favicon_url %}
          <form method=\"post\" action=\"/admin/branding/favicon/clear\" style=\"margin-top:8px\">
            <button class=\"btn\" type=\"submit\">Clear Favicon (use default)</button>
          </form>
          {% endif %}
        </div>
        <div>
          <div class=\"preview\" style=\"gap:16px;margin-bottom:10px\">
            <div>
              <div class=\"pill\">Page Logo (Navigation & Headers)</div>
              <div style=\"color:#9fb0c0;font-size:13px\">PNG, JPG, WEBP, or SVG · Recommended: transparent background</div>
            </div>
            {% if branding.page_logo_url %}
              <img src=\"{{ branding.page_logo_url }}\" alt=\"page logo\" style=\"height:50px;width:auto;max-width:150px;object-fit:contain;border:1px solid #2a3b58;border-radius:6px;background:#0b1118;padding:4px\">
            {% else %}
              <div class=\"pill\">Using default</div>
            {% endif %}
          </div>
          <a class=\"toggle-gallery\" onclick=\"toggleGallery('pagelogo-gallery')\">▼ Choose from existing logos</a>
          <div id=\"pagelogo-gallery\" class=\"hidden\">
            <div class=\"logo-gallery\" id=\"pagelogo-logos-grid\">Loading...</div>
            <form method=\"post\" action=\"/admin/branding/select_logo\" id=\"pagelogo-select-form\" style=\"margin-top:8px\">
              <input type=\"hidden\" name=\"logo_type\" value=\"page_logo\">
              <input type=\"hidden\" name=\"logo_name\" id=\"pagelogo-selected\" value=\"\">
              <button class=\"btn primary\" type=\"submit\" id=\"pagelogo-select-btn\" disabled>Select This Logo</button>
            </form>
          </div>
          <div style=\"margin-top:12px\">
            <div style=\"color:#9fb0c0;font-size:13px;margin-bottom:6px\">Or upload a new logo:</div>
            <form method=\"post\" action=\"/admin/branding/page_logo\" enctype=\"multipart/form-data\" style=\"display:flex;gap:8px;align-items:center\">
              <input type=\"file\" name=\"file\" accept=\"image/png,image/jpeg,image/webp,image/svg+xml\">
              <button class=\"btn primary\" type=\"submit\">Upload New</button>
            </form>
          </div>
          {% if branding.page_logo_url %}
          <form method=\"post\" action=\"/admin/branding/page_logo/clear\" style=\"margin-top:8px\">
            <button class=\"btn\" type=\"submit\">Clear Page Logo (use default)</button>
          </form>
          {% endif %}
        </div>
      </div>
      <div class=\"card\">
        <h2 style=\"margin:0 0 10px 0\">Login Branding</h2>
        <div class=\"preview\" style=\"gap:16px\">
          <div>
            <div class=\"pill\">Background image</div>
            <div style=\"color:#9fb0c0;font-size:13px\">PNG, JPG, WEBP, or SVG</div>
          </div>
          {% if branding.login_bg_url %}
            <img src=\"{{ branding.login_bg_url }}\" alt=\"login background\" style=\"width:120px;height:70px;object-fit:cover;border:1px solid #2a3b58;border-radius:6px;background:#0b1118\">
          {% else %}
            <div class=\"pill\">No background set</div>
          {% endif %}
        </div>
        <form method=\"post\" action=\"/admin/branding/login_bg\" enctype=\"multipart/form-data\" style=\"margin-top:10px;display:flex;gap:8px;align-items:center\">
          <input type=\"file\" name=\"file\" accept=\"image/png,image/jpeg,image/webp,image/svg+xml\">
          <button class=\"btn primary\" type=\"submit\">Upload</button>
        </form>
        {% if branding.login_bg_url %}
        <form method=\"post\" action=\"/admin/branding/login_bg/clear\" style=\"margin-top:8px\">
          <button class=\"btn\" type=\"submit\">Clear Background</button>
        </form>
        {% endif %}
        <div style=\"margin-top:14px\">
          <div class=\"pill\">Login title</div>
          <form method=\"post\" action=\"/admin/branding/login_title\" style=\"display:flex;gap:8px;margin-top:8px\">
            <input type=\"text\" name=\"title\" value=\"{{ branding.login_title }}\" placeholder=\"Site title shown on login\" style=\"flex:1\">
            <button class=\"btn primary\" type=\"submit\">Save</button>
          </form>
        </div>
      </div>
      <div class=\"card\">
        <h2 style=\"margin-top:0\">Navigation Toggles</h2>
        <form method=\"post\" action=\"/admin/ui\">
          <label>
            <input type=\"checkbox\" name=\"show_csv\" {% if ui.show_csv %}checked{% endif %}> Show CSV exports button on Nav
            <span>Allows CSV export links for jobs/powders/customers.</span>
          </label>
          <button class=\"btn primary\" type=\"submit\" style=\"margin-top:10px\">Save Toggles</button>
        </form>
      </div>
      <div class=\"card\">
        <h2 style=\"margin-top:0\">Print Templates</h2>
        <p style=\"color:#9fb0c0;font-size:13px;margin:8px 0 12px 0\">
          Manage custom print layouts for worksheets and intake forms. Set different templates for each form type.
        </p>
        <a class=\"btn primary\" href=\"/admin/print-templates\">Manage Print Templates</a>
      </div>
    </div>
    <script>
    let logosData = [];
    
    function toggleGallery(galleryId) {
      const gallery = document.getElementById(galleryId);
      const isHidden = gallery.classList.contains('hidden');
      gallery.classList.toggle('hidden');
      
      if (isHidden && logosData.length === 0) {
        loadLogos();
      }
    }
    
    function loadLogos() {
      fetch('/admin/logos/list')
        .then(r => r.json())
        .then(data => {
          logosData = data.logos || [];
          renderGallery('favicon-logos-grid', 'favicon');
          renderGallery('pagelogo-logos-grid', 'page_logo');
        })
        .catch(err => {
          console.error('Failed to load logos:', err);
          document.getElementById('favicon-logos-grid').innerHTML = '<div style=\"color:#ef4444;padding:12px\">Failed to load logos</div>';
          document.getElementById('pagelogo-logos-grid').innerHTML = '<div style=\"color:#ef4444;padding:12px\">Failed to load logos</div>';
        });
    }
    
    function renderGallery(gridId, logoType) {
      const grid = document.getElementById(gridId);
      if (logosData.length === 0) {
        grid.innerHTML = '<div style=\"color:#9fb0c0;padding:12px\">No logos found in static/logos folder</div>';
        return;
      }
      
      grid.innerHTML = logosData.map(logo => `
        <div class=\"logo-item\" onclick=\"selectLogo('${logoType}', '${logo.name}')\">
          <img src=\"${logo.url}\" alt=\"${logo.name}\" onerror=\"this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100\\' height=\\'100\\'%3E%3Ctext x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\'%3E?%3C/text%3E%3C/svg%3E'\">
          <div class=\"name\">${logo.name}</div>
        </div>
      `).join('');
    }
    
    function selectLogo(logoType, logoName) {
      const gridId = logoType === 'favicon' ? 'favicon-logos-grid' : 'pagelogo-logos-grid';
      const grid = document.getElementById(gridId);
      const items = grid.querySelectorAll('.logo-item');
      items.forEach(item => item.classList.remove('selected'));
      
      event.currentTarget.classList.add('selected');
      
      const selectedInput = document.getElementById(logoType === 'favicon' ? 'favicon-selected' : 'pagelogo-selected');
      const submitBtn = document.getElementById(logoType === 'favicon' ? 'favicon-select-btn' : 'pagelogo-select-btn');
      
      selectedInput.value = logoName;
      submitBtn.disabled = false;
    }
    </script>
    </body></html>
    """
    login_bg = branding.get("login_bg")
    favicon = branding.get("favicon")
    page_logo = branding.get("page_logo")
    
    # Handle both uploaded files and static file references
    favicon_url = ""
    if favicon:
        if favicon.startswith("static:"):
            favicon_url = url_for("static", filename=favicon.replace("static:", ""))
        else:
            favicon_url = url_for("uploaded_file", name=favicon)
    
    page_logo_url = ""
    if page_logo:
        if page_logo.startswith("static:"):
            page_logo_url = url_for("static", filename=page_logo.replace("static:", ""))
        else:
            page_logo_url = url_for("uploaded_file", name=page_logo)
    
    branding_context = {
        "login_bg_url": url_for("uploaded_file", name=login_bg) if login_bg else "",
        "login_title": branding.get("login_title") or "Victoria Powder Coating Ltd",
        "favicon_url": favicon_url,
        "page_logo_url": page_logo_url,
    }
    return render_template_string(
        inline,
        ui=SimpleNamespace(**ui),
        branding=SimpleNamespace(**branding_context),
        saved=saved,
    )


@bp.route("/admin/ui", methods=["POST"])
def admin_ui_save():
    guard = require_admin()
    if guard:
        return guard
    show_csv = request.form.get("show_csv") == "on"
    ui = get_ui_settings()
    ui["show_csv"] = show_csv
    save_ui_settings(ui)
    return redirect(url_for("admin_panel", saved=1))


@bp.route("/admin/branding/favicon", methods=["POST"])
def admin_branding_favicon_upload():
    guard = require_admin()
    if guard:
        return guard
    file = request.files.get("file")
    if not file or not getattr(file, "filename", None):
        flash("No file selected", "error")
        return redirect(url_for("admin_panel"))
    filename = file.filename
    allowed = {"png", "jpg", "jpeg", "webp", "svg", "ico"}
    if "." not in filename or filename.rsplit(".", 1)[-1].lower() not in allowed:
        flash("Unsupported file type. Use PNG, JPG, WEBP, SVG, or ICO.", "error")
        return redirect(url_for("admin_panel"))
    try:
        ext = filename.rsplit(".", 1)[-1].lower()
        base = secure_filename(os.path.splitext(filename)[0]) or "favicon"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = f"{base[:40]}-{timestamp}.{ext}"
        branding_dir = os.path.join(UPLOADS_DIR, "branding")
        os.makedirs(branding_dir, exist_ok=True)
        path = os.path.join(branding_dir, safe_name)
        file.save(path)
        data = get_branding_settings()
        data["favicon"] = os.path.join("branding", safe_name)
        save_branding_settings(data)
        flash("Favicon updated.", "success")
    except Exception:
        flash("Failed to upload favicon.", "error")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/branding/favicon/clear", methods=["POST"])
def admin_branding_favicon_clear():
    guard = require_admin()
    if guard:
        return guard
    data = get_branding_settings()
    data.pop("favicon", None)
    save_branding_settings(data)
    flash("Favicon cleared.", "success")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/branding/page_logo", methods=["POST"])
def admin_branding_page_logo_upload():
    guard = require_admin()
    if guard:
        return guard
    file = request.files.get("file")
    if not file or not getattr(file, "filename", None):
        flash("No file selected", "error")
        return redirect(url_for("admin_panel"))
    filename = file.filename
    allowed = {"png", "jpg", "jpeg", "webp", "svg"}
    if "." not in filename or filename.rsplit(".", 1)[-1].lower() not in allowed:
        flash("Unsupported file type. Use PNG, JPG, WEBP, or SVG.", "error")
        return redirect(url_for("admin_panel"))
    try:
        ext = filename.rsplit(".", 1)[-1].lower()
        base = secure_filename(os.path.splitext(filename)[0]) or "logo"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = f"{base[:40]}-{timestamp}.{ext}"
        branding_dir = os.path.join(UPLOADS_DIR, "branding")
        os.makedirs(branding_dir, exist_ok=True)
        path = os.path.join(branding_dir, safe_name)
        file.save(path)
        data = get_branding_settings()
        data["page_logo"] = os.path.join("branding", safe_name)
        save_branding_settings(data)
        flash("Page logo updated.", "success")
    except Exception:
        flash("Failed to upload page logo.", "error")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/branding/page_logo/clear", methods=["POST"])
def admin_branding_page_logo_clear():
    guard = require_admin()
    if guard:
        return guard
    data = get_branding_settings()
    data.pop("page_logo", None)
    save_branding_settings(data)
    flash("Page logo cleared.", "success")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/branding/login_bg", methods=["POST"])
def admin_branding_login_bg_upload():
    guard = require_admin()
    if guard:
        return guard
    file = request.files.get("file")
    if not file or not getattr(file, "filename", None):
        flash("No file selected", "error")
        return redirect(url_for("admin_panel"))
    filename = file.filename
    allowed = {"png", "jpg", "jpeg", "webp", "svg"}
    if "." not in filename or filename.rsplit(".", 1)[-1].lower() not in allowed:
        flash("Unsupported file type. Use PNG, JPG, WEBP, or SVG.", "error")
        return redirect(url_for("admin_panel"))
    try:
        ext = filename.rsplit(".", 1)[-1].lower()
        base = secure_filename(os.path.splitext(filename)[0]) or "login"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = f"{base[:40]}-{timestamp}.{ext}"
        branding_dir = os.path.join(UPLOADS_DIR, "branding")
        os.makedirs(branding_dir, exist_ok=True)
        path = os.path.join(branding_dir, safe_name)
        file.save(path)
        data = get_branding_settings()
        data["login_bg"] = os.path.join("branding", safe_name)
        save_branding_settings(data)
        flash("Login background updated.", "success")
    except Exception:
        flash("Failed to upload background.", "error")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/branding/login_bg/clear", methods=["POST"])
def admin_branding_login_bg_clear():
    guard = require_admin()
    if guard:
        return guard
    data = get_branding_settings()
    data.pop("login_bg", None)
    save_branding_settings(data)
    flash("Login background cleared.", "success")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/branding/login_title", methods=["POST"])
def admin_branding_login_title_save():
    guard = require_admin()
    if guard:
        return guard
    title = (request.form.get("title") or "").strip() or "Victoria Powder Coating Ltd"
    data = get_branding_settings()
    data["login_title"] = title
    save_branding_settings(data)
    flash("Login title saved.", "success")
    return redirect(url_for("admin_panel"))


@bp.route("/admin/powder-options", methods=["POST"])
def admin_powder_options_save():
    guard = require_admin()
    if guard:
        return guard
    data = {
        "color_families": _parse_list_field("color_families"),
        "manufacturers": _parse_list_field("manufacturers"),
        "gloss_levels": _parse_list_field("gloss_levels"),
        "finishes": _parse_list_field("finishes"),
        "int_ext": _parse_list_field("int_ext"),
    }
    # Handle markup percentage
    try:
        markup_str = request.form.get("markup_percentage", "").strip()
        markup_value = float(markup_str) if markup_str else 0
        data["markup_percentage"] = max(0, markup_value)  # Ensure non-negative
    except (ValueError, TypeError):
        data["markup_percentage"] = 0
    
    current = get_powder_options()
    for key in list(data.keys()):
        if key == "markup_percentage":
            continue  # Already set above
        if not data[key]:
            data[key] = current.get(key, [])
    save_powder_options(data)
    flash("Powder options updated.", "success")
    ref = request.headers.get("Referer") or request.referrer
    return redirect(ref or url_for("admin_panel", saved=1))


@bp.route("/admin/work-order-options", methods=["POST"])
def admin_work_order_options_save():
    guard = require_admin()
    if guard:
        return guard
    incoming = {
        "blast": _parse_list_field("blast"),
        "tank": _parse_list_field("tank"),
        "pretreatment": _parse_list_field("pretreatment"),
        "quote": _parse_list_field("quote"),
    }
    current = get_work_order_options()
    for key, values in incoming.items():
        if not values:
            incoming[key] = current.get(key, [])
    save_work_order_options(incoming)
    flash("Work order dropdowns updated.", "success")
    ref = request.headers.get("Referer") or request.referrer
    return redirect(ref or url_for("jobs_board"))


@bp.route("/config/intake.json")
def intake_config():
    return jsonify(get_intake_config_payload())


@bp.route("/config/intake", methods=["POST"])
def save_intake_config():
    if not is_admin():
        abort(403, description="Admin login required to save config")
    payload = request.get_json(force=True, silent=False)
    if not isinstance(payload, dict) or "options" not in payload or "required" not in payload:
        abort(400, description="Invalid payload")
    save_intake_config_payload(payload)
    return jsonify({"ok": True})


@bp.route("/config/railing.json")
def railing_config():
    return jsonify(get_railing_config_payload())


@bp.route("/config/railing", methods=["POST"])
def save_railing_config():
    if not is_admin():
        abort(403, description="Admin login required to save config")
    payload = request.get_json(force=True, silent=False)
    if not isinstance(payload, dict) or "options" not in payload or "required" not in payload:
        abort(400, description="Invalid payload")
    save_railing_config_payload(payload)
    return jsonify({"ok": True})


@bp.route("/admin/users")
def admin_users():
    guard = require_admin()
    if guard:
        return guard
    rows = db_query_all(
        "SELECT id, username, is_admin, created_at, permissions_json FROM users ORDER BY LOWER(username) ASC"
    )
    users = []
    for row in rows:
        try:
            perms = json.loads(row["permissions_json"] or "{}")
        except Exception:
            perms = {}
        users.append(
            {
                "id": row["id"],
                "username": row["username"],
                "is_admin": row["is_admin"],
                "created_at": row["created_at"],
                "perms": {**PERM_DEFAULTS, **{k: bool(v) for k, v in perms.items()}},
            }
        )
    saved = request.args.get("saved") == "1"
    err = (request.args.get("err") or "").strip()
    return render_template(
        "admin_users.html",
        users=users,
        me_username=session.get("username"),
        PERM_KEYS=list(PERM_DEFAULTS.keys()),
        saved=saved,
        err=err,
    )


@bp.route("/admin/users/add", methods=["POST"])
def admin_users_add():
    guard = require_admin()
    if guard:
        return guard
    form = request.form
    username = (form.get("username") or "").strip()
    password = form.get("password") or ""
    is_admin_flag = 1 if form.get("is_admin") == "on" else 0
    if not username or not password:
        abort(400, "username and password required")
    try:
        db_execute(
            "INSERT INTO users (username, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), is_admin_flag, datetime.now().isoformat()),
        )
    except INTEGRITY_ERRORS:
        return redirect(url_for("admin_users") + "?err=exists")
    return redirect(url_for("admin_users", saved=1))


@bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
def admin_users_delete(user_id: int):
    guard = require_admin()
    if guard:
        return guard
    me_id = session.get("user_id")
    if me_id and int(me_id) == int(user_id):
        return redirect(url_for("admin_users") + "?err=self")
    db_execute("DELETE FROM users WHERE id=?", (user_id,))
    return redirect(url_for("admin_users", saved=1))


@bp.route("/admin/users/<int:user_id>/toggle_admin", methods=["POST"])
def admin_users_toggle(user_id: int):
    guard = require_admin()
    if guard:
        return guard
    row = db_query_one("SELECT is_admin FROM users WHERE id=?", (user_id,))
    if row:
        new_val = 0 if int(row["is_admin"] or 0) else 1
        db_execute("UPDATE users SET is_admin=? WHERE id=?", (new_val, user_id))
    return redirect(url_for("admin_users", saved=1))


@bp.route("/admin/users/<int:user_id>/set_password", methods=["POST"])
def admin_users_set_password(user_id: int):
    guard = require_admin()
    if guard:
        return guard
    password = request.form.get("password") or ""
    if not password:
        return redirect(url_for("admin_users") + "?err=pw")
    db_execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(password), user_id))
    return redirect(url_for("admin_users", saved=1))


@bp.route("/admin/users/<int:user_id>/perms", methods=["POST"])
def admin_users_set_perms(user_id: int):
    guard = require_admin()
    if guard:
        return guard
    incoming = {key: 1 if request.form.get(key) == "on" else 0 for key in PERM_DEFAULTS}
    db_execute("UPDATE users SET permissions_json=? WHERE id=?", (json.dumps(incoming), user_id))
    return redirect(url_for("admin_users", saved=1))