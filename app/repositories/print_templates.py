"""Repository for print templates."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select

from ..models import PrintTemplate
from .session import session_scope


class PrintTemplateRepository:
    def list_by_type(self, template_type: str) -> Iterable[PrintTemplate]:
        with session_scope() as session:
            return (
                session.execute(
                    select(PrintTemplate).filter(PrintTemplate.template_type == template_type)
                )
                .scalars()
                .all()
            )

    def list_all(self, template_type: str) -> Iterable[PrintTemplate]:
        return self.list_by_type(template_type)

    def create(self, *, template_type: str, name: str, content: str) -> PrintTemplate:
        with session_scope() as session:
            tpl = PrintTemplate(template_type=template_type, name=name, content=content)
            session.add(tpl)
            session.flush()
            return tpl

    def delete(self, template_id: int) -> bool:
        with session_scope() as session:
            tpl = session.get(PrintTemplate, template_id)
            if not tpl:
                return False
            session.delete(tpl)
            session.flush()
            return True

    def set_default(self, template_id: int) -> bool:
        with session_scope() as session:
            tpl = session.get(PrintTemplate, template_id)
            if not tpl:
                return False
            # Unset others of same type
            session.execute(
                select(PrintTemplate).filter(PrintTemplate.template_type == tpl.template_type)
            )
            for other in (
                session.execute(
                    select(PrintTemplate).filter(PrintTemplate.template_type == tpl.template_type)
                )
                .scalars()
                .all()
            ):
                other.is_default = False
            tpl.is_default = True
            session.flush()
            return True


print_template_repo = PrintTemplateRepository()
