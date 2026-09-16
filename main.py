import os
import json
import discord
import aiohttp
import asyncio
import re
from datetime import datetime
import time

from discord.ext import commands


def loadowner():
    with open("ownerids.txt", 'r', encoding='utf-8') as f:
        ownerids = f.read().splitlines()
        return set(ownerids)
    
def loadsafeids():
    with open("safeids.txt", 'r', encoding='utf-8') as f:
        safeids = f.read().splitlines()
        return set(safeids)

def loadids():
    with open('huddyids.txt', 'r') as f:
        blacklisted_ids = set(f.read().splitlines())
        return blacklisted_ids

def loadyts():
    with open('huddyytids.txt', 'r') as f:
        blacklisted_ids = set(f.read().splitlines())
        return blacklisted_ids

def loadfandom():
    with open('huddyfandomids.txt', 'r') as f:
        blacklisted_ids = set(f.read().splitlines())
        return blacklisted_ids

bot = commands.Bot(intents=discord.Intents.all(), command_prefix=".", help_command=None)

config = "data/servers.json"
if not os.path.exists(config):
    with open(config, 'w') as f:
        json.dump({}, f)

recentmsgs = {}
webhooks = {}
def load():
    with open(config, 'r') as f:
        return json.load(f)

configs = load()

def save(data):
    with open(config, 'w') as f:
        json.dump(data, f, indent=4)

