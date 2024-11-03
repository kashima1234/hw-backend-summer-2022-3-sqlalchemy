from aiohttp_apispec import request_schema, response_schema

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.utils import error_json_response, json_response
from constants import SESSION_NAME


class AdminLoginView(View):
    @request_schema(AdminSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        data = await self.request.json()
        email = data.get("email")
        password = data.get("password")

        if email is None:
            return error_json_response(
                http_status=400,
                status="bad_request",
                message="Unprocessable Entity",
                data={"json": {"email": ["Missing data for required field."]}},
            )
        elif email == password:
            self.response = error_json_response(http_status=403,
                                                status="forbidden",
                                                message="Unprocessable Entity",
                                                data={"json": "Password is the same as email."}, )
            return self.response
        else:
            response = json_response(
                data={
                    "id": 1,
                    "email": email,
                }
            )
            response.set_cookie(SESSION_NAME, self.request.app.config.session.key)
            return response


class AdminCurrentView(View):
    @response_schema(AdminSchema, 200)
    async def get(self):
        if self.request.cookies.get(SESSION_NAME) is None:
            return error_json_response(
                http_status=401,
                status="unauthorized",
                message="No authorization data"
            )
        else:
            return json_response(
                data={
                    "id": 1,
                    "email": self.request.app.config.admin.email
                }
            )
