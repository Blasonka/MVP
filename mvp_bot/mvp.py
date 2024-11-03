##############################################################################################################################################################################
# region importsAndVars
# imports
import os
import discord
import platform
from discord.utils import get
from discord.ext import commands
from dotenv import load_dotenv, dotenv_values
import asyncio
import datetime
import random as r
from string import ascii_letters, digits
import math as m
import mvpconstants as cts
from discord import FFmpegPCMAudio as auplayer
import pokemonevent as pmn

# variables
intents = discord.Intents().all()
help_command = commands.DefaultHelpCommand(no_category = 'Parancsok')
client = commands.Bot(command_prefix = '#', intents = intents, help_command = help_command)

selfContext = 'Management Virtual Protocol#2097'

global inTestingMode
inTestingMode = False

global allowedIDs
allowedIDs = [778331044641636443, 780473061211504640, pmn.eventRoomId]

for roomID in pmn.fightRoomIds:
    allowedIDs.append(roomID)

for roomID in pmn.channelIDs:
    allowedIDs.append(roomID)

if platform.system() == 'Linux':
    discord.opus.load_opus('/opt/lib/libopus.so.0')

# endregion
##############################################################################################################################################################################
# region events
# startup
@client.event
async def on_ready():
    print('Bot on-the-go.')

    await pmn.startPME(client)

    reminderTask = asyncio.create_task(reminderCoroutine())
    await reminderTask

# message
@client.event
async def on_message(msg):
    if msg.author == client.user:
        return

    if msg.content.startswith('#') and msg.guild is None:
        await msg.channel.send('Csak szerveren fogadok el parancsokat. Bocsesz.')
        return

    if msg.content.startswith('#') and msg.channel.id not in allowedIDs:
        await msg.delete()
        return

    if msg.content.startswith('#') and inTestingMode == True and await checkIfHasRole(msg.author, 'Apuci') == False:
        await msg.channel.send('Épp tesztelési üzemmódban vagyok. Légyszíves ne piszkálj.')
        return

    if msg.content.startswith('#hello'):
        await msg.channel.send(f'Szeva {msg.author.name}!')
        await msg.add_reaction('🖐️')
    elif msg.content.startswith('#pok') and pmn.inProgress == False:
        await msg.channel.send('Ez az event jelenleg nem elérhető.')
        return

    if 'bazdmeg' in msg.content:
        await deleteMsg(msg, 'Nem beszész csunyán!!4!')

    await client.process_commands(msg)

@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user:
        return
    if before.channel == after.channel:
        return

    clientVoice = member.guild.voice_client
    if clientVoice is None or clientVoice.channel is None:
        if after.channel is not None:
            await after.channel.connect()

            await asyncio.sleep(1)

            if randomReact == 0:
                await playVoiceUpdate(member, 'effects/csoka/napot')
            else:
                await playVoiceUpdate(member, 'effects/lan/bonjour')
        return

    randomReact = r.randint(0, 9)

    if before.channel == clientVoice.channel:
        if len(before.channel.members) == 1 and after.channel is None:
            await asyncio.sleep(30)
            await clientVoice.disconnect()
        elif len(before.channel.members) == 1:
            await clientVoice.disconnect()
            await after.channel.connect()
        elif after.channel is None:
            if member.id == 235088799074484224:
                await playVoiceUpdate(member, 'other/ritmusleave')
            elif member.id == 234395307759108106:
                await playVoiceUpdate(member, 'other/groovyleave')
            else:
                await playVoiceUpdate(member, 'other/szeva')
        elif after.channel.id == 778962813057630240:
            await playVoiceUpdate(member, 'other/cigi')
    elif before.channel is not clientVoice.channel and after.channel is clientVoice.channel:
        await asyncio.sleep(2)

        if member.id == 235088799074484224:
            await playVoiceUpdate(member, 'other/ritmus')
        elif member.id == 234395307759108106:
            await playVoiceUpdate(member, 'other/groovy')
        elif member.id == 418826095047999491 or member.id == 494890371499819009:
            await playVoiceUpdate(member, 'other/poiip')
        else:
            if randomReact == 0:
                await playVoiceUpdate(member, 'other/garbage')
            else:
                await playVoiceUpdate(member, 'other/obi')

# endregion
##############################################################################################################################################################################
# region rolesAndMessages
# roles
async def assignRole(ctx, roleName):
    member = ctx.author
    role = get(member.guild.roles, name=roleName)
    await discord.Member.add_roles(member, role)

async def checkIfHasRole(ctx, roleName):
    if type(ctx) != discord.Member:
        member = ctx.message.author
    else:
        member = ctx
    for role in member.roles:
        if role.name == roleName:
            return True
    return False

