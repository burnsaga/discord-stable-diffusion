import asyncio
import os
from abc import ABC

import discord
from discord.ext import commands
from src.core.logging import get_logger
import aiohttp
import io

class Shanghai(commands.Bot, ABC):
    def __init__(self, args):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=args.prefix, intents=intents)
        self.args = args
        self.logger = get_logger(__name__)
        self.load_extension('src.bot.stablecog')

    async def on_ready(self):
        self.logger.info(f'Logged in as {self.user.name} ({self.user.id})')
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.playing, name='/dream'))

    async def on_message(self, message):
        if message.author == self.user:
            try:
                # Check if the message from Shanghai was actually a generation
                if message.embeds[0].fields[0].name == 'Compute used':
                    await message.add_reaction('❌')
                    #await message.add_reaction('🔁')
                    #await message.add_reaction('👁')
                    #await message.add_reaction('👆')
                    await message.add_reaction('💾')
            except:
                pass


    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name == '❌':
            message = await self.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if message.embeds:
                # look at the message footer to see if the generation was by the user who reacted
                if message.embeds[0].footer.text == f'{payload.member.name}#{payload.member.discriminator}':
                    await message.delete()
        elif payload.emoji.name == '💾':
            message = await self.get_channel(payload.channel_id).fetch_message(payload.message_id)
            if message.embeds:
                embed = message.embeds[0]
                if embed.type == 'image':
                    print('save')
                    async with aiohttp.ClientSession() as session:
                        async with session.get(embed.url) as resp:
                            if resp.status != 200:
                                return await message.channel.send('Could not download file...')
                            data = io.BytesIO(await resp.read())
                            filename = f'{embed.title}.{embed.url.split(".")[-1]}'
                            with open(filename, 'wb') as f:
                                f.write(data.getbuffer())
                            await message.channel.send(f'Downloaded image to {os.getcwd()}')