class Bot:
    def __init__(self):
        self.token = "replace with your token"
        self.commands = {
            "help": "Shows this",
            "banhuddy": "Mass bans huddy accounts + a few affiliates and unwanted people",
            "toggle": "Toggles banning new accounts and/or huddy accounts",
            "settings": "Shows the server's settings",
            "get-yts": "Gets Huddy's YouTube channels",
            "get-fandom": "Gets Huddy's Fandom accounts",
            "addid": "Adds a user ID to the huddyids.txt file (the file that contains all huddy ids). Only the owner of the bot can use this command",
            "removeid": "Removes a user ID from the huddyids.txt file (the file that contains all huddy ids). Only the owner of the bot can use this command",
            "addsafeid": "Adds a user ID to the safeids.txt file (the file that contains all huddy ids). Only the owner of the bot can use this command",
            "removesafeid": "Removes a user ID from the safeids.txt file (the file that contains all huddy ids). Only the owner of the bot can use this command",
            "deletehuddyinvites": "Deletes all invite links created by huddy",
            "gethuddyinvites": "Gets all invite links created by huddy in your server"
        }
        self.idsfile = "huddyids.txt"
        self.config = "data/servers.json"
        self.newer_than = 1525000000000000000
        self.raidbotkeywords = ["cxe", "krown", "generic", "insomnia"]
        self.topxregex = re.compile(r"^Top .* Worst MIBU Users\/Related", re.IGNORECASE)
        self.topxregex2 = re.compile(r"^Top .* MIBUTUBERS worst than Huddy", re.IGNORECASE)
        self.invite_regex = re.compile(r"https://discord\.gg/[a-zA-Z0-9]+", re.IGNORECASE)
        self.webhookurl = '' 
        self.webhookurl2 = ''
        self.webhookurl3 = ''
        self.date = self.accountdate(self.newer_than)

    def accountdate(self, id):
        de = 1420070400000
        time = ((int(id) >> 22) + de) / 1000
        date = datetime.utcfromtimestamp(time)
        return date.strftime('%B %d, %Y') 

    async def sendwebhookmessage(self, webhookurl: str, json):
        async with aiohttp.ClientSession() as session:
            async with session.post(webhookurl + "?wait=true", json=json) as r:
                return r.status, await r.text()


    async def checkinvite(self, invite: discord.Invite):
        safeids = loadsafeids()
        huddyids = loadids()
        reasonslist = Reasons()
        reasons = set()
        ownerids = loadowner()

        huddytargets = [
            "1401339199361253521", "892976749644742686", "1521904206947024986", "946412610658635836",
            "1018245266517807264", "974821596751593542", "1003322931218239599", "1122183841239539873",
            "841533749946613780", "1026091150005772308", "1069646561161789521", "980514119939674234",
            "1540790604659957771", "1305297716850724914"
        ]

        huddyinvitecodes = [
            "2fAkwdbyR", "HURf6DMRU", "QmGpd9R5E", "Mw6DG9Sx6", "SZEpeYnY5", "HHXhMZDS7F"
        ]

        inviter = invite.inviter
        code = invite.code
        based_on = invite.guild

        if inviter is not None:
            _, inviter_reasons = await self.checkuser(inviter)
            reasons.update(inviter_reasons)

        if based_on is not None and str(based_on.id) in huddytargets:
            reasons.add(reasonslist.invitetousualserver)

        if code in huddyinvitecodes:
            reasons.add(reasonslist.invitetousualserver)

        return bool(reasons), reasons


    async def checkuser(self, user: discord.User):
        safeids = loadsafeids()
        huddyids = loadids()
        ownerids = loadowner()
        reasonslist = Reasons()
        reasons = set()

        if user is None:
            return False, reasons

        username = user.name
        displayname = user.global_name or ""

        self.keywords = [
            'huddy', 'hanzala', 'hanza', 'hamzi', 'hamza', 'hanzi', 'mama666', 'dynasty', 'iceberg',
            'daisysdestruction', 'nanda', 'scully', 'mdpope', 'lolodin', 'trippiethedevil', 'necrobaphome',
            'iht', 'mega link', 'megalink', 'uttp', 'dvi', 'hurtcore', 'h2tc', 'tripsychixx', 'ydduh'
        ]

        if any(name in username.lower() for name in self.keywords):
            reasons.add(reasonslist.namematcheskeywords)

        if any(name in displayname.lower() for name in self.keywords):
            reasons.add(reasonslist.namematcheskeywords)

        if user.avatar is not None:
            if "79ee349b6511e2000af8a32fb8a6974e" in str(user.avatar.url):
                reasons.add(reasonslist.duckpfp)

        if ("xvhjs" in username.lower() or "xvhjs" in displayname.lower()) and str(user.id) not in ownerids:
            reasons.add(reasonslist.impersonate)

        if "xongito" in username.lower() or "xongito" in displayname.lower():
            reasons.add(reasonslist.impersonate)

        if ("montymoleloremaster" in username.lower() or "montymoleloremaster" in displayname.lower()) and str(user.id) not in safeids:
            reasons.add(reasonslist.impersonate)

        if ("red freak from hell" in displayname.lower() or "redfreakfromhell" in username.lower() or "muhtesemrobot" in username.lower()) and str(user.id) != "1044666378478682205":
            reasons.add(reasonslist.impersonate)

        if "cxe" in displayname.lower() or "cxe" in username.lower():
            reasons.add(reasonslist.impersonate)

        if user.id > self.newer_than:
            reasons.add(reasonslist.newaccount)

        if str(user.id) in huddyids:
            reasons.add(reasonslist.ishuddy)

        return bool(reasons), reasons
    
    async def checkmsg(self, message: discord.Message) -> tuple[bool, set]:
        sender = message.author

        text = message.content
        huddyids = loadids()
        safeids = loadsafeids()
        check_, reasons_ = await self.checkuser(sender)
        reasonslist = Reasons()
        reasons = set()
        if check_:
            reasons.update(reasons_)

        if not str(sender.id) in safeids:
            if self.topxregex.search(text):
                reasons.add(reasonslist.topxmibu)

            if self.topxregex2.search(text):
                reasons.add(reasonslist.topxmibu)

            if "xvhjs" in text.lower():
                reasons.add(reasonslist.talksaboutxvhjs)

            if any(nko in text.lower() for nko in ["slaughterhouse", "slaugtherhouse", "halo", "niko", "nasseli"]):
                reasons.add(reasonslist.talksaboutslaughterhouse)

            if any(mth in text.lower() for mth in ["mythicxx", "mythicxz", "mythiccz", "mythiczz", "authsauth", "barshlo"]):
                reasons.add(reasonslist.talksaboutauthsauth)

            if "forevor" in text.lower():
                reasons.add(reasonslist.forevermisspell)

            if "fwGmQdMkHr" in text: # old diddlements invite code that was deleted in early 2026
                reasons.add(reasonslist.invitetodiddlementsold)

            if "peaple" in text.lower():
                reasons.add(reasonslist.speltpeoplewrong)

            if "controversiel" in text.lower():
                reasons.add(reasonslist.controversialmisspell)
        
        return bool(reasons), reasons


    async def checkbotmsg(self, message: discord.Message) -> tuple[bool, set, discord.User]:
        huddyids = loadids()
        safeids = loadsafeids()
        reasonslist = Reasons()
        reasons = set()
        sender = message.author
        try:
            intmetadata = message.interaction_metadata.user
        except AttributeError:
            intmetadata = None

        check_, reasons_ = await self.checkuser(intmetadata)
        text = message.content
        #print(f" MESSAGE INTERACTION: {intmetadata}")
        if check_:
            reasons.update(reasons_)

        if any(bname in sender.name.lower() for bname in BOT_.raidbotkeywords):
            reasons.add(reasonslist.usesraidbot)

        if intmetadata is not None:
            if str(intmetadata.id) in huddyids:
                reasons.add(reasonslist.ishuddy) 

        if self.topxregex.search(text):
            reasons.add(reasonslist.topxmibu)

        if "xvhjs" in text.lower():
            reasons.add(reasonslist.talksaboutxvhjs)

        if any(nko in text.lower() for nko in ["slaughterhouse", "slaugtherhouse", "halo", "niko", "nasseli"]):
            reasons.add(reasonslist.talksaboutslaughterhouse)

        if any(mth in text.lower() for mth in ["mythicxx", "mythicxz", "mythiccz", "mythiczz", "authsauth"]):
            reasons.add(reasonslist.talksaboutauthsauth)

        if any(mth in text.lower() for mth in ["mythicxx", "mythicxz", "mythiccz", "mythiczz", "authsauth"]):
            reasons.add(reasonslist.talksaboutloeleveman)

        if "forevor" in text.lower():
            reasons.add(reasonslist.forevermisspell)

        if "fwGmQdMkHr" in text: # old diddlements invite code that was deleted in early 2026
            reasons.add(reasonslist.invitetodiddlementsold)

        if "peaple" in text.lower():
            reasons.add(reasonslist.speltpeoplewrong)

        if "controversiel" in text.lower():
            reasons.add(reasonslist.controversialmisspell)
            

        return bool(reasons), reasons, intmetadata

    async def checkwebhookmsg(self, message: discord.Message) -> tuple[bool, set]:
        huddyids = loadids()
        reasonslist = Reasons()
        reasons = set()
        sender = message.author
        intmetadata = message.interaction_metadata.user
        text = message.content

        if any(bname in sender.name.lower() for bname in BOT_.raidbotkeywords):
            reasons.add(reasonslist.usesraidbot)

        if str(intmetadata.id) in huddyids:
            reasons.add(reasonslist.ishuddy) 

        if self.topxregex.search(text):
            reasons.add(reasonslist.topxmibu)

        if "xvhjs" in text.lower():
            reasons.add(reasonslist.talksaboutxvhjs)

        if any(nko in text.lower() for nko in ["slaughterhouse", "slaugtherhouse", "halo", "niko", "nasseli"]):
            reasons.add(reasonslist.talksaboutslaughterhouse)

        if any(mth in text.lower() for mth in ["mythicxx", "mythicxz", "mythiccz", "mythiczz", "authsauth"]):
            reasons.add(reasonslist.talksaboutauthsauth)

        if any(mth in text.lower() for mth in ["mythicxx", "mythicxz", "mythiccz", "mythiczz", "authsauth"]):
            reasons.add(reasonslist.talksaboutloeleveman)

        if "forevor" in text.lower():
            reasons.add(reasonslist.forevermisspell)

        if "fwGmQdMkHr" in text: # old diddlements invite code that was deleted in early 2026
            reasons.add(reasonslist.invitetousualserver)

        if "peaple" in text.lower():
            reasons.add(reasonslist.speltpeoplewrong)

        if "controversiel" in text.lower():
            reasons.add(reasonslist.controversialmisspell)

        if "huddy detector" in sender.name.lower():
            reasons.add(reasons.impersonatehuddytetector)

        return bool(reasons), reasons, intmetadata

