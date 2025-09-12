#anti huddy and judah bot
import discord
import json
import os
from discord.ext import commands
import re

intents = discord.Intents.all()
prefix = "." 

blud = commands.Bot(command_prefix=prefix, intents=intents)

huddyevidence = "79ee349b6511e2000af8a32fb8a6974e" 

pattern = r'^[a-z]+_[a-z]+_\d{2,8}$'

blacklisted_phrase = 'worst mibu'
blacklisted_names = ['huddy', 'hanzala', 'hanza', 'hamzi', 
                     'hamza', 'hanzi', 'mama666', 'tungdynasty', "daisysdestruction", 'nanda', 'northkorea', 'NotSoFantastic', 'necro', 'uncannyrapist', 'uncannyrpiper', '亡靈開膛手', 'lolodin'] 

blacklisted_names2 = ['neku', 'henry', 'henery', 'franzer', 'xv', 'kale', 'beau', 'viviun', 'bajel', 'day', 'adam', 'nana', 'kimi'] #for judah naming himself names like "BEAU'S DICK"  

obvjudah = ['dick', 'tits', 'pussy', 'judah', 'ass', 'boobs', 'cum', 'fuck', 'nigger'] #+ 

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

obvhuddy2 = ['twomad', 'stilian', 'ld', 'gsd', 'music', 'judah', 'king', 'huddy', 'antares', 'gof', 'awesomecat', 'slaughterhouse', 'uttp', '27dde', 'dante', 'hexagon', 'joe mama', 'dawn', 'yasmin pierre', 'dsf']
@blud.event
async def on_guild_join(guild):
    if str(guild.id) not in configs:
        configs[str(guild.id)] = {"banhuddy": True}
        save(configs)

with open('huddyids.txt', 'r') as f:
    blacklisted_ids = f.read().splitlines()
    print(blacklisted_ids)



@blud.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.author.id > 1400000000000000000:
        if 'top' in message.content.lower() and 'worst' in message.content.lower() and 'mibu' in message.content.lower() and 'related' in message.content.lower() and any(hd in message.content.lower() for hd in obvhuddy2):
            try:
                await message.guild.ban(
                    message.author,
                    reason="huddy we know it's you"
                )
                print(f"Banned {message.author} for potentially being huddy.")
            except Exception as e:
                print(f"Failed to ban {message.author}: {e}")

    elif message.author.id > 1410000000000000000:
        if 'worst' in message.content.lower() and 'mibu' in message.content.lower():
            try:
                await message.guild.ban(
                    message.author,
                    reason="huddy we know it's you"
                )
                print(f"Banned {message.author} for potentially being huddy.")
            except Exception as e:
                print(f"Failed to ban {message.author}: {e}")

    
    await blud.process_commands(message)

nopfp = ['9855d7e3b9780976', '2ccd8ae8b2379360', '18e336a74a159cfd', '411d8a698dd15ddf', '788f05731f8aa02e', '320d5a40d309f942', 'c82b3fa769ed6e6ffdea579381ed5f5c', '157e517cdbf371a47aaead44675714a3', '5445ffd7ffb201a98393cbdf684ea4b1', 'f7f2e9361e8a54ce6e72580ac7b967af', '6c5996770c985bcd6e5b68131ff2ba04']

@blud.event
async def on_ready():
    print(f'logged in as {blud.user}')

safe_ids = ['1408332135873384450', '1409664633513443461', '1091167315678212216', '972883349163098214', '1160646380214296716', '763882154173923368', '309437317813239809', '705536958990123079', '861291608968265759', '780287531840700418', '1313368024673423401', '1310784364375834714', '1157181396884914176', '1389358473313255517', '732676316704276501']

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

        elif 'uncanny' in member.name.lower() and 'ripper' in member.name.lower() and '666' in member.name.lower(): 
            try:
                await member.send("get the fuck out necro uncanny ripper 666 guy or whatever your name is. go back to gof's server")
            except:
                print('failed to send message')
            try:
                await member.ban(reason="potential necrouncannyrapistripper666 alt account")
            except:
                print('failed to ban necrophillia guy :(')

        elif (any(obvjud in member.display_name.lower() for obvjud in blacklisted_names2) and 
              any(obvjudah in member.display_name.lower() for obvjudah in obvjudah)) and not str(member.id) in safe_ids:
            try:
                await member.send("kill yourself judah")
            except:
                print('failed to send message')
            try:
                await member.ban(reason="potential judah alt account")
            except:
                print('failed to ban judah :(')
        
        elif str(member.id) in blacklisted_ids:
            try:
                await member.send('ur def a huddy alt so ur banned ')
            except:
                print('failed to send message')
            try:
                await member.ban(reason="potential huddy alt account")
            except:
                print('failed to ban huddy :(')

        elif re.fullmatch(pattern, member.name):
            try:
                await member.kick(reason="new account. could be a huddy alt")
            except:
                print('failed to ban huddy :(')

        elif member.id > 1410000000000000000:
            ahash = str(member.avatar) if member.avatar else None
            if ahash:
                if ahash in nopfp:
                    try:
                        await member.kick(reason="new account AND no pfp. could be a huddy alt or a sus user")
                    except:
                        print('failed to ban huddy :(')
            elif not ahash:
                try:
                    await member.kick(reason="new account AND no pfp. could be a huddy alt or a sus user")
                except:
                    print('failed to ban huddy :(')

        else:
            print('this person is safe. not a huddy alt')
    else:
        print('detector disabled, not tracking any joins')

@blud.command(name='toggle', help='turns huddy detector on/off')
async def banhuddy(ctx):
    if not ctx.author.guild_permissions.manage_guild:
        await ctx.send("❌ You don't have permission to do this: `MANAGE_SERVER` is required")
        return

    guild = ctx.guild
    guild_id = str(ctx.guild.id)
    huddyban = configs.get(guild_id, {}).get("banhuddy", False)
    configs[guild_id] = {"banhuddy": not huddyban}
    save(configs)
    status = 'Disabled' if huddyban else 'Enabled'
    embed = discord.Embed(title='Huddy Detector', description=f"Huddy detector has been {status}")

    print(f'huddy detector is {status}')
    await ctx.reply(embed=embed)

@blud.command()
async def banjudah(ctx):
    guild = ctx.guild
    judahids = ['1328567772116029542', '1293000690117120020', '867433511316357151', '1412620373861863434', '815986860521685033', '1394485081673826425', '958441194524913725', '1148077609457033288']
    embed = discord.Embed(title='Huddy Detector', description="Massbanning Judah's accounts")
    await ctx.reply(embed=embed)
    for id in blacklisted_ids:
        try:
            huddy = await ctx.bot.fetch_user(id)
            await ctx.guild.ban(huddy, reason='judah kill yourself')
            print(f'banned {huddy}')
        except:
            print('failed to ban account')
    embed2 = discord.Embed(title='Huddy Detector', description="✅ Successfully banned Judah's accounts")
    await ctx.reply(embed=embed2)

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

blud.run('bot token')

