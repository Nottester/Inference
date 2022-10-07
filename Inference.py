import discord
import time
import random
import itertools
import os
import asyncio
import functools
import datetime
import math
import ctypes
import ctypes.util
import re
import youtube_dl
from os import system
from discord.ext import commands, tasks
from discord.ext.commands import BucketType
from random import choice
from discord.utils import get
from discord.voice_client import VoiceClient
from async_timeout import timeout

client = commands.Bot(command_prefix = '.')
client.remove_command("help")

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}


ffmpeg_options = {
    'options': '-vn'
}

queue = []
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@client.event
async def on_ready():
    await asyncio.sleep(1)
    print(f"Client is ready. {client.user.name}")
    await asyncio.sleep(3)
    print("Please wait 10 seconds.")

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='join-leave')
    await channel.send(f'Welcome to {message.guild}, {member.guild}')

@client.event
async def on_message(message):
    client.handler.propagate(message)
    await client.process_commands(message)

@client.event
async def on_member_leave(self, member):
   if str(channel) == "join-leave":
            fembed = discord.Embed(color=0x4a3d9a)
            fembed.add_field(name="Welcome", value=f"{member.name} has joined {member.guild.name}", inline=False)
            fembed.set_image(url="https://cdn.discordapp.com/attachments/769706060121636876/770376723422249021/Acesters_small_transparent.png")
            await channel.send(embed=fembed)

@client.event
async def on_message(message):
    filter = ["Nigger", "NIgga", "NIGGER", "NIGGA", "NIGG3R", "N1GG3A", "N1GG3", "N1GG3R", "n3gg1r", "n1gg3", "n1gg3r", "n3gga", "nigg", "nIGGA", "nIgga", "NIgga", "NIGga", "NIGGa", "nIGga", "niGGA", "nIGGA","nigger", "nigga", "Nlgger", "USA", "US", "usa", "united states of america", "Usa", "United States of America"]
    for word in filter:
        muted_role = discord.utils.get(message.guild.roles, name='Muted')
        if message.content.count(word) > 0:
            await message.author.add_roles(muted_role)
            await message.channel.purge(limit=1)
            await message.channel.send(f'{message.author.mention} ``has said a banned word.``')
    if message.content == 'Is tomas gay':
        await message.channel.send('Yes, he %1000 is')
    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Invalid command used.')
#Commands

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms :ping_pong:')

@client.command()
async def Hello(ctx):
    await ctx.send('Hi!')

@commands.has_permissions(kick_members = True)
@client.command()
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=1)
    await ctx.channel.purge(limit=amount)
    await asyncio.sleep(1)
    await ctx.send(f'``{amount} Messages has been deleted.``')
    await asyncio.sleep(3)
    await ctx.channel.purge(limit=1)
    await asyncio.sleep(3)


@client.command(aliases=['m'])
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_arole = discord.utils.get(ctx.guild.roles, name='Muted')

    await member.add_roles(muted_arole)
    if not member:
        await ctx.send("Please specify a member.")
        return

    await ctx.send(member.mention + f"has been muted for ```\nReason: {reason}``` ```\nBy: {ctx.message.author}```")
    if member.dm_channel == None:
        await member.create_dm()
    await member.dm_channel.send(
        content=f"You have been muted from {ctx.guild} by {ctx.message.author}```\nReason: {reason}```")

@client.command()
@commands.cooldown(per = 4, rate = 1, type = BucketType.user)
async def cooldown(ctx):
    await ctx.send("cooling down...")

