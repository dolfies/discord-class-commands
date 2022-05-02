.. currentmodule:: discord.ext.class_commands

API Reference
===============

The following section outlines the API of discord-class-commands.

.. note::

    This module requires the :py:mod:`discord` or a compatible fork to be installed.  Check out :ref:`installing` for more info.

Version Related Info
---------------------

You can query version info using the below attribute. For guarantees, check :ref:`version_guarantees`.

.. data:: __version__

    A string representation of the version. e.g. ``'1.0.0rc1'``. This is based
    off of :pep:`440`.

Classes
--------

These classes are meant to be subclassed to be used as application commands.

.. danger::

    The classes listed below are **not intended to be instantiated**.

    You should not and cannot make your own :class:`SlashCommand` instance.
    Instead, you should subclass :class:`SlashCommand` and use it as a base class.

Command
~~~~~~~~

.. attributetable:: Command

.. autoclass:: Command
    :members:

.. note::

    This class is not the same as discord.py's `Command` class.

SlashCommand
~~~~~~~~~~~~~

.. attributetable:: SlashCommand

.. autoclass:: SlashCommand
    :members:
    :inherited-members:

UserCommand
~~~~~~~~~~~~

.. attributetable:: UserCommand

.. autoclass:: UserCommand
    :members:
    :inherited-members:

MessageCommand
~~~~~~~~~~~~~~~

.. attributetable:: MessageCommand

.. autoclass:: MessageCommand
    :members:
    :inherited-members:

Data Classes
-------------

These classes are designed to be used as data containers.

Unlike :ref:`models <discord_api_models>` you are allowed to create
these yourself.

All classes here have :ref:`py:slots` defined which means that it is
impossible to have dynamic attributes to the data classes.

Option
~~~~~~~~

.. attributetable:: Option

.. autoclass:: Option
    :members:
