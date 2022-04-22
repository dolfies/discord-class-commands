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
from typing import Any, List, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from discord import AppCommandOptionType
from discord.utils import resolve_annotation, MISSING
from discord.app_commands.commands import (
    _parse_args_from_docstring,
    _populate_descriptions,
    _populate_renames,
    _populate_choices,
    _populate_autocomplete,
    annotation_to_parameter,
)
from discord.app_commands.transformers import get_supported_annotation

if TYPE_CHECKING:
    from discord import Interaction
    from discord.app_commands.commands import Command, CommandParameter

    from .commands import Command as _Command
    from .tree import ContextMenuCallback, CommandCallback, P, T, Group

    func = Union[ContextMenuCallback, CommandCallback[Group, P, T]]

CB = TypeVar('CB')


# This is all next-level cursed


def _inject_callback(cls: Union[Type[_Command], CB]) -> CB:
    if inspect.isclass(cls) and issubclass(cls, _Command):

        async def callback(interaction: Interaction, **params) -> None:
            cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be an application command
            inst = cls()
            inst.interaction = interaction

            inst.__dict__.update(params)

        return callback  # type: ignore

    return cls  # type: ignore


def _inject_error_handler(cls: Type[_Command], command: Command) -> None:
    async def on_error(interaction: Interaction, error: Exception) -> None:
        cls.__discord_app_commands_id__ = int(interaction.data['id'])  # type: ignore # This will always be an application command
        inst = cls()
        inst.interaction = interaction
        return await inst.on_error(error)

    command.error(on_error)


def _inject_parameters(cls: Type[_Command], command: Command) -> None:
    params = cls.__discord_app_commands_parameters__
    cache = {}
    globalns = {}  # I'm legitimately confused by this

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


def _inject_class_based_information(cls: Union[Type[_Command], Any], command: Command) -> None:
    if not inspect.isclass(cls) or not issubclass(cls, _Command):
        return

    _inject_error_handler(cls, command)
    _inject_parameters(cls, command)