@client.command(pass_context=True, aliases=['j', 'joi', 'Join'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Joined {channel}")


@client.command(pass_context=True, aliases=['l', 'lea', 'Leave'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(ctx.bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")

@client.command(name='play', help='This command plays songs')
async def play(ctx):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))
    del(queue[0])

@client.command(aliases=['Help', 'hel'])
async def help(message):

    MyEmbed = discord.Embed(title="Help command", description="This command shows the list of commands you can use!", color=0xff0000)
    MyEmbed.set_author(name="Help", icon_url="https://cdn.discordapp.com/attachments/761666137179684886/769371393108213760/Chillopia_improved.png")
    MyEmbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/761666137179684886/769371393108213760/Chillopia_improved.png")
    MyEmbed.set_image(url="https://cdn.discordapp.com/attachments/761666137179684886/769371393108213760/Chillopia_improved.png")
    MyEmbed.add_field(name="kick", value="This command kicks a member out of the server! Moderation required.", inline=False)
    MyEmbed.add_field(name="ping", value="This command displays the Ping of the server!", inline=False)
    MyEmbed.add_field(name="ban", value="This command bans someone out of the server! Moderation required", inline=False)
    MyEmbed.add_field(name="mute", value="This command mutes someone which removes their speech permission! Moderation required.", inline=False)
    MyEmbed.add_field(name="unban", value="This command unbans someone so they can enjoy their time in the server. Moderation required.", inline=False)
    MyEmbed.add_field(name="clear", value="This command clears messages that someone sent [needs an amount]. Moderation required.", inline=False)
    MyEmbed.add_field(name="BanServer", value="WAIT DON'T DO THIS COMMAND.", inline=False)
    MyEmbed.add_field(name="Platform", value="Basically, the coding language that the bot is conded on", inline=False)
    MyEmbed.add_field(name="unmute", value="Unmutes someone, so they can talk on the server again.", inline=False)
    MyEmbed.add_field(name="Hello", value="Says 'Hello' back", inline=False)
    MyEmbed.add_field(name="Rules", value="The rules of the server, moderation required")
    MyEmbed.set_footer(text="Sun Tzu")


    await message.channel.send(embed=MyEmbed)

@commands.has_permissions(kick_members=True)
@client.command()
async def Rules(message):
    EmbedO = discord.Embed(title="The Rules", description="The rules of the Acesters Server", color=0xff0000)
    EmbedO.set_author(name="Rules", icon_url="https://cdn.discordapp.com/attachments/769706060121636876/770674375502069790/Hammer.png")
    EmbedO.add_field(name="Harassment", value='Do not insult anyone in this server')
    EmbedO.add_field(name="Racism", value="Do not use racist slurs against anyone in the server or even make a joke about it")
    EmbedO.add_field(name="Be mature", value="Don't act immature in this server or you will be facing a permanent ban")
    EmbedO.add_field(name="No politics or religion involved", value="Religion or politics aren't invovled in this server, please don't talk about them here.")
    EmbedO.add_field(name="Do not start arguments", value="Please don't start arguments in this server, this is a friendly server and arguments are only kept in Direct Messages")
    EmbedO.add_field(name="Drama", value="are not allowed in this server, you cant start drama or you will get a permanent ban.")
    EmbedO.add_field(name="No Spoilers", value="do not spoil any movie, books or anything else")
    EmbedO.add_field(name="Common sense", value="PLEASE use common sense if you do not then you will be facing a warn.")
    EmbedO.add_field(name="No Loopholes", value="Do not start loopholes or your permanently banned")
    EmbedO.add_field(name="No LGBTQ+", value="Please do not start any conversation about the LBGTQ+ community or even mention it. Keep this server friendly and basic. We do not need fake sexualities")
    EmbedO.add_field(name="No MAP Community", value="We do not accept any form of pedophilles, zoophiles, etc. We need to keep this community safe and friendly.")
    EmbedO.add_field(name="Discord TOS", value="Please follow the discord TOS if you do not then your getting permanently banned.", inline=False)

    await message.channel.send(embed=EmbedO)

@client.command()
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    muted_arole = discord.utils.get(ctx.guild.roles, name='Muted')

    await member.remove_roles(muted_arole)

    await ctx.send(member.mention + "has been muted")
    if member.dm_channel == None:
        await member.create_dm()
    await member.dm_channel.send(
        content=f"You have been unmuted from {ctx.guild} by {ctx.message.author}```\nReason: {reason}```")


    await ctx.send(member.mention + f"has been unmuted for ```\nReason: {reason}``` ```\nBy: {ctx.message.author}```")

    if not member:
        await ctx.send("Please specify a member.")
        return


@commands.has_permissions(kick_members = True)
@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    if not member:
        await ctx.send("Please specify a member.")
        return
    if member.dm_channel == None:
        await member.create_dm()
    await member.dm_channel.send(
        content=f"You have been kicked from {ctx.guild} by {ctx.message.author}```\nReason: {reason}```")
    await member.kick(reason=reason)
    await ctx.send(f"**{member.mention}** has been kicked for ```\nReason: {reason}``` ```\nBy: {ctx.message.author}```")




@commands.has_permissions(kick_members = True)
@client.command()
async def ban(ctx, member : discord.Member, *, reason=None):
    if member.dm_channel == None:
        await member.create_dm()
    await member.dm_channel.send(
        content=f"You have been banned from {ctx.guild} by {ctx.message.author}```\nReason: {reason}```")
    await member.ban(reason=reason)
    await ctx.send(f"**{member.mention}**has been banned for ```\nReason: {reason}``` ```\nBy: {ctx.message.author}```")

@commands.has_permissions(kick_members = True)
@client.command()
async def unban(ctx, *, member):
	banned_users = await ctx.guild.bans()

	member_name, member_discriminator = member.split('#')
	for ban_entry in banned_users:
		user = ban_entry.user

		if (user.name, user.discriminator) == (member_name, member_discriminator):
 			await ctx.guild.unban(user)
 			await ctx.channel.send(f"**{member.mention}**has been unbanned for ```\nReason: {reason}``` ```\nBy: {ctx.message.author}```")


@client.command()
async def Platform(ctx):
    await ctx.send('This Client was coded using Python')

@client.command()
async def BanServer(ctx):
    await ctx.send('Bruh, you really thought you could ban the whole server.')

@clear.error
async def clear_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Please specify an amount of messages to delete.')



client.run(os.environ['Acesters'])