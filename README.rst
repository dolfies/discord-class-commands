discord-class-commands
=======================

.. image:: https://discord.com/api/guilds/514232441498763279/embed.png
   :target: https://discord.gg/TvqYBrGXEm
   :alt: Discord server invite
.. image:: https://img.shields.io/pypi/v/discord-class-commands.svg
   :target: https://pypi.python.org/pypi/discord-class-commands
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/discord-class-commands.svg
   :target: https://pypi.python.org/pypi/discord-class-commands
   :alt: PyPI supported Python versions

An extension module for discord.py that facilitates class-based creation of Discord application commands.

Credits to discord.py for the docs and various snippets of code.

Key Features
-------------

- Modern Pythonic API using ``async`` and ``await``.
- Proper rate limit handling.
- Optimised in both speed and memory.
- Fully compatible with discord.py's application command implementation without monkey-patching.

Installing
----------

**Python 3.8 or higher is required**

To install the extension, you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U discord-class-commands

    # Windows
    py -3 -m pip install -U discord-class-commands

To install the development version, do the following:

.. code:: sh

    $ git clone https://github.com/iDevision/discord-class-commands
    $ cd discord.py
    $ python3 -m pip install -U .

Quick Example
--------------

.. code:: py

    import discord
    from discord.ext import class_commands

    client = discord.Client(intents=discord.Intents.default(), application_id=...)
    tree = discord.app_commands.CommandTree(client)

    @client.event
    async def setup_hook():
        await tree.sync()

    class Ping(class_commands.SlashCommand):
        async def callback(self):
            await self.send(f'Pong!')

    tree.add_command(Ping)
    client.run('token')

You can find more examples in the examples directory.

Links
------

- `Documentation <https://discord-class-commands.readthedocs.io/en/latest/index.html>`_
- `discord.py Documentation <https://discordpy.readthedocs.io/en/latest/index.html>`_
- `Official Discord Server <https://discord.gg/TvqYBrGXEm>`_
- `Discord API <https://discord.gg/discord-api>`_
