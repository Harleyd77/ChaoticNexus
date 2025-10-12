from __future__ import annotations

from flask import flash, jsonify, redirect, render_template, request, url_for


class AppError(Exception):
    """Base class for application errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class ValidationError(AppError):
    """Raised when input validation fails."""


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


def _handle_app_error(error: AppError):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"error": str(error)}), error.status_code
    flash(str(error), "error")
    return redirect(request.referrer or url_for("nav"))


def _handle_404(_error):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"error": "Not found"}), 404
    return (
        render_template(
            "error.html",
            error="Page not found",
            message="The requested page could not be found.",
        ),
        404,
    )


def _handle_500(_error):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"error": "Internal server error"}), 500
    return (
        render_template(
            "error.html",
            error="Internal Server Error",
            message="An unexpected error occurred. Please try again later.",
        ),
        500,
    )


def register_error_handlers(app) -> None:
    app.register_error_handler(AppError, _handle_app_error)
    app.register_error_handler(404, _handle_404)
    app.register_error_handler(500, _handle_500)
