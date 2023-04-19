from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from data.database import get_user, set_user


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
            database_user = get_user(data['event_from_user'].id)
        else:
            return await handler(event, data)

        if database_user is None:
            database_user = set_user(data['events_from_user'].id, data['event_from_user'].username)
            await data['state'].update_data(user=database_user)
        else:
            await data['state'].update_data(user=database_user)

        return await handler(event, data)
