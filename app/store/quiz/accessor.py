from collections.abc import Iterable, Sequence

from sqlalchemy import text, select, insert

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    AnswerModel,
    QuestionModel,
    ThemeModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                insert(ThemeModel).values(title=title).returning(ThemeModel.id)
            )
            theme_id = result.scalar_one()
        return ThemeModel(id=theme_id, title=title)

    async def get_theme_by_title(self, title: str) -> ThemeModel | None:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                select(ThemeModel).where(ThemeModel.title == title)
            )
            executed_theme = result.scalars().first()
            if executed_theme:
                return ThemeModel(id=executed_theme.id, title=executed_theme.title)
        return None

    async def get_theme_by_id(self, id_: int) -> ThemeModel | None:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                select(ThemeModel).where(ThemeModel.id == id_)
            )
            executed_theme = result.scalars().first()
            if executed_theme:
                return ThemeModel(id=executed_theme.id, title=executed_theme.title)
        return None

    async def list_themes(self) -> Sequence[ThemeModel]:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                select(ThemeModel)
            )
            return result.scalars().all()

    async def create_question(
        self, title: str, theme_id: int, answers: Iterable[AnswerModel]
    ) -> QuestionModel:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                insert(QuestionModel).values(title=title, theme_id=theme_id).returning(QuestionModel.id)
            )
            question_id = result.scalar_one()
            for answer in answers:
                await session.execute(
                    insert(AnswerModel).values(
                        title=answer.title,
                        is_correct=answer.is_correct,
                        question_id=question_id
                    )
                )
            return QuestionModel(id=question_id, title=title, theme_id=theme_id)

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                select(QuestionModel).where(QuestionModel.title == title)
            )
            executed_question = result.scalars().first()
            if executed_question:
                return QuestionModel(id=executed_question.id, title=executed_question.title, theme_id=executed_question.theme_id)
        return None

    async def list_questions(
        self, theme_id: int | None = None
    ) -> Sequence[QuestionModel]:
        async with self.app.database.session.begin() as session:
            result = await session.execute(
                select(QuestionModel)
            )
            return result.scalars().all()
