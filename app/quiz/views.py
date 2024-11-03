from aiohttp.web_routedef import delete
from aiohttp_apispec import querystring_schema, request_schema, response_schema
from sqlalchemy import text, select

from app.quiz.models import AnswerModel, QuestionModel
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.utils import error_json_response, json_response
from constants import SESSION_NAME


class ThemeAddView(View):
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        data = await self.request.json()
        if self.request.cookies.get(SESSION_NAME) is None:
            return error_json_response(
                http_status=401,
                status="unauthorized",
                message="No authorization data"
            )
        elif data == {}:
            return error_json_response(
                http_status=400,
                status="bad_request",
                message="Unprocessable Entity",
                data={"json": {"title": ["Missing data for required field."]}}
            )
        elif await self.store.quizzes.get_theme_by_title(data["title"]):
            return error_json_response(
                http_status=409,
                status="conflict",
                message="Theme with such title already exists"
            )
        else:
            theme = await self.store.quizzes.create_theme(title=data["title"])
            return json_response(
                data={
                    "id": theme.id,
                    "title": theme.title
                })


class ThemeListView(View):
    @response_schema(ThemeListSchema)
    async def get(self):
        if self.request.cookies.get(SESSION_NAME) is None:
            return error_json_response(
                http_status=401,
                status="unauthorized",
                message="No authorization data"
            )
        else:
            data = {
                "themes": []
            }
            for theme in await self.store.quizzes.list_themes():
                data["themes"].append({"id": theme.id, "title": theme.title})
            return json_response(
                data=data
            )


class QuestionAddView(View):
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = await self.request.json()
        answers = []
        title = data["title"]
        theme_id = data["theme_id"]

        for answer in data["answers"]:
            answers.append(AnswerModel(title=answer["title"], is_correct=answer["is_correct"]))

        if self.request.cookies.get(SESSION_NAME) is None:
            return error_json_response(
                http_status=401,
                status="unauthorized",
                message="No authorization data"
            )
        elif await self.store.quizzes.get_theme_by_id(theme_id) is None:
            return error_json_response(
                http_status=404,
                status="not_found",
                message="Such questions's theme doesn't exist"
            )
        elif (len(answers) == 1 or all(not answer.is_correct for answer in answers)
              or sum(answer.is_correct for answer in answers) > 1):
            return error_json_response(
                http_status=400,
                status="bad_request",
                message="Bad answers"
            )
        else:
            created_question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
            return json_response(
                data={
                    "id": created_question.id,
                    "title": created_question.title,
                    "theme_id": created_question.theme_id,
                    "answers": data["answers"]
                }
            )


class QuestionListView(View):
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        if self.request.cookies.get(SESSION_NAME) is None:
            async with self.database.session.begin() as session:
                await session.execute(
                    text("""DELETE FROM questions""")
                )
                await session.execute(
                    text("""DELETE FROM answers""")
                )
            return error_json_response(
                http_status=401,
                status="unauthorized",
                message="No authorization data"
            )
        else:
            data = {
                "questions": []
            }
            for question in await self.store.quizzes.list_questions():
                async with self.database.session.begin() as session:
                    result = await session.execute(
                        select(AnswerModel).where(AnswerModel.question_id == question.id)
                    )
                answers = []
                for answer in result.scalars().all():
                    answers.append({"title": answer.title, "is_correct": answer.is_correct})
                data["questions"].append({"id": question.id, "title": question.title,
                                          "theme_id": question.theme_id, "answers": answers})

            return json_response(data=data)