# message handling
async def reactToMsg(ctx, reaction):
    try:
        ctx.message
    except AttributeError:
        return

    await ctx.message.add_reaction(reaction)

async def deleteMsg(msg, *reason):
    await msg.delete()

    if len(list(reason)) == 1:
        await msg.channel.send(reason[0])

# endregion
##############################################################################################################################################################################
# region pokemonEvent
# pokemon event managing
@client.command(pass_context=True, brief='Pokémon event parancs.', description='A paranccsal kapcsolatos tudnivalókért írd be a "#pok help" parancsot.')
async def pok(ctx, *args):
    # autism check
    if pmn.inEvent(ctx.message.author.id) == False and args[0] != 'join' and len(args) == 1:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    # command check

    if len(args) < 1:
        await ctx.send('A parancs használatával kapcsolatban való segítséghez használd a #help pok parancsot.')
        return
    elif len(args) == 1:
        if ctx.message.channel.id != pmn.eventRoomId and args[0] != 'join':
            await ctx.message.delete()
            warningMessage = await ctx.send('A pokémon parancsokat a pokémon-event csatornán használd!')
            await asyncio.sleep(5)
            await warningMessage.delete()
            return

        if args[0] == 'list':
            await pmn.checkPokemons(ctx.message)
        elif args[0] == 'save':
            await pmn.saveState()
        elif args[0] == 'join':
            await pmn.joinEvent(ctx.message)
        elif args[0] == 'exit':
            await pmn.exitEvent(ctx.message)
        elif args[0] == 'buy' or args[0] == 'shop':
            await ctx.send(pmn.listShopContents())
        elif args[0] == 'help':
            await pmn.printHelp(ctx, 'help')
        elif args[0] == 'daily' or args[0] == 'login':
            await pmn.userLogin(ctx)
        elif args[0] == 'inv':
            await ctx.message.author.send(pmn.listInventory(ctx))
            await ctx.message.delete()
        elif args[0] == 'lead' or args[0] == 'leader' or args[0] == 'leaderboard':
            await pmn.listLeaderBoard(ctx)
        elif args[0] == 'trans' or args[0] == 'transfer':
            await pmn.listHighDemandPokemons(ctx)
        else:
            await ctx.send('Ismeretlen argumentum a parancsban.')
    elif len(args) == 2:
        if args[0] == 'use':
            if args[1] == 'inc' or args[1] == 'incense':
                await pmn.useIncense(ctx)
            elif args[1] == 'track' or args[1] == 'tracker':
                await pmn.useTracker(ctx)
            else:
                await ctx.send('Ismeretlen argumentum a parancsban.')
        elif args[0] == 'shop' or args[0] == 'buy':
            if args[1] == 'ball' or args[1] == 'pokeball':
                await pmn.buyItem(ctx, 0, 1)
            elif args[1] == 'inc' or args[1] == 'incense':
                await pmn.buyItem(ctx, 1, 1)
            elif args[1] == 'track' or args[1] == 'tracker':
                await pmn.buyItem(ctx, 2, 1)
            elif args[1] == 'pot' or args[1] == 'potion':
                if pmn.getUserFightIndex(ctx) is None:
                    await pmn.buyItem(ctx, 3, 1)
                else:
                    await ctx.send('Harc közben nem tudsz Potion-t venni!')
            elif args[1] == 'elix' or args[1] == 'elixir':
                if pmn.getUserFightIndex(ctx) is None:
                    await pmn.buyItem(ctx, 4, 1)
                else:
                    await ctx.send('Harc közben nem tudsz Elixir-t venni!')
            else:
                await ctx.send('A bolt nem árul ilyen terméket.')
        elif args[0] == 'help':
            await pmn.printHelp(ctx, args[1])
        elif args[0] == 'fight':
            if args[1] == 'cancel':
                await pmn.cancelFight(ctx)
            else:
                await pmn.fightAction(ctx, args[1])
        else:
            await ctx.send('Ismeretlen argumentum a parancsban.')
    elif len(args) == 3:
        if args[0] == 'catch':
            await ctx.send(await pmn.claimPokemon(ctx, str(args[1]), int(args[2])))
        elif args[0] == 'shop' or args[0] == 'buy':
            amountToBuy = int(args[2])
            if args[1] == 'ball' or args[1] == 'pokeball':
                await pmn.buyItem(ctx, 0, amountToBuy)
            elif args[1] == 'inc' or args[1] == 'incense':
                await pmn.buyItem(ctx, 1, amountToBuy)
            elif args[1] == 'track' or args[1] == 'tracker':
                await pmn.buyItem(ctx, 2, amountToBuy)
            elif args[1] == 'pot' or args[1] == 'potion':
                if pmn.getUserFightIndex(ctx) is None:
                    await pmn.buyItem(ctx, 3, amountToBuy)
                else:
                    await ctx.send('Harc közben nem tudsz Potion-t venni!')
            elif args[1] == 'elix' or args[1] == 'elixir':
                if pmn.getUserFightIndex(ctx) is None:
                    await pmn.buyItem(ctx, 4, amountToBuy)
                else:
                    await ctx.send('Harc közben nem tudsz Elixir-t venni!')
            else:
                await ctx.send('A bolt nem árul ilyen terméket.')
        elif args[0] == 'trans' or args[0] == 'transfer':
            await pmn.transferPokemon(ctx, args[1], args[2])
        else:
            await ctx.send('Ismeretlen argumentum a parancsban.')
    elif len(args) == 4:
        if args[0] == 'fight':
            await pmn.pokemonFight(ctx, int(args[1]), args[2], int(args[3]))
        elif args[0] == 'use':
            if args[1] == 'pot' or args[1] == 'potion':
                await pmn.usePot(ctx, args[2], args[3])
            elif args[1] == 'elix' or args[1] == 'elixir':
                await pmn.useElix(ctx, args[2], args[3])
            else:
                await ctx.send('Ismeretlen argumentum a parancsban.')
        else:
            await ctx.send('Ismeretlen argumentum a parancsban.')
    else:
        await ctx.send('Ismeretlen argumentum a parancsban.')

