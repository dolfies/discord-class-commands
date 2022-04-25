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

from typing import (
    Any,
    TYPE_CHECKING,
    Callable,
    Coroutine,
    List,
    Optional,
    Type,
    Union,
)

from discord.app_commands.commands import Command, ContextMenu, Group as _Group, _shorten
from discord.app_commands.errors import AppCommandError
from discord.app_commands import CommandTree as _CommandTree
from discord.utils import MISSING

from .commands import Command as _Command
from .interop import _generate_callback, _inject_class_based_information

if TYPE_CHECKING:
    from discord.interactions import Interaction
    from discord.abc import Snowflake
    from discord.app_commands.commands import ContextMenuCallback, CommandCallback, GroupT, P, T

    ErrorFunc = Callable[
        [Interaction, AppCommandError],
        Coroutine[Any, Any, Any],
    ]

__all__ = ('CommandTree', 'Group', 'command')


class CommandTree(_CommandTree):
    """Represents a container that holds application command information.

    This is a replacement for :class:`discord.app_commands.CommandTree`
    that is completely compatible with the original class.

    Parameters
    -----------
    client: :class:`~discord.Client`
        The client instance to get application command information from.
    """

    def command(
        self,
        *,
        name: str = MISSING,
        description: str = MISSING,
        guild: Optional[Snowflake] = MISSING,
        guilds: List[Snowflake] = MISSING,
    ) -> Callable[[CommandCallback[_Group, P, T]], Command[_Group, P, T]]:
        """Creates an application command directly under this tree.

        Parameters
        ------------
        name: :class:`str`
            The name of the application command. If not given, it defaults to a lower-case
            version of the callback name.
        description: :class:`str`
            The description of the application command. This shows up in the UI to describe
            the application command. If not given, it defaults to the first line of the docstring
            of the callback shortened to 100 characters.
        guild: Optional[:class:`~discord.abc.Snowflake`]
            The guild to add the command to. If not given or ``None`` then it
            becomes a global command instead.
        guilds: List[:class:`~discord.abc.Snowflake`]
            The list of guilds to add the command to. This cannot be mixed
            with the ``guild`` parameter. If no guilds are given at all
            then it becomes a global command instead.
        """

        def decorator(param: Union[CommandCallback[_Group, P, T], Type[_Command]]) -> Command[_Group, P, T]:
            if not inspect.iscoroutinefunction(param) and not (inspect.isclass(param) and issubclass(param, _Command)):
                raise TypeError('command parameter must be a coroutine function or Command subclass')

            if description is MISSING:
                if param.__doc__ is None:
                    desc = '…'
                else:
                    desc = _shorten(param.__doc__)
            else:
                desc = description

            command = Command(
                name=name if name is not MISSING else param.__name__,
                description=desc,
                callback=_generate_callback(param, fake=True),
                parent=None,
            )

            _inject_class_based_information(param, command)
            self.add_command(command, guild=guild, guilds=guilds)
            return command

        return decorator

    def context_menu(
        self,
        *,
        name: str = MISSING,
        guild: Optional[Snowflake] = MISSING,
        guilds: List[Snowflake] = MISSING,
    ) -> Callable[[ContextMenuCallback], ContextMenu]:
        """Creates a application command context menu directly under this tree.

        If a function, it must have a signature of :class:`~discord.Interaction` as its first parameter
        and taking either a :class:`~discord.Member`, :class:`~discord.User`, or :class:`~discord.Message`,
        or a :obj:`typing.Union` of ``Member`` and ``User`` as its second parameter.

        Examples
        ---------

        .. code-block:: python3

            @app_commands.context_menu()
            async def react(interaction: discord.Interaction, message: discord.Message):
                await interaction.response.send_message('Very cool message!', ephemeral=True)

            @app_commands.context_menu()
            async def ban(interaction: discord.Interaction, user: discord.Member):
                await interaction.response.send_message(f'Should I actually ban {user}...', ephemeral=True)

        Parameters
        ------------
        name: :class:`str`
            The name of the context menu command. If not given, it defaults to a title-case
            version of the callback name. Note that unlike regular slash commands this can
            have spaces and upper case characters in the name.
        guild: Optional[:class:`~discord.abc.Snowflake`]
            The guild to add the command to. If not given or ``None`` then it
            becomes a global command instead.
        guilds: List[:class:`~discord.abc.Snowflake`]
            The list of guilds to add the command to. This cannot be mixed
            with the ``guild`` parameter. If no guilds are given at all
            then it becomes a global command instead.
        """

        def decorator(param: Union[ContextMenuCallback, Type[_Command]]) -> ContextMenu:
            if not inspect.iscoroutinefunction(param) and not (inspect.isclass(param) and issubclass(param, _Command)):
                raise TypeError('context menu parameter must be a coroutine function or Command subclass')

            actual_name = param.__name__.title() if name is MISSING else name
            context_menu = ContextMenu(name=actual_name, callback=_generate_callback(param))

            _inject_class_based_information(param, context_menu)
            self.add_command(context_menu, guild=guild, guilds=guilds)
            return context_menu

        return decorator