class Reasons:
    def __init__(self):
        self.topxmibu = 'User talks about "top X worst MIBU creators"'
        self.talksaboutslaughterhouse = "User talks about Slaughterhouse"
        self.talksaboutxvhjs = "User talks about xvhjs"
        self.talksaboutauthsauth = "User talks about AuthSauth/Mythiczz"
        self.talksaboutloeleveman = "User talks about Loeleveman"

        self.speltpeoplewrong = "User spelt people wrong"
        self.controversialmisspell = "User spelt controversial wrong"
        self.forevermisspell = "User spelt forever wrong"
        self.usesraidbot = "User uses known raid bot"

        self.namematcheskeywords = "Username matches keywords"
        self.duckpfp = "User has the duck pfp (one of the default profile pictures)"
        self.impersonate = "User is impersonating a known member of the mibu community (99% huddy)"
        self.newaccount = "User is a new account"
        self.impersonatehuddydetector = "User/tupper is impersonating huddy detector"
        self.ishuddy = "User is confirmed to be Huddy himself, an affiliate or someone you generally wouldn't want in your server"

        self.invitetousualserver = "User sent an invite link to a server that Huddy usually targets"
        self.sentbotinvite = "User sent a bot invite link"
    
    

BOT_ = Bot()

async def alert_user(webhookurl: str, checked: tuple[bool, str], user: discord.User):
    confirmaion, reasons = checked

    embed = {
        "title": "Huddy Detector",
        "description": f"Potential Huddy Account Detected \n```Username: {user.name}\nDisplay Name: {user.global_name}\nUser ID: {str(user.id)}``` \n\n(Copyable user ID for mobile:  `{str(user.id)}`)",
        "fields": [
            {"name": f"Reason {i}", "value": reason, "inline": False} for i, reason in enumerate(reasons, start=1)
        ]
    }

    payload = {
        "embeds": [embed]
    }
    await BOT_.sendwebhookmessage(webhookurl, json=payload)
    

