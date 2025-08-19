import discord
import json
import os
from discord.ext import commands

intents = discord.Intents.all()
prefix = "." 

blud = commands.Bot(command_prefix=prefix, intents=intents)

huddyevidence = "79ee349b6511e2000af8a32fb8a6974e" 

blacklisted_names = ['huddy', 'hanzala', 'hanza', 'hamzi', 
                     'hamza', 'hanzi', 'mama666', 'tungdynasty', "daisysdestruction", 'nanda', 'northkorea', 'NotSoFantastic'] 

config = "data/servers.json"
if not os.path.exists(config):
    with open(config, 'w') as f:
        json.dump({}, f)

def load():
    with open(config, 'r') as f:
        return json.load(f)
def save(data):
    with open(config, 'w') as f:
        json.dump(data, f, indent=4)

configs = load()

@blud.event
async def on_guild_join(guild):
    if str(guild.id) not in configs:
        configs[str(guild.id)] = {"banhuddy": True}
        save(configs)

with open('huddyids.txt', 'r') as f:
    blacklisted_ids = f.read().splitlines()
    print(blacklisted_ids)


@blud.event
async def on_ready():
    print(f'logged in as {blud.user}')


@blud.event
async def on_member_join(member):
    print(member)
    server = str(member.guild.id)
    if configs.get(server, {}).get("banhuddy", True):
        pfp = str(member.display_avatar.url)
        if huddyevidence in pfp:
            try:
                await member.send('ur prob a huddy alt so ur banned ')
            except:
                print('failed to send message')
            try:
                await member.ban(reason="potential huddy alt account")
            except:
                print('failed to ban huddy :(')
        elif any(obvhuddy in member.name.lower() for obvhuddy in blacklisted_names) or any(obvhuddy in member.display_name.lower() for obvhuddy in blacklisted_names):
            try:
                await member.send('ur prob a huddy alt so ur banned ')
            except:
                print('failed to send message')
            try:
                await member.ban(reason="potential huddy alt account")
            except:
                print('failed to ban huddy :(')

        elif str(member.id) in blacklisted_ids:
            try:
                await member.send('ur def a huddy alt so ur banned ')
            except:
                print('failed to send message')
            try:
                await member.ban(reason="potential huddy alt account")
            except:
                print('failed to ban huddy :(')

        else:
            print('this person is safe. not a huddy alt')
    else:
        print('detector disabled, not tracking any joins')

@blud.command(name='toggle', help='turns huddy detector on/off')
async def banhuddy(ctx):
    guild = ctx.guild
    guild_id = str(ctx.guild.id)
    huddyban = configs.get(guild_id, {}).get("banhuddy", False)
    configs[guild_id] = {"banhuddy": not huddyban}
    save(configs)
    status = 'Disabled' if huddyban else 'Enabled'
    embed = discord.Embed(title='Huddy Detector', description=f"Huddy detector has been {status}")

    print(f'huddy detector is {status}')
    await ctx.reply(embed=embed)

@blud.command(name='banhuddy', help="Bans most of Huddy's past accounts")
async def masshuddyban(ctx):
    embed = discord.Embed(title='Huddy Detector', description="Massbanning Huddy's accounts")
    await ctx.reply(embed=embed)
    for id in blacklisted_ids:
        try:
            huddy = await ctx.bot.fetch_user(id)
            await ctx.guild.ban(huddy, reason='huddy gfys')
            print(f'banned {huddy}')
        except:
            print('failed to ban account')
    embed2 = discord.Embed(title='Huddy Detector', description="✅ Successfully banned Huddy's accounts")
    await ctx.reply(embed=embed2)


blud.run('enter your bot token')

