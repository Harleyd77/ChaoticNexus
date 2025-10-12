from __future__ import annotations

from flask import Flask

from .core.config import configure_app
from .core.db import init_db
from .core.errors import register_error_handlers
from .core.security import register_security
from .core.templates import ensure_template_encoding, register_template_utils
from .blueprints import admin, auth, base, intake, customers, jobs, powders, sprayer, customer_portal, react_frontend, migrate, print_templates, inventory

_ALIAS_MAP = [
    # Core navigation
    ("base.favicon", "favicon"),
    ("base.home", "home"),
    ("base.nav", "nav"),
    ("base.uploaded_file", "uploaded_file"),
    # Auth
    ("auth.login", "login"),
    ("auth.logout", "logout"),
    ("auth.customer_login", "customer_login"),
    # Intake
    ("intake.intake_form", "intake_form"),
    ("intake.railing_intake", "railing_intake"),
    ("intake.submit_form", "submit_form"),
    # Customers
    ("customers.customers_search", "customers_search"),
    ("customers.customers_page", "customers_page"),
    ("customers.customers_save", "customers_save"),
    ("customers.customers_delete", "customers_delete"),
    ("customers.contacts_json", "contacts_json"),
    ("customers.contacts_add", "contacts_add"),
    ("customers.contacts_save", "contacts_save"),
    ("customers.contacts_delete", "contacts_delete"),
    ("customers.customer_detail", "customer_detail"),
    ("customers.customer_detail_save", "customer_detail_save"),
    # Jobs
    ("jobs.jobs_board", "jobs_board"),
    ("jobs.job_photos_json", "job_photos_json"),
    ("jobs.jobs_reorder", "jobs_reorder"),
    ("jobs.jobs_screen", "jobs_screen"),
    ("jobs.jobs_completed", "jobs_completed"),
    ("jobs.jobs_screen_add", "jobs_screen_add"),
    ("jobs.jobs_screen_remove", "jobs_screen_remove"),
    ("jobs.jobs_screen_reorder", "jobs_screen_reorder"),
    ("jobs.jobs_csv", "jobs_csv"),
    ("jobs.edit_job", "edit_job"),
    ("jobs.job_photos_upload", "job_photos_upload"),
    ("jobs.job_photo_delete", "job_photo_delete"),
    ("jobs.archive_job", "archive_job"),
    ("jobs.unarchive_job", "unarchive_job"),
    ("jobs.jobs_complete", "jobs_complete"),
    ("jobs.jobs_reopen", "jobs_reopen"),
    ("jobs.jobs_delete", "jobs_delete"),
    ("jobs.job_detail", "job_detail"),
    ("jobs.job_workorder", "job_workorder"),
    ("jobs.job_workorder_save", "job_workorder_save"),
    # Powders
    ("powders.powders_page", "powders_page"),
    ("powders.powder_edit", "powder_edit"),
    ("powders.powder_new", "powder_new"),
    ("powders.powders_save", "powders_save"),
    ("powders.powders_delete", "powders_delete"),
    ("powders.powders_upload", "powders_upload"),
    ("powders.powders_csv", "powders_csv"),
    ("powders.powders_families", "powders_families"),
    ("powders.powders_colors_full", "powders_colors_full"),
    ("powders.powders_by_color", "powders_by_color"),
    ("powders.powder_detail_json", "powder_detail_json"),
    # Sprayer
    ("sprayer.sprayer_hit_list", "sprayer_hit_list"),
    ("sprayer.sprayer_batches", "sprayer_batches"),
    ("sprayer.sprayer_batches_start", "sprayer_batches_start"),
    ("sprayer.sprayer_batch_detail", "sprayer_batch_detail"),
    ("sprayer.sprayer_candidates_json", "sprayer_candidates_json"),
    ("sprayer.sprayer_hitlist_json", "sprayer_hitlist_json"),
    ("sprayer.sprayer_batch_add_job", "sprayer_batch_add_job"),
    ("sprayer.sprayer_job_start", "sprayer_job_start"),
    ("sprayer.sprayer_job_end", "sprayer_job_end"),
    ("sprayer.sprayer_job_remove", "sprayer_job_remove"),
    ("sprayer.sprayer_batch_close", "sprayer_batch_close"),
    # Admin / settings
    ("admin.admin_dbinfo", "admin_dbinfo"),
    ("admin.admin_panel", "admin_panel"),
    ("admin.admin_ui_save", "admin_ui_save"),
    ("admin.admin_branding_favicon_upload", "admin_branding_favicon_upload"),
    ("admin.admin_branding_favicon_clear", "admin_branding_favicon_clear"),
    ("admin.admin_branding_login_bg_upload", "admin_branding_login_bg_upload"),
    ("admin.admin_branding_login_bg_clear", "admin_branding_login_bg_clear"),
    ("admin.admin_branding_login_title_save", "admin_branding_login_title_save"),
    ("admin.admin_powder_options_save", "admin_powder_options_save"),
    ("admin.admin_work_order_options_save", "admin_work_order_options_save"),
    ("admin.intake_config", "get_intake_config"),
    ("admin.save_intake_config", "save_intake_config"),
    ("admin.railing_config", "get_railing_config"),
    ("admin.save_railing_config", "save_railing_config"),
    ("admin.admin_users", "admin_users"),
    ("admin.admin_users_add", "admin_users_add"),
    ("admin.admin_users_delete", "admin_users_delete"),
    ("admin.admin_users_toggle", "admin_users_toggle"),
    ("admin.admin_users_set_password", "admin_users_set_password"),
    ("admin.admin_users_set_perms", "admin_users_set_perms"),
    # Inventory
    ("inventory.inventory_page", "inventory_page"),
    ("inventory.reorder_list", "reorder_list"),
    ("inventory.update_inventory", "update_inventory"),
    ("inventory.adjust_inventory", "adjust_inventory"),
    ("inventory.inventory_history", "inventory_history"),
]

def _alias_endpoint(app: Flask, new: str, legacy: str) -> None:
    view = app.view_functions.get(new)
    if not view:
        return
    app.view_functions[legacy] = view
    rules = [rule for rule in app.url_map.iter_rules() if rule.endpoint == new]
    if rules:
        app.url_map._rules_by_endpoint[legacy] = rules

def _register_legacy_endpoint_aliases(app: Flask) -> None:
    for new_endpoint, legacy_endpoint in _ALIAS_MAP:
        _alias_endpoint(app, new_endpoint, legacy_endpoint)

def create_app() -> Flask:
    app = Flask(__name__)
    configure_app(app)
    init_db()
    ensure_template_encoding()
    register_template_utils(app)
    register_error_handlers(app)

    # Register blueprints before security so routes are available
    app.register_blueprint(base.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(intake.bp)
    app.register_blueprint(customers.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(powders.bp)
    app.register_blueprint(sprayer.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(migrate.bp)
    app.register_blueprint(customer_portal.customer_portal_bp)
    app.register_blueprint(react_frontend.react_bp)
    app.register_blueprint(print_templates.bp)
    app.register_blueprint(inventory.bp)

    # Register security after blueprints
    register_security(app)
    _register_legacy_endpoint_aliases(app)
    return app