@bot.command(name="help")
async def help(ctx):
    embed = discord.Embed(
        title = "Huddy Detector",
        description = "Commands",
        color = 0xBC4027
    )
    for cmd, desc in BOT_.commands.items():
        embed.add_field(name=f"{bot.command_prefix}{cmd}", value=desc, inline=False)

    await ctx.reply(embed=embed)

async def banlist(guild: discord.Guild) -> list:
    bans = guild.bans()
    ids = [str(ban.user.id) async for ban in bans]
    return ids

@bot.command(name="banhuddy")
async def banhuddy(ctx):
    guild: discord.Guild = ctx.guild
    
    currentbans = await banlist(guild)
    failed = set()
    success = 0
    huddyids = loadids()
    embed = discord.Embed(
        title="Huddy Detector", 
        description="Mass-banning a bunch of Huddy accounts alongside some generally unwanted people",
        colour=0xD1510E
        )

    await ctx.reply(embed=embed)
    for i, _id in enumerate(huddyids, start=1):
        print(f"Banning {i}/{len(huddyids)}")

        if _id in currentbans:
            print(f"Skipping {str(_id)} or account {i}/{len(huddyids)}, already banned\n")
            continue

        user = await bot.fetch_user(int(_id))

        try:
            await guild.ban(user, reason="huddy gfys", delete_message_seconds=0)
            print(f"Successfully banned {str(_id)} or account {i}/{len(huddyids)}\n")
            success += 1

        except Exception as e:
            print(str(e))
            print(f"Failed to ban {i}/{len(huddyids)}")
            failed.add((user.name, user.id))

    complete = discord.Embed(title="Huddy Detector", description=f"✅ Successfully banned {success} of Huddy's accounts, alongside some generally unwanted people", colour=0x00FF00)
    if bool(failed):
        complete.description += (f"\nFailed to ban these users:\n")
        for username, userid in failed:
            complete.description += (f"`{username} - {userid}`\n")
        complete.add_field(
            name="Tip", 
            value="If the bot doesn't have admin or at least the **Ban Members** and **Kick Members** permission then give the bot those permisions or a role with those permissions.\nIf the bot's role is lower than the people who are being banned then you should move the role or give it a role thats higher.\nAlternatively you can just ban the users yourself if you're a moderator and don't have **Manage Roles**",
            inline=False
            )

        if len(complete.description) > 4000:
            complete.description = f"✅ Successfully banned {success} of Huddy's accounts, alongside some generally unwanted people, but failed to ban a lot of the accounts (failed to ban {len(failed)} accounts)."

    await ctx.reply(embed=complete)

@bot.command(name="gethuddyinvites", description="Gets all invite links that were made by huddy")
async def getinvites(ctx):
    guild: discord.Guild = ctx.guild
    huddyids = loadids()
    huddyinvites = []
    invites = await guild.invites()
    for invite in invites:
        if str(invite.inviter.id) in huddyids:
            huddyinvites.append(invite.code)

    embed = discord.Embed(
        title="Huddy Detector", 
        colour=0xD1510E,
        description="Here are invite links created by huddy. I recommend deleting the invite links yourself or typing .deletehuddyinvites\n\n```"
        )
    if len(huddyinvites) == 0:
        return await ctx.reply("There are no invite links created by huddy")
    for _invite in huddyinvites:
        embed.description += f"{_invite} "
    embed.description += f"```"

    await ctx.reply(embed=embed)

