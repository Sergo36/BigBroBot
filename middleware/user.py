from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from data.models.user import User


class UsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        state = await data['state'].get_data()
        user = state.get('user')

        if user is None:
            database_user = User.get_or_none(User.telegram_id == data['event_from_user'].id)
        else:
            return await handler(event, data)

        if database_user is None:
            database_user = User.create(
                telegram_id=data['event_from_user'].id,
                telegram_name=data['event_from_user'].username)
            database_user.save()
            await data['state'].update_data(user=database_user)
        else:
            await data['state'].update_data(user=database_user)

        return await handler(event, data)
