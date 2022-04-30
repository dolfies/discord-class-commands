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
from typing import TYPE_CHECKING, Any, List

from discord.utils import MISSING

if TYPE_CHECKING:
    from discord.app_commands.commands import Choice, ChoiceT

_empty = inspect.Parameter.empty

# fmt: off
__all__ = (
    'Option',
)
# fmt: on


class ParameterData(inspect.Parameter):  # This is a fake inspect.Parameter designed to be compatible with existing code
    def __init__(self, name: str, default: Any = MISSING, annotation: Any = MISSING):
        super().__init__(
            name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=default if default is not MISSING else _empty,
            annotation=annotation if annotation is not MISSING else _empty,
        )


class _Option:
    """Represents a command parameter.

    Attributes
    ----------
    default: :class:`Any`
        The default value for the option if the option is optional.
    name: :class:`str`
        The overriden name of the option.
    description: :class:`str`
        The description of the option.

        .. note::
            If not explicitly overrided here, the description is parsed
            from the class docstring. Else, it defaults to "…".
    autocomplete: :class:`bool`
        Whether or not the parameter should be autocompleted.
    choices: List[:class:`~discord.app_commands.Choice`]
        The choices for the parameter.

        .. note::
            This is not the only way to provide choices to a command.
            There are two more ergonomic ways of doing this, using a
            :obj:`typing.Literal` annotation or a :class:`enum.Enum`.
    """

    __slots__ = ('autocomplete', 'default', 'description', 'name', 'choices')

    def __init__(
        self,
        default: Any = MISSING,
        name: str = MISSING,
        description: str = MISSING,
        *,
        autocomplete: bool = False,
        choices: List[Choice[ChoiceT]] = MISSING,
    ) -> None:
        self.description = description
        self.default = default
        self.autocomplete = autocomplete
        self.name = name
        self.choices = choices


if TYPE_CHECKING:

    def Option(
        default: Any = MISSING,
        name: str = MISSING,
        description: str = MISSING,
        *,
        autocomplete: bool = MISSING,
        choices: List[Choice[ChoiceT]] = MISSING,
    ) -> Any:
        ...

else:
    Option = _Option
