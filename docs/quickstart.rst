:orphan:

.. _quickstart:

.. currentmodule:: discord-class-commands

Quickstart
============

This page gives a brief introduction to the library. It assumes you have the library installed,
if you don't check the :ref:`installing` portion.

An Example Command
-------------------

Let's make a bot with a simple ping command in a test guild and walk you through it.

It looks something like this:

.. code-block:: python3

    import discord
    from discord.ext import class_commands

    test_guild = discord.Object(id=...)  # Replace with your test guild ID

    client = discord.Client(intents=discord.Intents.default(), application_id=...)  # Replace with your bot's application ID
    tree = discord.app_commands.CommandTree(client)

    @client.event
    async def setup_hook():
        await tree.sync(guild=test_guild)

    @client.event
    async def on_ready():
        print(f'We have logged in as {client.user}')

    class Ping(class_commands.SlashCommand, description="Check latency of the bot"):
        async def callback(self):
            await self.send(f'Pong! {round(self.interaction.client.ws.latency * 1000)}ms')

    tree.add_command(Ping, guild=test_guild)
    client.run('your token here')

Let's name this file ``example_command.py``. Make sure not to name it ``discord.py`` as that'll conflict
with the library.

There's a lot going on here. If you don't know how to use discord.py, you should read :doc:`their documentation <discord:index>`

1. First we just import the ext, if this raises a `ModuleNotFoundError` or `ImportError`
   then head on over to :ref:`installing` section to properly install.

2. Next we create a new command by subclassing the :class:`~discord.ext.commands.SlashCommand` class, and set a description.
   The name defaults to a lower-case version of the class name.

3. We then define a callback within the command class, which is where we'll respond to our command.
   This is where we'll do all of our logic.

   In this case, we just respond with a message.

4. Finally, we add the command to the command tree, and specify our test guild.
   This works the same way it does with regular function-based application commands.

Now that we've made our example command, we have to *run* it. Luckily, this is simple since this is just a
Python script, we can run it directly.

On Windows:

.. code-block:: shell

    $ py -3 example_command.py

On other systems:

.. code-block:: shell

    $ python3 example_command.py

Now you can try playing around with application commands.