@bot.command(name="deletehuddyinvites", description="Deletes all invite links that were made by huddy")
async def deleteinvites(ctx):
    guild: discord.Guild = ctx.guild
    huddyids = loadids()
    embed = discord.Embed(
        title="Huddy Detector", 
        colour=0xD1510E,
        description="Deleting all of Huddy's invite links"
    )
    await ctx.reply(embed=embed)
    invites = await guild.invites()
    for invite in invites:
        if str(invite.inviter.id) in huddyids:
            await invite.delete()

    embed = discord.Embed(
        title="Huddy Detector", 
        colour=0xD1510E,
        description="Successfully deleted all of Huddy's invite links"
        )
    await ctx.reply(embed=embed)
        
    

@bot.command(name="get-yts", description="Gets all of Huddy's YouTube channels")
async def getyts(ctx):
    msg = ""
    youtubeids = loadyts()
    for _id in youtubeids:
        msg += f"https://youtube.com/channel/{_id}\n"

    embed = discord.Embed(
        title="Huddy Detector", 
        colour=0xD1510E,
        description=f"These are all of Huddy's YouTube channels. I recommend blocking these channels and little to no communications with him.\n{msg}"
        )
    await ctx.send(embed=embed)    

@bot.command(name="get-fandom", description="Gets all of Huddy's Fandom accounts")
async def getyts(ctx):
    msg = ""
    fandomids = loadfandom()
    for _id in fandomids:
        msg += f"{_id}\n"

    embed = discord.Embed(
        title="Huddy Detector", 
        colour=0xD1510E,
        description=f"These are all of Huddy's Fandom accounts. I recommend blocking these accounts from your wiki/a wiki you moderate and little to no communications with him.\n{msg}"
        )
    await ctx.send(embed=embed)    

@bot.command(name='settings')
async def settings(ctx):
    guild = ctx.guild
    guild_id = str(guild.id)
    hb = configs.get(guild_id, {}).get("banhuddy", True)
    kn = configs.get(guild_id, {}).get("kicknew", False)
    embed = discord.Embed(
        title=f'Huddy Detector',
        description=f'**These are the settings for**\n`{ctx.guild.name} (ID: {str(ctx.guild.id)})`\n\nBan Huddy: {":white_check_mark:" if hb else ":x:"}\nKick new accounts: {":white_check_mark:" if kn else ":x:"}',
        color=0xD1510E
    )
    await ctx.reply(embed=embed)


@bot.command(name='addid', aliases=['add-id', 'add'])
async def addid(ctx, user_id: str):
    owner = loadowner()
    blacklisted_ids = loadids()

    if str(ctx.author.id) not in owner:
        return await ctx.reply("you dont have permission to use this command. only this bot's owner can use it")

    if user_id in blacklisted_ids:
        return await ctx.reply("already in huddyids.txt")

    try:
        with open("huddyids.txt", 'a', encoding='utf-8') as f:
            f.write(f"{user_id}\n")

        return await ctx.reply("added id to huddyids.txt")
    except Exception:
        return await ctx.reply("failed to add id.")


