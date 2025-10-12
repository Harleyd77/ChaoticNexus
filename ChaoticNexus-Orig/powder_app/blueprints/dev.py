"""
Dev/Diagnostics Blueprint for MCP Chrome DevTools
Provides health check and self-test checklist endpoints
"""

from __future__ import annotations

from flask import Blueprint, jsonify

bp = Blueprint("dev", __name__, url_prefix="/dev")


@bp.route("/health")
def health():
    """Simple health check endpoint"""
    return "OK", 200, {"Content-Type": "text/plain"}


@bp.route("/mcp-checklist.json")
def mcp_checklist():
    """
    Returns JSON checklist for MCP Chrome DevTools validation
    Describes critical selectors and expected UI states
    """
    checklist = {
        "version": "1.0.0",
        "paths": ["/customers", "/customers/<id>"],
        "selectors": {
            # Customers List Page
            "customerCard": "[data-testid='customer-card']",
            "expandCard": "[data-testid='expand-card']",
            "viewMore": "[data-testid='view-more']",
            "kpis": {
                "active": "[data-testid='kpi-active']",
                "turnaround": "[data-testid='kpi-turnaround']",
                "onTime": "[data-testid='kpi-ontime']",
                "month": "[data-testid='kpi-month']",
                "revenue": "[data-testid='kpi-revenue']",
                "redo": "[data-testid='kpi-redo']",
            },
            "recentJobsTable": "[data-testid='recent-jobs-table']",
            # Theme System
            "themeMenu": "[data-testid='theme-menu']",
            "themeOptions": {
                "dark": "[data-testid='theme-option-dark']",
                "light": "[data-testid='theme-option-light']",
                "vpc": "[data-testid='theme-option-vpc']",
                "vpcLight": "[data-testid='theme-option-vpc-light']",
                "chaos": "[data-testid='theme-option-chaos']",
                "chaosLight": "[data-testid='theme-option-chaos-light']",
            },
            # Customer Profile Page
            "editToggle": "[data-testid='edit-toggle']",
            "saveButton": "[data-testid='save']",
            "cancelButton": "[data-testid='cancel']",
            "unsavedGuard": "[data-testid='unsaved-guard']",
            "toast": "[data-testid='toast']",
        },
        "assertions": [
            "at least 1 customer-card exists on /customers",
            "expanding a card reveals KPIs and recent-jobs-table",
            "clicking expand-card toggles aria-expanded attribute",
            "theme switcher toggles classes on <html> element",
            "theme selection persists to localStorage",
            "profile page opens in view/locked mode (fields disabled)",
            "clicking edit-toggle enables fields and shows save/cancel buttons",
            "navigating away with unsaved changes triggers confirmation",
            "successful save shows toast notification",
        ],
        "notes": [
            "All diagnostics run only when ?mcp_check=1 query parameter is present",
            "Console markers use [MCP-OK] and [MCP-ERR] prefixes",
            "window.__MCP_RESULTS__ object available after test run",
            "Motion respects prefers-reduced-motion setting",
        ],
    }

    return jsonify(checklist)