class Group(_Group):
    """A class that implements an application command group.

    These are usually inherited rather than created manually.

    This is a replacement for :class:`discord.app_commands.Group`
    that is completely compatible with the original class.

    Attributes
    ------------
    name: :class:`str`
        The name of the group. If not given, it defaults to a lower-case
        kebab-case version of the class name.
    description: :class:`str`
        The description of the group. This shows up in the UI to describe
        the group. If not given, it defaults to the docstring of the
        class shortened to 100 characters.
    parent: Optional[:class:`Group`]
        The parent group. ``None`` if there isn't one.
    """

    def command(
        self,
        *,
        name: str = MISSING,
        description: str = MISSING,
    ) -> Callable[[CommandCallback[GroupT, P, T]], Command[GroupT, P, T]]:
        """Creates an application command under this group.

        Parameters
        ------------
        name: :class:`str`
            The name of the application command. If not given, it defaults to a lower-case
            version of the callback name.
        description: :class:`str`
            The description of the application command. This shows up in the UI to describe
            the application command. If not given, it defaults to the first line of the docstring
            of the callback shortened to 100 characters.
        """

        def decorator(param: Union[CommandCallback[GroupT, P, T], Type[_Command]]) -> Command[GroupT, P, T]:
            if not inspect.iscoroutinefunction(param) and not (inspect.isclass(param) and issubclass(param, _Command)):
                raise TypeError('command parameter must be a coroutine function or Command subclass')

            if description is MISSING:
                if param.__doc__ is None:
                    desc = '…'
                else:
                    desc = _shorten(param.__doc__)
            else:
                desc = description

            command = Command(
                name=name if name is not MISSING else param.__name__,
                description=desc,
                callback=_generate_callback(param, fake=True),
                parent=self,
            )

            _inject_class_based_information(param, command)
            self.add_command(command)
            return command

        return decorator


def command(
    *,
    name: str = MISSING,
    description: str = MISSING,
) -> Callable[[CommandCallback[GroupT, P, T]], Command[GroupT, P, T]]:
    """Creates an application command.

    This is a replacement for :func:`discord.app_commands.command`
    that is completely compatible with the original class.

    Parameters
    ------------
    name: :class:`str`
        The name of the application command. If not given, it defaults to a lower-case
        version of the callback name.
    description: :class:`str`
        The description of the application command. This shows up in the UI to describe
        the application command. If not given, it defaults to the first line of the docstring
        of the callback shortened to 100 characters.
    """

    def decorator(param: CommandCallback[GroupT, P, T]) -> Command[GroupT, P, T]:
        if not inspect.iscoroutinefunction(param) and not (inspect.isclass(param) and issubclass(param, _Command)):
            raise TypeError('command parameter must be a coroutine function or Command subclass')

        if description is MISSING:
            if param.__doc__ is None:
                desc = '…'
            else:
                desc = _shorten(param.__doc__)
        else:
            desc = description

        command = Command(
            name=name if name is not MISSING else param.__name__,
            description=desc,
            callback=_generate_callback(param, fake=True),
            parent=None,
        )

        _inject_class_based_information(param, command)
        return command

    return decorator


def context_menu(*, name: str = MISSING) -> Callable[[ContextMenuCallback], ContextMenu]:
    """Creates an application command context menu.

    If a function, it must have a signature of :class:`~discord.Interaction` as its first parameter
    and taking either a :class:`~discord.Member`, :class:`~discord.User`, or :class:`~discord.Message`,
    or a :obj:`typing.Union` of ``Member`` and ``User`` as its second parameter.

    This is a replacement for :func:`discord.app_commands.context_menu`
    that is completely compatible with the original class.

    Examples
    ---------

    .. code-block:: python3

        @app_commands.context_menu()
        async def react(interaction: discord.Interaction, message: discord.Message):
            await interaction.response.send_message('Very cool message!', ephemeral=True)

        @app_commands.context_menu()
        async def ban(interaction: discord.Interaction, user: discord.Member):
            await interaction.response.send_message(f'Should I actually ban {user}...', ephemeral=True)

    Parameters
    ------------
    name: :class:`str`
        The name of the context menu command. If not given, it defaults to a title-case
        version of the callback name. Note that unlike regular slash commands this can
        have spaces and upper case characters in the name.
    """

    def decorator(param: ContextMenuCallback) -> ContextMenu:
        if not inspect.iscoroutinefunction(param) and not (inspect.isclass(param) and issubclass(param, _Command)):
            raise TypeError('context menu parameter must be a coroutine function or Command subclass')

        actual_name = param.__name__.title() if name is MISSING else name
        context_menu = ContextMenu(name=actual_name, callback=_generate_callback(param))

        _inject_class_based_information(param, context_menu)
        return context_menu

    return decorator