@bot.command(name='removeid', aliases=['remove-id', 'remove'])
async def removeid(ctx, user_id: str):
    owner = loadowner()
    blacklisted_ids = loadids()

    if str(ctx.author.id) not in owner:
        return await ctx.reply("you dont have permission to use this command. only this bot's owner can use it")

    if user_id not in blacklisted_ids:
        return await ctx.reply("id not in huddyids.txt")

    try:
        with open("huddyids.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open("huddyids.txt", 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip() != user_id:
                    f.write(line)

        return await ctx.reply("removed id from huddyids.txt")
    except Exception:
        return await ctx.reply("failed to remove id.")


@bot.command(name='addsafeid', aliases=['addsafe-id', 'addsafe'])
async def addsafeid(ctx, user_id: str):
    owner = loadowner()
    safe_ids = loadsafeids()

    if str(ctx.author.id) not in owner:
        return await ctx.reply("you dont have permission to use this command. only this bot's owner can use it")

    if user_id in safe_ids:
        return await ctx.reply("already in safeids.txt")

    try:
        with open("safeids.txt", 'a', encoding='utf-8') as f:
            f.write(f"{user_id}\n")

        return await ctx.reply("added id to safeids.txt")
    except Exception:
        return await ctx.reply("failed to add id.")


@bot.command(name='removesafeid', aliases=['removesafe-id', 'removesafe'])
async def removesafeid(ctx, user_id: str):
    owner = loadowner()
    safe_ids = loadsafeids()

    if str(ctx.author.id) not in owner:
        return await ctx.reply("you dont have permission to use this command. only this bot's owner can use it")

    if user_id not in safe_ids:
        return await ctx.reply("id not in safeids.txt")

    try:
        with open("safeids.txt", 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open("safeids.txt", 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip() != user_id:
                    f.write(line)

        return await ctx.reply("removed id from safeids.txt")
    except Exception:
        return await ctx.reply("failed to remove id.")
    
@bot.command(name='toggle', help='turns huddy detector on/off')
async def toggle(ctx):
    if not ctx.author.guild_permissions.manage_guild:
        embd = discord.Embed(
            title="Huddy Detector",
            description="❌ You don't have permission to do this: You need the **Manage Server** permission in order to use this command",
            colour=0xba0d0d
        )
        return await ctx.send(embed=embd)
    guild = ctx.guild
    guild_id = str(guild.id)
    hb = configs.get(guild_id, {}).get("banhuddy", False)
    kn = configs.get(guild_id, {}).get("kicknew", False)
    class ToggleButton(discord.ui.View):
        def __init__(self, authorid: int):
            self.authorid = authorid
            super().__init__(timeout=60)

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user.id != self.authorid:
                await interaction.response.send_message("You didnt run the command", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="Ban Huddy", style=discord.ButtonStyle.secondary, emoji="⚒")
        async def gbutton(self, interaction: discord.Interaction, button):
            guild = interaction.guild
            guild_id = str(guild.id)
            huddyban = configs.get(guild_id, {}).get("banhuddy", False)

            configs.setdefault(guild_id, {})
            configs[guild_id]["banhuddy"] = not huddyban
            save(configs)
            status = 'disabled' if huddyban else 'enabled'
            embed = discord.Embed(title='Huddy Detector', description=f"Ban huddy has been {status}", color=0xD1510E if status == 'disabled' else 0xD1510E)

            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                pass

        @discord.ui.button(label="Kick New Accounts", style=discord.ButtonStyle.secondary, emoji="👢")
        async def nbutton(self, interaction: discord.Interaction, button):
            guild = interaction.guild
            guild_id = str(guild.id)
            
            kicknew = configs.get(guild_id, {}).get("kicknew", False)
            configs.setdefault(guild_id, {})
            configs[guild_id]["kicknew"] = not kicknew

            save(configs)
            status = 'disabled' if kicknew else 'enabled'
            embed = discord.Embed(title='Huddy Detector', description=f"You have {status} kicking new accounts", color=0xD1510E if status == 'disabled' else 0xD1510E)

            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                pass

    embed = discord.Embed(
        title="Huddy Detector",
        description=f"You are changing the settings for Huddy Detector in \n`{ctx.guild.name} (ID: {str(ctx.guild.id)})`.\n\nHEADS UP: Kick New Accounts kicks any account that was created after {BOT_.date}\n\nThe date can and will be moved up over time",
        colour=0xD1510E
    )
    embed.add_field(name="Current Settings", value=f"Ban Huddy: {':white_check_mark:' if hb else ':x:'}\nKick New Accounts: {':white_check_mark:' if kn else ':x:'}\n", inline=False)
    await ctx.reply(embed=embed, view=ToggleButton(ctx.author.id))

@bot.event
async def on_guild_join(guild: discord.Guild):
    huddyids = loadids()
    payload = {
        "content": "",
        "embeds": [
            {
                "title": "Huddy Detector",
                "description": f"Bot joined server `{guild.name}` `ID: {str(guild.id)}`",
                "color": 45056
            }
        ]
    }
    await BOT_.sendwebhookmessage(BOT_.webhookurl3, payload)
    if guild.name == "gassy BLUD": # the bot leaves the server if its added to a server thats been nuked with the gassybluds bot
        return await guild.leave(guild)

    if str(guild.owner.id) in huddyids: # the bot leaves the server if huddy owns it
        return await guild.leave(guild)

    if str(guild.id) not in configs:
        configs[str(guild.id)] = {"banhuddy": True, "kicknew": False}
        save(configs)


@bot.event
async def on_member_join(member: discord.Member):
    safe_ids = loadsafeids()
    guild = member.guild
    guild_id = guild.id
    banhuddy_ = configs.get(guild_id, {}).get("banhuddy", True)
    kicknew = configs.get(guild_id, {}).get("kicknew", False)

    payload = {
        "content": "",
        "embeds": [
            {
                "title": "Huddy Detector",
                "description": f"User `{member.name + '#' + member.discriminator if int(member.discriminator) else member.name}` joined `{guild.name}` `ID: {str(guild.id)}`\n\n\nClick here to copy the id if you're on mobile `{str(member.id)}`",
                "color": 45056  
            }
        ]
    }
    await BOT_.sendwebhookmessage(BOT_.webhookurl3, payload)

    huddyids = loadids()
    checked = await BOT_.checkuser(member)
    confirmation, reasons = checked
    if confirmation:
        await alert_user(webhookurl=BOT_.webhookurl2, checked=(confirmation, reasons), user=member)

        if (len(reasons) >= 6 or Reasons().impersonate in reasons) and not str(member.id) in safe_ids:
            if banhuddy_:
                await guild.ban(member, reason="80% sure that its huddy\n")

        if Reasons().duckpfp in reasons and not str(member.id) in safe_ids:
            if banhuddy_:
                await guild.ban(member, reason="huddy....")

        if Reasons().newaccount in reasons and not str(member.id) in safe_ids:
            if kicknew:
                await guild.kick(member, reason="new account")

    else:
        print("member's name doesnt match blacklisted usernames")

@bot.event
async def on_message(message: discord.Message):
    guild = message.guild
    guild_id = str(guild.id)
    banhuddy_ = configs.get(guild_id, {}).get("banhuddy", True)
    kicknew = configs.get(guild_id, {}).get("kicknew", False)
    safe_ids = loadsafeids()

    timestamp = time.time()
    if message.author == bot.user:
        return
    if str(message.channel.id) in ["1464280414167371992", "1464277687538290836", "1464276488726642719", "1464276511686136050", "1464276622503841954"]:
        await bot.process_commands(message)
        return
# checks if tuppers are being used or wtv
    if message.webhook_id is None:
        recentmsgs[message.id] = {
            "content": message.content,
            "timestamp": timestamp,
            "channel_id": message.channel.id,
            "author_id": message.author.id,
            "message_id": message.id
        }

    msgs = [data for data in recentmsgs.values() if (data["channel_id"] == message.channel.id and message.content in data['content'].strip() and timestamp - data["timestamp"] <= 15)]
    if msgs:
        og = max(msgs, key=lambda x: x["timestamp"])

        webhooks[message.id] = {
            "webhook_id": message.id,
            "tupper_name": message.author.name,
            "content": message.content,
            "channel_id": message.channel.id,
            "original_message_id": og["message_id"],
            "original_author_id": og["author_id"],
            "time": timestamp,
        }

    if message.author.bot and not message.webhook_id:
        confirmation, reasons, truesender = await BOT_.checkbotmsg(message)
        print(confirmation, reasons, truesender)
        if confirmation:
            for i, reason in enumerate(reasons, start=1):
                print(f"Reason {i}: {reason}")

        if banhuddy_:
            for reason in reasons:
                if reason == Reasons().ishuddy:
                    await guild.ban(truesender, reason="huddy we know its you")

                if reason == Reasons().duckpfp and not str(truesender.id) in safe_ids:
                    await guild.ban(truesender, reason="huddy we know its you")

                if reason == Reasons().usesraidbot and not str(truesender.id) in safe_ids:
                    await guild.ban(truesender, reason="huddy we know its you")

                if (Reasons().talksaboutslaughterhouse in reasons or Reasons().talksaboutxvhjs in reasons) and Reasons().speltpeoplewrong in reasons and not str(truesender.id) in safe_ids:
                    print("100% huddy")
                    await guild.ban(truesender, reason="huddy we know its you")
        if kicknew:
            for reason in reasons:
                if reason == Reasons().newaccount:
                    await guild.kick(truesender, reason="new account")

    checked = await BOT_.checkmsg(message)
    confirmation, reasons = checked

    if "huddy detector" in message.author.name and not str(message.author.id) in ["1396127387212710029", "1461358640995897344", "1548811959804231763", "1548811639099236374"]: # if "huddy detector" is in the webhook message's name and the user id isn't any of the ids listed here (huddy detector 1.0 and 2.0's ids) then it will identify the message as an impersonation attempt
        if message.webhook_id:
            await message.reply("ohhhh looks like an impersonation attempt.\nIf tupperbox is in the server (which if you're reading this it probably is) then type \"tul!find huddy\" and ban the tupper's owner from the server or react to the message that i replied to with the \":question:\" emoji to identify who actually wrote this if you figure out who actually wrote the message create a forum on the server and give me their username or user id (NOT DISPLAY NAME OR SCREENSHOT) https://discord.gg/x2k22VPDwF\nalso the bot will NEVER tell you to add another bot directly so if they give you a link to a bot it is 100% huddy")
            await BOT_.sendwebhookmessage(BOT_.webhookurl2, {"content": f"@everyone impersonation attempt in {guild.name} (ID: {guild.id})"})



    #print(f"User {'is' if confirmation else 'isnt'} potentially HUddy")

    #check for any inites
    if "discord.gg/" in message.content or "discord.com/invite" in message.content:
        invites = set()
        msg = message.content.split()
        for mg in msg:
            if "discord.gg/" in mg.strip():
                invite_code = mg.split("discord.gg/")[-1]
                #print(mg)
                invites.add(invite_code)
            if "discord.com/invite/" in mg.strip():
                invite_code = mg.split("discord.com/invite/")[-1]
                invites.add(invite_code)
                

        for invite in invites:
            try:
                invite_info = await bot.fetch_invite(url=f"https://discord.gg/{invite}")
                check_inv, inv_reasons = await BOT_.checkinvite(invite_info)
                old_reasons = reasons.copy()
                reasons.update(inv_reasons)

                for reason in reasons - old_reasons:
                    print(f"New reason from invite: {reason}")
                    
                reasons.update(inv_reasons)

                print(reasons)
                print("invitereasonssss====\n")
                print(inv_reasons)

            except discord.NotFound:
                print("invalid invite")
    
    if confirmation:
        if len(reasons) == 1 and Reasons().newaccount in reasons:
            pass
        else:        
            await alert_user(webhookurl=BOT_.webhookurl2, checked=checked, user=message.author) 

        for i, reason in enumerate(reasons, start=1):
            print(f"Reason {i}: {reason}")
            
    if str(message.author.id) not in safe_ids:
        if banhuddy_:
            for reason in reasons:
                if reason == Reasons().ishuddy:
                    await guild.ban(message.author, reason="huddy we know its you")

                if (Reasons().talksaboutslaughterhouse in reasons or Reasons().talksaboutxvhjs in reasons) and Reasons().speltpeoplewrong in reasons:
                    await guild.ban(message.author, reason="huddy we know its you")


    await bot.process_commands(message)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    payload = {
        "content": "",
        "embeds": [
            {
                "title": "Huddy Detector",
                "description": f"Bot was removed from server `{guild.name} ID: {str(guild.id)}`",
                "color": 852992
            }
        ]
    }
    await BOT_.sendwebhookmessage(BOT_.webhookurl3, payload)

@bot.event
async def on_message_delete(message: discord.Message):
    guild = message.guild
    if message.webhook_id is not None:
        return

    matches = [data for data in webhooks.values() if data["original_message_id"] == message.id]
    checked = await BOT_.checkmsg(message=message)
    conf, reasons = checked
    for match in matches:
        print(f"\nTupper: {match['tupper_name']}\nOriginal message author ID: {match['original_author_id']}")
        if "huddy detector" in match["tupper_name"]: 
            reasons.add(Reasons().impersonatehuddydetector)
            try:
                await guild.ban(await bot.fetch_user(match["original_author_id"]), reason="huddy gfys")
            except:
                pass

            await alert_user(webhookurl=BOT_.webhookurl2, checked=(conf, reasons), user=message.author) 

        del webhooks[match["webhook_id"]]

  

@bot.event
async def on_ready():
    guilds = bot.guilds
    for guild in guilds:
        if str(guild.id) not in configs:
            configs[str(guild.id)] = {"banhuddy": True, "kicknew": False}
            save(configs)

bot.run(BOT_.token)