# endregion
##############################################################################################################################################################################
# region voiceChannelHandling
# join and leave
@client.command(pass_context=True, aliases=['here', 'come'], brief='Belépés voice-ra', description='Beléptet engem arra a voice channel-re, ahol te vagy.')
async def join(ctx):
    if ctx.message.author.voice is not None:
        voice = ctx.message.author.voice.channel

        try:
            await voice.connect()
        except discord.errors.ClientException:
            await ctx.send('Már bent vagyok egy hangcsatornában.')
            return

        await reactToMsg(ctx, '🖐️')

        randomReact = r.randint(0, 9)

        if randomReact == 0:
            await ae(ctx, 'csoka', 'napot')
        else:
            if await checkIfHasRole(ctx, 'Russia Forever') == True:
                await ae(ctx, 'lan', 'oyy')
            elif await checkIfHasRole(ctx, 'Gipsy') == True:
                await ae(ctx, 'tavesz')
            elif ctx.message.author.id == 345162576013033473:
                await ae(ctx, 'big')
            else:
                await ae(ctx, 'lan', 'bonjour')
    else:
        await ctx.send('A #join parancs használatához bent kell lenned egy szobában.')

@client.command(pass_context=True, brief='Kövess!', description='Beléptet engem arra a voice channel-re, ahol te vagy, ha esetleg máshol lennék.')
async def switch(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        await voice.disconnect()
    else:
        await ctx.send('A #switch parancs használatához mindkettőnknek bent kell lennie egy szobában.')
        return

    if ctx.message.author.voice.channel is not None:
        voice = ctx.message.author.voice.channel
        await voice.connect()
    else:
        await ctx.send('A #switch parancs használatához mindkettőnknek bent kell lennie egy szobában.')

@client.command(pass_context=True, aliases=['away', 'hess'], brief='Kilépés voice-ról', description='Kiléptet engem a voice channel-ből.')
async def leave(ctx):
    global auQueue

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        auQueue = []

        await reactToMsg(ctx, '🖐️')

        randomReact = r.randint(0, 9)

        if randomReact == 0:
            await ae(ctx, 'csoka', 'viszlat')
            await asyncio.sleep(0.6)
        else:
            if await checkIfHasRole(ctx, 'Russia Forever') == True:
                await ae(ctx, 'lan', 'das')
                await asyncio.sleep(1)
            elif await checkIfHasRole(ctx, 'Gipsy') == True:
                await ae(ctx, 'tavesz')
                await asyncio.sleep(1.25)
            else:
                await ae(ctx, 'lan', 'adios')
                await asyncio.sleep(0.6)

        await voice.disconnect()
    else:
        await ctx.send('A #leave parancs használatához bent kell lennem egy szobában.')

# switch users of voice channel to other channel
@client.command(pass_context=True, aliases=['mig'], brief='Migrálás másik szobába', description='A velem egy szobában lévő felhasználókat átviszi egy másik szobába, velem együtt.')
async def migrate(ctx, id):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice is None:
        await ctx.send('Bent kell lennem egy hangcsatornában a parancs használatához.')
        return

    if ctx.message.author.voice.channel is None:
        await ctx.send('Bent kell lenned egy hangcsatornában a parancs használatához.')
        return

    if voice.channel != ctx.message.author.voice.channel:
        await ctx.send('Egy hangcsatornában kell lennünk a parancs használatához.')
        return

    try:
        int(id)
    except ValueError:
        await ctx.send('Add meg a csatorna ID-jét.')
        return

    destination = ctx.guild.get_channel(int(id))
    if destination is None:
        await ctx.send('Nincs ilyen csatorna.')
        return
    elif destination == voice.channel:
        await ctx.send('Nem migrálhatsz ugyanarra a csatornára.')
        return

    for member in ctx.message.author.voice.channel.members:
        if member != client.user:
            await member.move_to(destination)

    await voice.disconnect()
    await destination.connect()

# endregion
##############################################################################################################################################################################
# region audioHandling
# au system
global auQueue
auQueue = []

    # list effects
@client.command(pass_context=True, aliases=['eff'], brief='Hangeffektek listája', description='Kilistázza a jelenleg elérhető hangeffekteket.')
async def effects(ctx, *subcategory):
    effectFiles = []
    categories = []

    if len(subcategory) > 1:
        await ctx.send('Nincs ilyen alkategória.')
        return
    elif len(subcategory) == 1:
        subcategory = list(subcategory)[0]
    else:
        subcategory = ''

    for f in os.listdir(cts.effectPath):
        if '.mp3' in f:
            f = f.replace('.mp3', '')
            effectFiles.append(f)
        else:
            categories.append(f)

    if subcategory in categories:
        effectFiles = []
        for f in os.listdir(cts.effectPath + subcategory + '/'):
            if '.mp3' in f:
                f = f.replace('.mp3', '')
                effectFiles.append(f)

    effectFiles = sorted(effectFiles)
    categories = sorted(categories)

    effectString = ''
    for e in effectFiles:
        effectString += e + '\t'

    categoryString = ''
    for c in categories:
        categoryString += c + '\t'

    if len(subcategory) == 0:
        await ctx.send(f'**Hangeffektek listája ({len(effectFiles)}):**\n{effectString}\n\n**Alkategóriák:**\n{categoryString}')
    elif subcategory in categories:
        await ctx.send(f'**Hangeffektek listája a(z) {subcategory.upper()} kategóriában ({len(effectFiles)}):**\n{effectString}')
    else:
        await ctx.send(f'Nincs ilyen alkategória.')

    # play effect
@client.command(pass_context=True, aliases=['au', 'audio'], brief='Hangeffekt lejátszása', description='Lejátszok egy hangeffektet, ha benne vagyok egy voice channel-ben. Az elérhető hangeffektek mutatásához használd az #effects/eff parancsot.')
async def ae(ctx, *trueEffectPath):
    if ctx.message.author.voice == None:
        await ctx.send('Először be kell lépned egy hangcsatornába.')
        return

    if trueEffectPath[0] == 'clear':
        await clearQ(ctx)
        return

    if len(trueEffectPath) == 2:
        trueEffect = cts.effectPath + trueEffectPath[0] + '/' + trueEffectPath[1] + '.mp3'
    elif len(trueEffectPath) == 1:
        trueEffect = cts.effectPath + trueEffectPath[0] + '.mp3'
    else:
        await ctx.send('Nincs ilyen effekt.')
        return

    if os.path.exists(trueEffect):
        await play(ctx, trueEffect)
    else:
        await ctx.send('Nincs ilyen effekt.')

    # play audio
global silenced
silenced = False

async def play(ctx, auFilePath):
    global auQueue

    if silenced == True:
        await ctx.send('Shhhh.')
        return

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice is not None:
        auQueue.append(auFilePath)
        await reactToMsg(ctx, '🎧')
        while len(auQueue) != 0:
            try:
                voice.play(auplayer(auQueue[0]))
                auQueue.remove(auQueue[0])
            except discord.errors.ClientException:
                await asyncio.sleep(.1)
    else:
        await ctx.send('Először bent kell lennem egy csatornában. (#join)')

async def playVoiceUpdate(member, auFilePath):
    if silenced == True:
        return

    voice = get(client.voice_clients, guild=member.guild)

    if voice is not None:
        voice.play(auplayer(cts.audioPath + auFilePath + '.mp3'))

async def clearQ(ctx):
    global auQueue

    if await checkIfHasRole(ctx, 'DJ') == False:
        await ctx.send('Nincs DJ rangod.')
        return

    if len(auQueue) == 0:
        await ctx.send('Nincs lejátszásra váró hang.')
        return

    auQueue = []

    await reactToMsg(ctx, '✅')

    # silence the bot
@client.command(pass_context = True, brief='Némítás', description='Lenémít engem, vagy épp feloldja a némítást. Csak "Silencer" ranggal lehet használni.')
async def silence(ctx):
    global silenced

    role = 'Silencer'
    canSilence = False

    for item in ctx.message.author.roles:
        if item.name == role:
            canSilence = True

    if canSilence == True:
        silenced = not silenced

        if silenced == True:
            await ctx.send('Shhhh.')
        else:
            await ctx.send('Némítás feloldva.')
    else:
        await ctx.send('Nincs jogosultságod engem némítani!')


# endregion
##############################################################################################################################################################################
# region bugReporting
knownProblems = []

if os.path.exists(cts.txtPath + "bugsReported.txt"):
    with open(cts.txtPath + "bugsReported.txt") as f:
        for line in f.readlines():
            knownProblems.append(line)

global problemTypes
problemTypes = {
    0: "Hangcsatorna",
    1: "Szövegcsatorna",
    2: "Hangeffekt",
    3: "Minigame",
    4: "Egyéb"
}

@client.command(pass_context=True, aliases=['report', 'rep'], brief="Hibák jelentése", description="Ha valami hibát véltél felfedezni a botban, akkor kérlek, ezzel a paranccsal jelezd nekem.")
async def bug(ctx, problemType=None, *problemDescription):
    global problemTypes

    if problemType is None:
        await ctx.send("wau")

        s = "Probléma típusok:\n";
        for p in problemTypes:
            s += p

        await ctx.send(s)
        return
    else:
        try:
            int(problemType)
        except ValueError:
            await ctx.send("A probléma típusánál a sorszámát add meg.")
            return

        if len(problemDescription) == 0:
            await ctx.send("A probléma típusa után írd be a probléma leírását.")
            return

    problemType = problemType - 1

    descriptionString = ""
    for word in problemDescription:
        descriptionString += f"{word} "

    knownProblems.append(f"{problemTypes[problemType]} - {descriptionString}")

    with open(cts.txtPath + "bugsReported.txt", "w") as f:
        for p in knownProblems:
            f.write(p + "\n")

    await ctx.send("Köszönöm a visszajelzést. Mihamarabb nekilátok a hiba kijavításának.")




# endregion
##############################################################################################################################################################################
# region other
# wau
@client.command(pass_context = True, brief='Woof!', description='Wau gecó mit nem értesz?!')
async def wau(ctx):
    await ctx.send('Waubazdmeg.')

# poiip
@client.command(pass_context=True, brief='Poiip!', description='Poiiiiiiiiiiiiiip!')
async def poiip(ctx):

    if await checkIfHasRole(ctx.message.author, 'Poiip'):
        await play(ctx, cts.audioPath + 'other/poiip.mp3')
    else:
        await ctx.send('Imposztor!')

# endregion
##############################################################################################################################################################################
# region ppThings
# pp size
def ppcske(hossz):
    torzs = ''
    for i in range(hossz):
        torzs += "="
    return torzs

async def ppmeret(ctx):
    pelo = "8"
    pelo += ppcske(r.randint(0, 30))
    pelo += "D"

    if await checkIfHasRole(ctx, 'Jew') == True:
        pelo = pelo.replace('D', '=')

    await ctx.send(f'{ctx.message.author.name} PP-je:\n' + pelo)
    return pelo

# pp showdown
global firstContender
global firstSize
global firstContext

firstContender = True
firstSize = 0

@client.command(pass_context = True, brief='Mérd össze!', description='Egy végsőkig tartó PP leszámolás!')
async def ppshowdown(ctx):
    global firstContender
    global firstSize
    global firstContext

    if firstContender == True:
        await ctx.send(f'{ctx.message.author.name} egy PP leszámolást indított!')

        PP = await ppmeret(ctx)
        await ctx.send(f'A csatához írd be a #ppshowdown parancsot!')

        firstSize = len(PP)
        firstContext = ctx

        firstContender = False
    elif firstContext.message.author.name is not ctx.message.author.name:
        await ctx.send(f'{ctx.message.author.name} elfogadta a megmérettetést!')
        PP = await ppmeret(ctx)

        # PP role assignment

        for person in ctx.author.guild.members:
            for role in person.roles:
                if role.name == 'Enormous PP':
                    await person.remove_roles(role)

        # PP role assignment end

        if firstSize < len(PP):
            await ctx.send(f'A PP leszámolást {ctx.message.author.name} nyerte!\n{firstContext.message.author.name} mikropénisszel él!')
            await assignRole(ctx, 'Enormous PP')
        elif firstSize > len(PP):
            await ctx.send(f'A PP leszámolást {firstContext.message.author.name} nyerte!\n{ctx.message.author.name} mikropénisszel él!')
            await assignRole(firstContext, 'Enormous PP')
        else:
            await ctx.send(f'A PP leszámolás döntetlen! Egyensúly!!!')

        firstContender = True
    else:
        await ctx.send('Nem mérheted össze önmagaddal!')

# endregion
##############################################################################################################################################################################
# region TTT
# tic tac toe
global tictac
tictac = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
global isMatchOn
isMatchOn = False
global p1
global p2
global pTurn
global turnCount

@client.command(pass_context = True, brief='Tic-Tac-Toe játék', description='TTT játék létrehozásához a launch, csatlakozáshoz a join paramétert kell megadni mögötte. (#ttt paraméter)')
async def ttt(ctx, action):
    global tictac
    global isMatchOn
    global p1
    global p2
    global pTurn
    global turnCount

    if action == 'launch':
        if isMatchOn == False:
            tictac = [['□', '□', '□'], ['□', '□', '□'], ['□', '□', '□']]
            p1 = ctx.message.author.name
            await ctx.send(f'{p1} egy Tic-Tac-Toe meccset akar indítani. Ki lesz a másik játékos? (#ttt join)')
        else:
            await ctx.send(f'{p1} és {p2} között már van egy játék. Várd meg a végét!')

    elif action == 'join':
        if isMatchOn == False:
            if p1 is not ctx.message.author.name:
                p2 = ctx.message.author.name
                isMatchOn = True

                await ctx.send(f'{p2} lesz {p1} ellenfele.')

                if r.randint(0, 1) == 0:
                    pTurn = p1
                    await ctx.send(f'{p1} kezd.')
                else:
                    pTurn = p2
                    await ctx.send(f'{p2} kezd.')

                turnCount = 0

                await showTTT(ctx)
            else:
                await ctx.send(f'Magad ellen nem játszhatsz!')
        else:
            await ctx.send(f'{p1} és {p2} között már van egy játék. Várd meg a végét!')
    else:
        await ctx.send(f'Ismeretlen (#ttt {action}) parancs. Typo?')

@client.command(pass_context = True, brief='TTT bevitel', description='TTT közben koordináta alapú rendszerként megadható, hogy hova szeretnéd tenni a keresztet/kört (#move x y). Az (1; 1) koordináta a bal felső sarok. Pl: a #move 3 1 parancs a jobb felső sarokba fogja rakni a lépést.')
async def move(ctx, xCor, yCor):
    global tictac
    global isMatchOn
    global p1
    global p2
    global pTurn

    xCor = int(xCor)
    yCor = int(yCor)

    if isMatchOn is False:
        await ctx.send('Nincs folyamatban lévő játék. (#ttt launch)')
    else:
        if ctx.message.author.name is not p1 and ctx.message.author.name is not p2:
            await ctx.send('Te nem veszel részt ebben a játékban.')
        elif ctx.message.author.name is not pTurn:
            await ctx.send('Nem a te köröd van.')
        else:
            if not (0 < xCor < 4 and 0 < yCor < 4):
                await ctx.send('Érvénytelen lépés. Próbáld újra.')
            else:
                # actual move
                xCor = xCor - 1
                yCor = yCor - 1

                if tictac[yCor][xCor] == 'X' or tictac[yCor][xCor] == 'O':
                    await ctx.send('Érvénytelen lépés. Próbáld újra.')
                else:
                    if pTurn == p1:
                        tictac[yCor][xCor] = 'X'

                        pTurn = p2

                        await showTTT(ctx)

                        await checkTTT(ctx)
                    else:
                        tictac[yCor][xCor] = 'O'

                        pTurn = p1

                        await showTTT(ctx)

                        await checkTTT(ctx)

async def showTTT(ctx):
    global tictac
    tttString = ''

    for i in range(3):
        tttString += (str(tictac[i][0]) + ' ' + str(tictac[i][1]) + ' ' + str(tictac[i][2]) + '\n')

    await ctx.send(tttString)

async def checkTTT(ctx):
    global tictac
    global p1
    global p2
    global isMatchOn
    global turnCount

    # raise turnCount
    turnCount = turnCount + 1

    # a list will store possible solves
    solves = list()
    p1solve = ['X', 'X', 'X']
    p2solve = ['O', 'O', 'O']

    # add columns
    for i in range(3):
        solves.append([tictac[0][i], tictac[1][i], tictac[2][i]])
    # add rows
    for i in range(3):
        solves.append([tictac[i][0], tictac[i][1], tictac[i][2]])
    # add diagonal
    solves.append([tictac[0][0], tictac[1][1], tictac[2][2]])
    solves.append([tictac[2][0], tictac[1][1], tictac[0][2]])

    # check results
    if p1solve in solves:
        await ctx.send(f'{p1} nyert!')
    elif p2solve in solves:
        await ctx.send(f'{p2} nyert!')
    else:
        if turnCount == 9:
            await ctx.send('Döntetlen játék!')
        else:
            return

    # stop game
    isMatchOn = False
    p1 = None
    p2 = None

# endregion
##############################################################################################################################################################################
# region szolancGame
# szolanc
global chain
chain = list()
global lastWord
global lastWordCreator

@client.command(pass_context = True, brief='Szólánc játék', description='Írj be egy szót és zsalhat a szólánc.')
async def szl(ctx, word):
    global chain
    global lastWord
    global lastWordCreator

    if len(chain) > 0:
        if lastWordCreator == ctx.message.author.name:
            await ctx.send('Nem írhatsz a saját szavad után.')
            return

    ervenyesSzo = True

    if len(word) < 1:
        ervenyesSzo = False
    else:
        for letter in word:
            if letter.isalpha() == False:
                ervenyesSzo = False
                break

    if ervenyesSzo == False:
        await ctx.send('Érvénytelen bevitel.')
        return

    if len(chain) == 0:
        await ctx.send(f'{ctx.message.author.name} szóláncot indított! A kezdő szó: {word}')
        chain.append(word.lower())
        lastWord = word.lower()
        lastWordCreator = ctx.message.author.name
    else:
        if lastWord.lower()[-1] == word.lower()[0]:
            if word.lower() in chain:
                await ctx.send('Ez a szó már volt!')
                return
            else:
                await ctx.send(f'{ctx.message.author.name} szava: {word}')
                chain.append(word.lower())
                lastWord = word.lower()
                lastWordCreator = ctx.message.author.name
        else:
            await ctx.send(f'{ctx.message.author.name} elrontotta a szóláncot! Az ő szava "{word}" lett volna.')
            await ctx.send(f'A szólánc {len(chain)} szó hosszúságnál tört meg. A szólánc:')

            finalChain = ''
            for eachWord in chain:
                finalChain += eachWord + ' '
            await ctx.send(finalChain)

            chain = list()
            lastWord = None

@client.command(pass_context = True, brief='Kiírja a szóláncot.', description='Kiírja a szóláncot, ha van jelenleg folyamatban lévő játék.')
async def showszl(ctx):
    global chain
    currentChain = ''

    if len(chain) > 0:
        await ctx.send('A szólánc jelenleg:')
        for word in chain:
            currentChain += word + ' '
        await ctx.send(currentChain)
    else:
        await ctx.send('Nincs folyamatban lévő szólánc játék.')

# endregion
##############################################################################################################################################################################
# region coinToss
# fej vagy iras
@client.command(pass_context = True, brief='Fej vagy írás?', description='Dobj fel egy érmét! Vajon fej lesz? Vagy talán írás? Vagy talán egyik sem?')
async def coin(ctx):
    generatedNumber = r.randint(0, 1000)

    if generatedNumber == 0:
        await ctx.send(f'Az érme az élére esett!\n{ctx.message.author.name} egy champ!')
        await ctx.message.pin()
    elif generatedNumber % 2 == 0:
        await ctx.send('Fej!')
    else:
        await ctx.send('Írás!')

# endregion
##############################################################################################################################################################################
# region dice
# dobokocka
@client.command(pass_context=True, brief='N oldalú dobókocka, K db dobás.', description='Szabadon választott N oldalú dobókocka szimulátor, ami K-szor hajtódik végre.')
async def dice(ctx, N, K):
    safetyNLimit = 100000
    safetyKLimit = 100

    if N.isdigit() == False or K.isdigit() == False:
        await ctx.send('Helytelen bevitel.')
        return
    elif int(K) > safetyKLimit:
        await ctx.send('Ne próbálj meg kinyírni kérlek. 100 dobás a limit.')
        return
    elif int(N) > safetyNLimit:
        await ctx.send('Ne próbálj meg kinyírni kérlek. 100.000 oldalú lehet a legnagyobb kocka.')
        return
    elif int(K) < 1 or int(N) < 1:
        await ctx.send('Túl kicsi valamelyik érték. Próbáld újra.')
        return

    dobasok = ''

    for i in range(int(K)):
        dobasok += str(r.randint(1, int(N))) + ' '

    await ctx.send(f'Dobásaid:\n{dobasok}')

# endregion
##############################################################################################################################################################################
# region maths
# matek függvények
    # masodfoku
@client.command(pass_context=True, brief='Másodfokú egyenlet', description='Másodfokú egyenlet megoldóképlet')
async def quad(ctx, a, b, c):
    eredmeny = list()

    a = float(a)
    b = float(b)
    c = float(c)

    if a == 0:
        await ctx.send('Az "a" nem lehet 0, hiszen akkor nem másodfokú az egyenleted.')
        return

    d = (b**2) - 4 * a * c

    if d < 0:
        await ctx.send(f'Nincs megoldás.')
        return

    gyok = (-b + m.sqrt(d)) / (2 * a)
    eredmeny.append(gyok)
    gyok = (-b - m.sqrt(d)) / (2 * a)
    eredmeny.append(gyok)

    if d == 0:
        await ctx.send(f'x = {eredmeny[0]}')
    else:
        await ctx.send(f'x1 = {eredmeny[0]}\nx2 = {eredmeny[1]}')

# endregion
##############################################################################################################################################################################
# region physics
# fizika függvények
    # lambda-v-f
@client.command(pass_context=True, brief='lambda-v-f', description='Adj meg neki a 3 értékből 2-t, és visszaadja a 3.at. A hiányzó érték helyére írd azt, hogy "None".')
async def hangseb(ctx, la, v, f):

    if la != 'None':
        la = float(la)
    if v != 'None':
        v = float(v)
    if f != 'None':
        f = float(f)

    if la == 'None':
        eredmeny = v / f;
    elif v == 'None':
        eredmeny = la * f;
    elif f == 'None':
        eredmeny = v / la;

    await ctx.send(f'A hiányzó tag: {eredmeny}')

    # T-f
@client.command(pass_context=True, brief='f-T', description='Periódusidőből frekvenciát ad vissza, és fordítva.')
async def frekper(ctx, ft):
    await ctx.send(f'A keresett érték: {1 / float(ft)}')

    # s-v-t
@client.command(pass_context=True, brief='s-v-t', description='Adj meg neki a 3 értékből 2-t, és visszaadja a 3.at. A hiányzó érték helyére írd azt, hogy "None".')
async def utido(ctx, s, v, t):
                                                                                                                                                                                                                                    # snoop
    if s != 'None':
        s = float(s)
    if v != 'None':
        v = float(v)
    if t != 'None':
        t = float(t)

    if s == 'None':
        eredmeny = v * t;
    elif v == 'None':
        eredmeny = s / t;
    elif t == 'None':
        eredmeny = s / v;

    await ctx.send(f'A hiányzó tag: {eredmeny}')

# endregion
##############################################################################################################################################################################
# region reminderSystem
# reminders logged
global remindersList
remindersList = []

with open(cts.txtPath + 'savedReminders.txt', encoding='utf8') as f:
    for row in f:
        row = row.split()
        remindersList.append(row)

# reminder command
@client.command(pass_context = True, aliases=['reminder', 'rem'], brief='Emlékeztető beállítása', description='Egy emlékeztető beállításához ezt írd be: #remind *óra:perc* *emlékeztető*\nEmlékeztetőt az elkövetkező 24 órára vonatkozóan lehet létrehozni.')
async def remind(ctx, *args):
    global remindersList

    if ctx.message.channel.id != 784430919867039764:
        await ctx.message.delete()
        warningMessage = await ctx.send('Az emlékeztetőket az emlékeztető szövegcsatornában használd!')
        await asyncio.sleep(3)
        await warningMessage.delete()
        return

    l = len(args)

    if l > 0:
        try:
            int(args[0].split(':')[0])
            int(args[0].split(':')[1])
        except ValueError:
            await ctx.send('Az időpontot óra:perc formátumban kell megadni.')
            return

    if l == 0:
        await ctx.send('Hány órára szeretnéd az emlékeztetőt? (óra:perc)')
    elif l == 1:
        await ctx.send('Miről szeretnél emlékeztetőt? (Időpont után írd.)')
    elif l > 1:
        await ctx.send('Emlékeztető rögzítve.')

        thisReminder = []
        thisReminder.append(str(ctx.message.author.id))
        for item in args:
            thisReminder.append(item)
        remindersList.append(thisReminder)

        saveReminders()

        reminderTask = asyncio.get_event_loop()
        await reminderTask


# remind
async def reminderCoroutine():
    now = datetime.datetime.now().strftime("%H:%M")

    for rem in remindersList:
        if rem[1] == now:
            await remindOfReminder(rem)
            remindersList.remove(rem)
            saveReminders()

    await asyncio.sleep(30)

    reminderTask = asyncio.create_task(reminderCoroutine())
    await reminderTask

async def remindOfReminder(theReminder):
    reminderChannel = client.guilds[0].get_channel(784430919867039764)

    user = client.get_user(int(theReminder[0]))

    theReminder.remove(theReminder[0])
    theReminder.remove(theReminder[0])

    reminderString = ''
    for item in theReminder:
        reminderString += ' ' + item

    await reminderChannel.send(user.mention + ' Az emlékeztetőd:' + reminderString)

# save reminders to file
def saveReminders():
    with open(cts.txtPath + 'savedReminders.txt', 'w', encoding='utf8') as f:
        for rem in remindersList:
            rowString = ''
            for item in rem:
                rowString += item + ' '
            f.write(rowString.strip() + '\n')


# endregion
##############################################################################################################################################################################
# launch bot
load_dotenv()
client.run(os.getenv("TOKEN"))
##############################################################################################################################################################################
