"""HTTP endpoints for print templates JSON APIs (legacy parity)."""

from __future__ import annotations

from flask import jsonify, request

from app.services.print_template_service import print_template_service

from . import bp


@bp.get("/<template_type>")
def list_by_type(template_type: str):
    items = print_template_service.list_by_type(template_type)
    return jsonify(
        [
            {"id": t.id, "name": t.name, "content": t.content, "is_default": bool(t.is_default)}
            for t in items
        ]
    )


@bp.get("/<template_type>/all")
def list_all(template_type: str):
    items = print_template_service.list_all(template_type)
    return jsonify(
        [
            {"id": t.id, "name": t.name, "content": t.content, "is_default": bool(t.is_default)}
            for t in items
        ]
    )


@bp.post("")
def create():
    payload = request.get_json(silent=True) or {}
    tpl = print_template_service.create(
        payload.get("template_type", ""),
        payload.get("name", ""),
        payload.get("content", ""),
    )
    return (
        jsonify({"id": tpl.id, "name": tpl.name, "content": tpl.content, "is_default": False}),
        201,
    )


@bp.delete("/<int:template_id>")
def delete(template_id: int):
    ok = print_template_service.delete(template_id)
    return (jsonify({"ok": ok}), 200 if ok else 404)


@bp.post("/<int:template_id>/set-default")
def set_default(template_id: int):
    ok = print_template_service.set_default(template_id)
    return (jsonify({"ok": ok}), 200 if ok else 404)
