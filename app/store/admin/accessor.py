from typing import TYPE_CHECKING

import bcrypt
from sqlalchemy import select, cast, String, text

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor
from app.web import config
from app.web.utils import error_json_response, json_response
from constants import SESSION_NAME

if TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.database = app.database

    async def connect(self, app: "Application") -> None:
        if self.database.session is None:
            await self.database.connect()
        await self.create_admin(app.config.admin.email, app.config.admin.password)

    async def get_by_email(self, email: str) -> AdminModel | None:
        async with self.database.session.begin() as session:
            result = await session.execute(
                select(AdminModel).where(AdminModel.email == email)
            )
            executed_admin = result.scalars().first()
            if executed_admin:
                return AdminModel(id=executed_admin.id, email=executed_admin.email, password=executed_admin.password)
        return None

    async def create_admin(self, email: str, password: str) -> AdminModel:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin = AdminModel(id=0, email=email, password=hashed_password)
        async with self.database.session.begin() as session:
            await session.execute(text(f"""INSERT INTO admins (id, email, "password") VALUES(nextval('admins_id_seq'::regclass), '{email}', '{hashed_password}');"""))
        return admin
