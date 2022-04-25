"""
The MIT License (MIT)

Copyright (c) 2022-present iDevision

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, List, Type, TypeVar, Union

from discord import AppCommandType, Member, Message, User
from discord.app_commands.commands import (
    ContextMenu,
    _parse_args_from_docstring,
    _populate_autocomplete,
    _populate_choices,
    _populate_descriptions,
    _populate_renames,
    annotation_to_parameter,
)
from discord.utils import MISSING, resolve_annotation

from .commands import Command as _Command

if TYPE_CHECKING:
    from discord import Interaction
    from discord.app_commands.commands import AppCommandError, Command, CommandParameter, Choice

    AppCommand = Union[Command, ContextMenu]

CB = TypeVar('CB')


# This is all next-level cursed
def _generate_callback(cls: Union[Type[_Command], CB], fake: bool = False) -> CB:
    if inspect.isclass(cls) and issubclass(cls, _Command):
        # Context menu callback relies on the annotation, so this duplication is necessary
        # The callback reassignation is so pyright doesn't complain that I'm redefining functions
        if fake:

            async def fake_callback(interaction: Interaction):
                pass

            callback = fake_callback
        elif cls.__discord_app_commands_type__ is AppCommandType.user:

            async def user_callback(interaction: Interaction, target: Union[Member, User]):
                cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be present
                inst = cls()
                inst.interaction = interaction
                inst.target = target  # type: ignore # Runtime attribute assignment
                await inst.callback()

            callback = user_callback
        elif cls.__discord_app_commands_type__ is AppCommandType.message:

            async def message_callback(interaction: Interaction, target: Message):
                cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be present
                inst = cls()
                inst.interaction = interaction
                inst.target = target  # type: ignore # Runtime attribute assignment
                await inst.callback()

            callback = message_callback
        else:

            async def slash_callback(interaction: Interaction, **params) -> None:
                cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be present
                inst = cls()
                inst.interaction = interaction
                inst.__dict__.update(params)
                await inst.callback()

            callback = slash_callback

        return callback  # type: ignore

    return cls  # type: ignore


def _inject_callback(cls: Type[_Command], command: AppCommand) -> None:
    if isinstance(command, ContextMenu):
        return

    command._callback = _generate_callback(cls)


def _inject_error_handler(cls: Type[_Command], command: AppCommand) -> None:
    async def on_error(interaction: Interaction, error: AppCommandError) -> None:
        cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be present
        inst = cls()
        inst.interaction = interaction
        return await inst.on_error(error)

    command.on_error = on_error


def _inject_parameters(cls: Type[_Command], command: AppCommand) -> None:
    if isinstance(command, ContextMenu):
        return

    params = cls.__discord_app_commands_params__
    cache = {}
    globalns = cls.__dict__

    parameters: List[CommandParameter] = []
    for parameter in params:
        if parameter.annotation is parameter.empty:
            raise TypeError(f'Annotation for {parameter.name} must be given in comm {cls.__qualname__!r}')

        resolved = resolve_annotation(parameter.annotation, globalns, globalns, cache)
        param = annotation_to_parameter(resolved, parameter)
        parameters.append(param)

    values = sorted(parameters, key=lambda a: a.required, reverse=True)
    result = {v.name: v for v in values}

    descriptions = _parse_args_from_docstring(cls, result)

    try:
        descriptions.update(cls.__discord_app_commands_param_description__)
    except AttributeError:
        for param in values:
            if param.description is MISSING:
                param.description = '…'
    if descriptions:
        _populate_descriptions(result, descriptions)

    try:
        renames = cls.__discord_app_commands_param_rename__
    except AttributeError:
        pass
    else:
        _populate_renames(result, renames.copy())

    try:
        choices = cls.__discord_app_commands_param_choices__
    except AttributeError:
        pass
    else:
        _populate_choices(result, choices.copy())

    try:
        autocomplete = cls.__discord_app_commands_param_autocomplete__
    except AttributeError:
        pass
    else:
        _populate_autocomplete(result, autocomplete.copy())

    command._params = result


def _inject_autocomplete(cls: Type[_Command], command: AppCommand) -> None:
    if isinstance(command, ContextMenu):
        return

    try:
        autocompleted = cls.__discord_app_commands_param_autocompleted__
    except AttributeError:
        return

    async def autocomplete(interaction: Interaction, current: Any) -> List[Choice]:
        cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be present
        inst = cls()
        inst.interaction = interaction
        inst.__dict__.update(interaction.namespace.__dict__)

        for k, v in inst.__dict__.items():
            if v == current:
                return await inst.autocomplete(k)  # type: ignore # Only slash commands can have autocomplete
        return []

    _populate_autocomplete(command._params, {k: autocomplete for k in autocompleted})


def _inject_class_based_information(cls: Union[Type[_Command], Any], command: AppCommand) -> None:
    if not inspect.isclass(cls) or not issubclass(cls, _Command):
        return

    _inject_callback(cls, command)
    _inject_parameters(cls, command)
    _inject_autocomplete(cls, command)
    _inject_error_handler(cls, command)
