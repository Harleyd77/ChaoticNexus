"""Service layer for print template management."""

from __future__ import annotations

from app.repositories.print_templates import print_template_repo


class PrintTemplateService:
    def __init__(self, repository=print_template_repo):
        self._repo = repository

    def list_by_type(self, template_type: str):
        return self._repo.list_by_type(template_type)

    def list_all(self, template_type: str):
        return self._repo.list_all(template_type)

    def create(self, template_type: str, name: str, content: str):
        if not template_type or not name or not content:
            raise ValueError("template_type, name, and content are required")
        return self._repo.create(template_type=template_type, name=name, content=content)

    def delete(self, template_id: int) -> bool:
        return self._repo.delete(template_id)

    def set_default(self, template_id: int) -> bool:
        return self._repo.set_default(template_id)


print_template_service = PrintTemplateService()
