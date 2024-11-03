##############################################################################################################################################################################
# region imports
# imports
import os
import discord
from discord.utils import get
import asyncio
import time
import datetime
import random as r
import math as m
import mvpconstants as cts
from pokemon import PokemonClass
from pokemonInv import PokemonInventory as inv
from pokemonFight import FightClass as Fight

global eventRoomId
eventRoomId = 781694226555469864
global fightRoomIds
fightRoomIds = [782937652563410974, 789169188434346005, 789169220290215966, 789169244679438357]
global channelIDs
channelIDs = [781666780736389170, 781666876170043392, 781666278464946196, 781666651640561684, 781666719898796052]


# endregion
##############################################################################################################################################################################
# region loading
# loading globals
global path
path = cts.pokemonPath
global wildPokemons
wildPokemons = []
global ownedPokemons
ownedPokemons = []
global eventUsers
eventUsers = []

with open(path + 'pokemonWilds.txt') as pokemonWilds:
    for row in pokemonWilds.readlines():
        wildPokemonAttributes = row.split()
        savedWildPokemon = PokemonClass(wildPokemonAttributes[0], int(wildPokemonAttributes[1]), int(wildPokemonAttributes[2]))
        wildPokemons.append(savedWildPokemon)

with open(path + 'caughtPokemons.txt') as caughtPokemons:
    for row in caughtPokemons.readlines():
        pokemonAttributes = row.split()
        ownedPokemons.append(PokemonClass(pokemonAttributes[0], int(pokemonAttributes[1]), int(pokemonAttributes[2]), int(pokemonAttributes[3]), int(pokemonAttributes[4]), int(pokemonAttributes[5]), int(pokemonAttributes[6])))

with open(path + 'partTakingUsers.txt') as joinedUsers:
    for row in joinedUsers.readlines():
        values = row.split()
        loginDateValues = [int(values[7]), int(values[8]), int(values[9]), int(values[10]), int(values[11])]
        rememberedUser = inv(int(values[0]), int(values[1]), int(values[2]), int(values[3]), int(values[4]), int(values[5]), int(values[6]), loginDateValues)
        eventUsers.append(rememberedUser)

# get list of pokemon names
global pokemonNames
pokemonNames = []

with open(path + 'pokemonNames.txt') as pokemonNameFile:
    for row in pokemonNameFile:
        pokemonNames.append(row.strip())

# pokemon spawnrate
global spawnrate
spawnrate = 1

# pokemon fighting
global allFights
allFights = []

with open(path + 'pokemonFights.txt') as f:
    for row in f.readlines():
        row = row.strip().split()
        p1 = int(row[0])
        p1pok = PokemonClass(row[1], int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]))
        p2 = int(row[8])
        p2pok = PokemonClass(row[9], int(row[10]), int(row[11]), int(row[12]), int(row[13]), int(row[14]), int(row[15]))
        turnID = int(row[16])
        defMultiplier = [float(row[17]), float(row[18])]
        fight = Fight(p1, p1pok, p2, p2pok, turnID, defMultiplier)
        allFights.append(fight)

global waitingFighters
waitingFighters = [[], [], [], []]

with open(path + 'fightQueue.txt') as f:
    index = 0
    for row in f.readlines():
        row = row.strip().split()

        if row[0] == '-':
            waitingFighters[index] = []
            index += 1
        else:
            fighterID = int(row[0])
            fighterPokemon = PokemonClass(row[1], int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]))
            waitingFighters[index] = [fighterID, fighterPokemon]
            index += 1

# pokemon transfer
global highDemandPokemons
highDemandPokemons = []
global lastDemandChange
lastDemandChange = []

with open(path + 'highDemandPokemonNames.txt') as f:
    firstRow = f.readline().strip().split()
    for i in range(5):
        lastDemandChange.append(int(firstRow[i]))

    for name in f.readlines()[0:]:
        highDemandPokemons.append(name.strip())

# endregion
##############################################################################################################################################################################
# region help
# print event help file
async def printHelp(ctx, helpFileName):
    if ctx.message.channel.id != eventRoomId:
        await ctx.send('Ezt a parancsot a pokémon-event szobában használd!')
        return

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if os.path.isfile(path + 'helps/' + helpFileName + '.txt') == False:
        await ctx.send('Nincs ilyen segítség.')
        return

    await ctx.send(open(path + 'helps/' + helpFileName + '.txt', encoding='utf8').read())
# endregion
##############################################################################################################################################################################
# region joinExitAndChecking
# ability to join and exit the event
async def joinEvent(msg):
    if inEvent(msg.author.id) == True:
        warningMessage = await msg.channel.send('Már részt veszel az eventen.')
        await asyncio.sleep(3)
        await warningMessage.delete()
        return

    if msg.channel.id != 778331044641636443:
        warningMessage = await msg.channel.send('Ezt a parancsot csak az mvp szobában lehet használni.')
        await msg.delete()
        await asyncio.sleep(3)
        await warningMessage.delete()
        return

    now = datetime.datetime.now().strftime("%y:%m:%d:%H:%M").split(':')
    for i in range(5):
        now[i] = int(now[i])

    await discord.Member.add_roles(msg.author, get(msg.author.guild.roles, name='Pokemon Participant'))

    thisUser = inv(msg.author.id, 100, 5, 1, 1, 1, 1, now)
    eventUsers.append(thisUser)
    await msg.guild.get_channel(eventRoomId).send(f'Üdv a pokémon eventen {msg.author.name}!\nA csatlakozásért kezdőfelszerelést kaptál.')

    await saveState()

    await msg.delete()

async def exitEvent(msg):
    global ownedPokemons

    if inEvent(msg.author.id) == True:
        for p in ownedPokemons:
            if p.owner == msg.author.id:
                ownedPokemons.remove(p)

        eventUsers.remove(getInv(msg.author.id))

        await msg.author.send('Remélem azért tetszett a pokémon event. Az összegyűjtött pénzed, valamint a pokémonjaid és tárgyaid a laborba kerültek.')

        await discord.Member.remove_roles(msg.author, get(msg.guild.roles, name='Pokemon Participant'))

        await saveState()
        return

    await msg.channel.send('Már nem veszel részt az eventen.')

# check if user is in event
def inEvent(id):
    for u in eventUsers:
        if id == u.userID:
            return True
    return False

# get user inventory
def getInv(id):
    for u in eventUsers:
        if id == u.userID:
            return u
    return None

# endregion
##############################################################################################################################################################################
# region startingEvent
# start event, declare progress, remember client
global client
global inProgress
inProgress = False

global pokemonCoroutineTask
pokemonCoroutineTask = None

async def startPME(bot):
    global inProgress
    global client
    global pokemonCoroutineTask

    client = bot

    print('PokemonEvent is active.')

    if inProgress == False:
        inProgress = True
        pokemonCoroutineTask = asyncio.create_task(pokemonCoroutine())
        await pokemonCoroutineTask


# endregion
##############################################################################################################################################################################
# region dailyLogin
# daily login
async def userLogin(ctx):
    global eventUsers

    user = [u for u in eventUsers if u.userID == ctx.message.author.id]

    if len(user) < 1:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    user = user[0]
    loginDate = datetime.datetime.now().strftime("%y:%m:%d:%H:%M").split(':')
    for i in range(5):
        loginDate[i] = int(loginDate[i])

    if user.canLogin(loginDate) == False:
        await ctx.send(f'Még nem telt el 24 óra az utolsó bejelentkezésed ({user.lastLoginString()}) óta.')
        return

    user.pokeCoins += 100
    user.pokeBalls += 5

    randomItems = [0, 0, 0, 0]
    for i in range(4):
        randomItems[r.randint(0, 3)] += 1

    user.incenses += randomItems[0]
    user.trackers += randomItems[1]
    user.potions += randomItems[2]
    user.elixirs += randomItems[3]

    await ctx.send('A napi belépésért kaptál 100C-t, 5 PokéBall-t, valamint 4 egyéb felszerelést!')

    user.lastLoginDate = loginDate

    await saveState()

# endregion
##############################################################################################################################################################################
# region pokemonSpawning
# spawn pokemon at random intervals
async def pokemonCoroutine():
    global pokemonCoroutineTask
    global wildPokemons

    name = pokemonNames[r.randint(0, len(pokemonNames) - 1)]

    tier = r.randint(1, 4)
    if tier > 1: tier = r.randint(1, 4)
    if tier > 2: tier = r.randint(1, 4)
    if tier > 3: tier = r.randint(1, 4)

    cp = r.randint(1 + 1000 * (tier - 1), 1000 * tier)

    home = channelIDs[r.randint(0, len(channelIDs) - 1)]
    newPokemon = PokemonClass(name, cp, home)

    await client.guilds[0].get_channel(newPokemon.home).send(f'Egy vad {newPokemon.name} jelent meg! CP: {newPokemon.cp}')

    wildPokemons.append(newPokemon)

    await saveState()

    #await asyncio.sleep(60 / spawnrate)
    await asyncio.sleep(r.randint(60 * 20 / spawnrate, 60 * 30 / spawnrate)) # original spawning time

    pokemonCoroutineTask = asyncio.create_task(pokemonCoroutine())
    await pokemonCoroutineTask

# endregion
##############################################################################################################################################################################
# region pokemonClaimAndCheck
# ability to claim pokemons
async def claimPokemon(ctx, name, cp):
    global wildPokemons
    global ownedPokemons

    if inEvent(ctx.message.author.id) == False:
        return 'Még nem veszel részt az eventen. (#pok join)'

    if len(wildPokemons) < 1:
        return 'Nincs elfogható pokémon a láthatáron.'

    if getInv(ctx.message.author.id).pokeBalls < 1:
        return 'Nincs PokéBall-od!'

    for p in wildPokemons:
        if p.name.lower() == name.lower() and p.cp == cp and p.home == ctx.message.channel.id:
            p.owner = ctx.message.author.id
            ownedPokemons.append(p)
            wildPokemons.remove(p)
            await ctx.message.add_reaction('✅')

            getInv(ctx.message.author.id).pokeBalls -= 1

            await saveState()

            return 'Pokémon sikeresen elfogva.'

    return 'Nincs ilyen pokémon.'

# ability to check owned pokemons
async def checkPokemons(msg):
    pokemonString = ''

    if inEvent(msg.author.id) == False:
        return 'Még nem veszel részt az eventen. (#pok join)'

    ownedPokemonsCP = 0
    selfPokemons = []
    maxNameLength = 0

    for p in ownedPokemons:
        if p.owner == msg.author.id:
            selfPokemons.append(PokemonClass(p.name, p.cp, p.home, p.owner, p.tier, p.hp, p.pp))

    for p in selfPokemons:
        p.cp = str(p.cp)
        p.hp = str(p.hp)
        p.pp = str(p.pp)

        if len(p.name) > maxNameLength:
            maxNameLength = len(p.name)

    for p in selfPokemons:
        while len(p.name) < maxNameLength:
            p.name += ' '
        while len(p.cp) < 4:
            p.cp = ' ' + p.cp
        while len(p.hp) < 4:
            p.hp = ' ' + p.hp
        while len(p.pp) < 2:
            p.pp = ' ' + p.pp

    for p in selfPokemons:
        pokemonString += p.getInfoTag() + '\n'
        ownedPokemonsCP += int(p.cp.replace(' ', ''))

    if len(pokemonString) == 0:
        await msg.author.send('```Még nem fogtál el egy pokémont sem.```')
    else:
        await msg.author.send(f'```Pokémonjaid:\n{pokemonString}\nÖsszes CP: {str(ownedPokemonsCP)}```')

    await msg.delete()

# endregion
##############################################################################################################################################################################
# region itemsAndInventory
# list inventory
def listInventory(ctx):
    if inEvent(ctx.message.author.id) == False:
        return 'Még nem veszel részt az eventen. (#pok join)'

    return getInv(ctx.message.author.id).listItems()

# item usage
# incenses
global incenseInUse
incenseInUse = False
global incenseWaitTime
incenseWaitTime = 60 * 30

async def useIncense(ctx):
    global incenseInUse
    global spawnrate
    global pokemonCoroutineTask

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if incenseInUse == True:
        await ctx.send('Már van egy Incense használatban!')
        return

    if ctx.message.channel.id != eventRoomId:
        await ctx.message.delete()
        await ctx.send('Ezt a parancsot a pokémon-event szobában használd!')
        return

    if getInv(ctx.message.author.id).incenses < 1:
        await ctx.send('Nincs Incense-ed!')
        return

    pokemonCoroutineTask.cancel()

    spawnrate = 2
    getInv(ctx.message.author.id).incenses -= 1
    incenseInUse = True
    await ctx.send('Aktiváltál egy Incense-t! Az elkövetkező fél órában több pokémon várható!')

    await saveState()

    pokemonCoroutineTask = asyncio.create_task(pokemonCoroutine())
    await pokemonCoroutineTask

    await incenseExpire(ctx)

async def incenseExpire(ctx):
    global incenseInUse

    await asyncio.sleep(incenseWaitTime)

    await ctx.send(f'Lejárt a(z) {ctx.message.author.name} által aktivált Incense!')

    incenseInUse = False

# tracker
async def useTracker(ctx):
    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id not in channelIDs:
        await ctx.message.delete()
        await ctx.send('Ez nem egy pokémon spawn hely!')
        return

    if getInv(ctx.message.author.id).trackers < 1:
        await ctx.send('Nincs Tracker-ed!')
        return

    trackerString = ''
    for p in wildPokemons:
        if p.home == ctx.message.channel.id:
            trackerString += 'Név: ' + p.name + '\tCP: ' + str(p.cp) + '\n'

    if len(trackerString) == 0:
        await ctx.send('Ezen a csatornán nincs vad pokémon. A Tracker-ed nem használódott el.')
        return

    await ctx.send(f'**Ezen a csatornán spawnolt, el nem fogott pokémonok listája:**\n{trackerString}')

    getInv(ctx.message.author.id).trackers -= 1

    await saveState()

# potion
async def usePot(ctx, pokemonName, pokemonCP):
    global ownedPokemons

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id != eventRoomId:
        await ctx.send('Ezt a parancsot a pokémon event csatornán használd!')
        return

    try:
        int(pokemonCP)
    except ValueError:
        await ctx.send('A pokémon CP-je csak egy egész szám lehet!')
        return

    if getInv(ctx.message.author.id).potions < 1:
        await ctx.send('Nincs Potion-öd!')
        return

    pokemonToHeal = [p for p in ownedPokemons if p.name.lower() == pokemonName.lower() and p.cp == int(pokemonCP)]

    if len(pokemonToHeal) == 0:
        await ctx.send('Nincs ilyen pokémonod.')
        return

    pokemonToHeal = pokemonToHeal[0]

    if pokemonToHeal.hp == pokemonToHeal.cp:
        await ctx.send('Ezt a pokémont nem kell gyógyítani.')
        return

    healAmount = r.randint(100, 150) * 10

    if pokemonToHeal.hp + healAmount >= pokemonToHeal.cp:
        pokemonToHeal.hp = pokemonToHeal.cp
        await ctx.send('A pokémonod teljesen meggyógyult.')
    else:
        pokemonToHeal.hp += healAmount
        await ctx.send(f'A pokémonod {healAmount} életpontot gyógyult. Mostani élete: {pokemonToHeal.hp} HP.')

# elixir
async def useElix(ctx, pokemonName, pokemonCP):
    global ownedPokemons

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id != eventRoomId:
        await ctx.send('Ezt a parancsot a pokémon event csatornán használd!')
        return

    try:
        int(pokemonCP)
    except ValueError:
        await ctx.send('A pokémon CP-je csak egy egész szám lehet!')
        return

    if getInv(ctx.message.author.id).elixirs < 1:
        await ctx.send('Nincs Elixir-ed!')
        return

    pokemonToCharge = [p for p in ownedPokemons if p.name.lower() == pokemonName.lower() and p.cp == int(pokemonCP)]

    if len(pokemonToCharge) == 0:
        await ctx.send('Nincs ilyen pokémonod.')
        return

    pokemonToCharge = pokemonToCharge[0]

    if pokemonToCharge.pp == pokemonToCharge.tier * 5:
        await ctx.send('Ennek a pokémonnak a harci erejét nem kell visszatölteni.')
        return

    chargeAmount = r.randint(2, 4) * 5

    if pokemonToCharge.pp + chargeAmount >= pokemonToCharge.tier * 5:
        pokemonToCharge.pp = pokemonToCharge.tier * 5
        await ctx.send('A pokémonod harci ereje teljesen feltöltődött!')
    else:
        pokemonToCharge.pp += chargeAmount
        await ctx.send(f'A pokémonod {chargeAmount} Power Point-ot visszatöltött. Mostani PP-je: {pokemonToHeal.pp} PP.')



# endregion
##############################################################################################################################################################################
# region shopping
# shopping
global itemPrices
itemPrices = [20, 100, 40, 30, 40] # pokeball, incense, tracker, potion, elixir

async def buyItem(ctx, itemIndex, itemCount):
    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id != eventRoomId:
        await ctx.message.delete()
        await ctx.send('A pokémon parancsokat a pokémon-event csatornán használd!')
        return

    if itemCount < 1:
        await ctx.send('Helytelen mennyiséget adtál meg.')
        return

    if getInv(ctx.message.author.id).pokeCoins < itemPrices[itemIndex] * itemCount:
        if itemCount == 1:
            await ctx.send('Nincs elég PokeCoin-od ennek a tárgynak a megvásárlására.')
        else:
            await ctx.send('Nincs elég PokeCoin-od ezeknek a tárgyaknak a megvásárlására.')
        return

    if itemIndex == 0:
        getInv(ctx.message.author.id).pokeBalls += itemCount
    elif itemIndex == 1:
        getInv(ctx.message.author.id).incenses += itemCount
    elif itemIndex == 2:
        getInv(ctx.message.author.id).trackers += itemCount
    elif itemIndex == 3:
        getInv(ctx.message.author.id).potions += itemCount
    elif itemIndex == 4:
        getInv(ctx.message.author.id).elixirs += itemCount
    else:
        await ctx.send('A bolt nem árul ilyen terméket.')
        return

    getInv(ctx.message.author.id).pokeCoins -= itemPrices[itemIndex] * itemCount

    await ctx.send(f'Sikeres vásárlás. Az egyenlegedről {itemPrices[itemIndex] * itemCount}C levonásra került.')

    await saveState()

def listShopContents():
    return f'**A boltban vásárolható termékek:**\n-------------------------------------\nPokéBall (ball/pokeball) - {itemPrices[0]}C\n-------------------------------------\nTracker (track/tracker) - {itemPrices[2]}C\nIncense (inc/incense) - {itemPrices[1]}C\n-------------------------------------\nPotion (pot/potion) - {itemPrices[3]}C\nElixir (elix/elixir) - {itemPrices[4]}C'

# endregion
##############################################################################################################################################################################
# region fightSystem
# pokemon fights
async def pokemonFight(ctx, tierNumber, pokemonName, pokemonCP):
    global ownedPokemons
    global allFights
    global waitingFighters

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if tierNumber < 1 or tierNumber > 4 and tierNumber % 1 != 0:
        await ctx.send('Csak 1-től 4-ig vannak szintek, amikben harcolhatnak a pokémonok.')
        return

    if ctx.message.channel.id != fightRoomIds[tierNumber - 1]:
        await ctx.send('Ezt a parancsot csak a szintnek megfelelő pokémon-harc szobában lehet használni!')
        return

    allFighterIDs = []
    for fight in allFights:
        allFighterIDs.append(fight.players[0])
        allFighterIDs.append(fight.players[1])

    if ctx.message.author.id in allFighterIDs:
        await ctx.send('Már részt veszel egy harcban. Először azt fejezd be.')
        return

    allFighterIDs = []
    for fighter in waitingFighters:
        if fighter != []:
            allFighterIDs.append(fighter[0])

    if ctx.message.author.id in allFighterIDs:
        await ctx.send('Már indítottál egy harcot.')
        return

    correctPokemon = None
    for p in ownedPokemons:
        if p.name.lower() == pokemonName.lower() and p.cp == pokemonCP and p.owner == ctx.message.author.id:
            correctPokemon = p
            break

    if correctPokemon == None:
        await ctx.send('Nincs ilyen pokémonod.')
        return

    if correctPokemon.tier != tierNumber:
        await ctx.send('Ez a pokémon nem ebbe a tier-be tartozik, nem szállhatsz vele harcba.')
        return

    if correctPokemon.hp <= 0:
        await ctx.send('A pokémonod túl gyenge a harchoz! Töltsd fel a HP-ját egy Potion-nel!')
        return

    if waitingFighters[tierNumber - 1] == []:
        waitingFighters[tierNumber - 1] = [ctx.message.author.id, correctPokemon]
        ownedPokemons.remove(correctPokemon)
        await ctx.send(f'{ctx.message.author.name} harcot szeretne indítani! Szint: {tierNumber}\nPokémonja: {correctPokemon.getInfo()}\nA csatlakozáshoz "#pok fight szint_száma pokémonod_neve pokémonod_cpje"')
    else:
        newFight = Fight(waitingFighters[tierNumber - 1][0], waitingFighters[tierNumber - 1][1], ctx.message.author.id, correctPokemon)
        ownedPokemons.remove(correctPokemon)
        allFights.append(newFight)
        waitingFighters[tierNumber - 1] = []
        await ctx.send(f'{ctx.message.author.name} beszállt a harcba!\nPokémonja: {correctPokemon.getInfo()}\nGyőzzön a legjobb!\n{client.guilds[0].get_member(newFight.turnID).name} kezdi a csatát!')

    await saveState()

async def cancelFight(ctx):
    global allFights
    global waitingFighters

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id not in fightRoomIds:
        await ctx.send('Ezt a parancsot csak pokémon-harc szobákban lehet használni!')
        return

    allFighterIDs = []
    for fight in allFights:
        allFighterIDs.append(fight.players[0])
        allFighterIDs.append(fight.players[1])

    if ctx.message.author.id in allFighterIDs:
        await ctx.send('Már folyamatban van a harcod. Ha ki akarsz lépni, akkor a "#pok fight surrender" paranccsal tudod feladni a te körödben.')
        return

    allFighterIDs = []
    allFighterIDs = [waitingFight for waitingFight in waitingFighters if waitingFight is not []]
    for fight in allFighterIDs:
        if len(fight) != 0:
            if fight[0] == ctx.message.author.id:
                waitingFighters.remove(fight)
                ownedPokemons.append(fight[1])
                await ctx.send('Visszavontad a harcot.')
                await saveState()
                return

    await ctx.send('Jelenleg nem vársz harcra.')

async def closeFight(ctx, winnerMem, fight):
    global ownedPokemons
    global allFights

    for p in fight.pokemons:
        if p.hp <= 0:
            p.hp = int(p.cp / 2)
            p.owner = winnerMem.id

    ownedPokemons.append(fight.pokemons[0])
    ownedPokemons.append(fight.pokemons[1])

    allFights.remove(fight)
    await saveState()

def getUserFightIndex(ctx):
    global allFights

    id = ctx.message.author.id
    userFightIndex = None

    for index in range(len(allFights)):
        if allFights[index].players[0] == id or allFights[index].players[1] == id:
            userFightIndex = index
            break

    return userFightIndex

async def fightAction(ctx, action):
    global allFights
    global eventUsers

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if getUserFightIndex(ctx) == None:
        await ctx.send('Még nem vagy harcban.')
        return

    if action == 'heal' and getInv(ctx.message.author.id).potions < 1:
        await ctx.send('Nincs Potion-öd!')
        return
    elif action == 'charge' and getInv(ctx.message.author.id).elixirs < 1:
        await ctx.send('Nincs Elixir-ed!')

    fight = allFights[getUserFightIndex(ctx)]

    await ctx.send(fight.doTurn(ctx.message.author.id, action))

    if fight.successfulTurn == True:
        if action == 'heal':
            getInv(ctx.message.author.id).potions -= 1
        elif action == 'charge':
            getInv(ctx.message.author.id).elixirs -= 1

        if fight.checkWinner() == None:
            await ctx.send(f'{client.guilds[0].get_member(fight.turnID).name} következik!\nÁllás:\n{fight.getFightState()}')
            await saveState()
        else:
            winner = client.guilds[0].get_member(fight.checkWinner())
            loser = fight.getOtherUser(fight.checkWinner())
            await ctx.send(f'A harcot {winner.name} nyerte! {client.guilds[0].get_member(loser).name} elvesztette {fight.pokemons[fight.getUserIndex(loser)].name} pokémonját!')
            await closeFight(ctx, winner, fight)

# endregion
##############################################################################################################################################################################
# region leaderboardAndWinning
async def listLeaderBoard(ctx):
    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id != eventRoomId:
        await ctx.send('Ezt a parancsot a pokémon event szobában használd!')
        return



    idAndCP = {}

    for p in ownedPokemons:
        if p.owner not in idAndCP.keys():
            idAndCP[p.owner] = p.cp
        else:
            idAndCP[p.owner] = idAndCP[p.owner] + p.cp

    idAndCP = {k: v for k, v in sorted(idAndCP.items(), key=lambda item: item[1], reverse=True)}

    leaderboardString = '**A játékállás:**\n'

    index = 1
    for key in idAndCP.keys():
        leaderboardString += f'{index}. {client.guilds[0].get_member(key).name} - {idAndCP[key]} CP\n'
        index += 1

    if index == 1:
        await ctx.send(leaderboardString + 'Még senki nem fogott el pokémont.')
    else:
        await ctx.send(leaderboardString)

# endregion
##############################################################################################################################################################################
# region transferAndDemand
async def changeDemand():
    global highDemandPokemons
    highDemandPokemons = []

    highDemandPokemonCount = r.randint(30, 40)
    for i in range(highDemandPokemonCount):
        correctRandom = False
        while correctRandom == False:
            randomPokemonToDemand = pokemonNames[r.randint(0, len(pokemonNames) - 1)]
            if randomPokemonToDemand not in highDemandPokemons:
                highDemandPokemons.append(randomPokemonToDemand)
                correctRandom = True

    channel = client.guilds[0].get_channel(eventRoomId)

    await channel.send('A laborban megváltoztak a kereslett pokémonok! (#pok trans/transfer)')

    await saveState()

async def listHighDemandPokemons(ctx):
    highDemandString = ''
    for name in sorted(highDemandPokemons):
        highDemandString += name + '\t'

    await ctx.send(f'**A magasan kereslett pokémonok ({len(highDemandPokemons)}) a laborban:**\n{highDemandString}')

async def transferPokemon(ctx, pokemonName, pokemonCP):
    global ownedPokemons

    if inEvent(ctx.message.author.id) == False:
        await ctx.send('Még nem veszel részt az eventen. (#pok join)')
        return

    if ctx.message.channel.id != eventRoomId:
        await ctx.send('Ezt a parancsot a pokémon event szobában használd!')
        return

    try:
        pokemonCP = int(pokemonCP)
    except ValueError:
        await ctx.send('A pokémon CP csak egy szám lehet.')
        return

    pokemonToTrans = None
    for p in ownedPokemons:
        if p.name.lower() == pokemonName.lower() and p.cp == pokemonCP and p.owner == ctx.message.author.id:
            pokemonToTrans = p
            break

    if pokemonToTrans == None:
        await ctx.send('Nincs ilyen pokémonod.')
        return

    demandMultiplier = 1
    if pokemonToTrans.name in highDemandPokemons:
        demandMultiplier = 2

    transferPayment = int(pokemonToTrans.cp * demandMultiplier / 20) + r.randint(-5, 5)
    if transferPayment < 0:
        transferPayment = 0

    ownedPokemons.remove(pokemonToTrans)
    getInv(ctx.message.author.id).pokeCoins += transferPayment

    if transferPayment == 0:
        await ctx.send('A pokémont eladományoztad a labornak. Alacsony CP miatt fizetséget nem kaptál.')
    elif demandMultiplier == 1:
        await ctx.send(f'A labor átvette a pokémonodat {transferPayment}C-ért.')
    else:
        await ctx.send(f'A labor a magas kereslet miatt {transferPayment}C-ért vette meg a pokémonodat.')

    await saveState()


# endregion
##############################################################################################################################################################################
# region saving
# save event state
async def saveState():
    with open(path + 'pokemonWilds.txt', 'w') as pokemonWilds:
        for p in wildPokemons:
            row = p.name + ' ' + str(p.cp) + ' ' + str(p.home)
            pokemonWilds.write(row + '\n')

    with open(path + 'caughtPokemons.txt', 'w') as caughtPokemons:
        for p in ownedPokemons:
            row = f'{p.name} {p.cp} {p.home} {p.owner} {p.tier} {p.hp} {p.pp}\n'
            caughtPokemons.write(row)

    with open(path + 'partTakingUsers.txt', 'w') as joinedUsers:
        for u in eventUsers:
            userState = f'{str(u.userID)} {str(u.pokeCoins)} {str(u.pokeBalls)} {str(u.incenses)} {str(u.trackers)} {str(u.potions)} {str(u.elixirs)}'
            for item in u.lastLoginDate:
                userState += ' ' + str(item)
            joinedUsers.write(userState + '\n')

    with open(path + 'pokemonFights.txt', 'w') as f:
        for fight in allFights:
            f.write(fight.getSaveString())

    with open(path + 'fightQueue.txt', 'w') as f:
        for person in waitingFighters:
            if len(person) == 0:
                f.write('-\n')
            else:
                fighterID = str(person[0])
                fighterPokemon = f'{person[1].name} {person[1].cp} {person[1].home} {person[1].owner} {person[1].tier} {person[1].hp} {person[1].pp}\n'
                f.write(fighterID + ' ' + fighterPokemon)

    # demands
    global highDemandPokemons
    global lastDemandChange

    currentDate = datetime.datetime.now().strftime("%y:%m:%d:%H:%M").split(':')
    for i in range(5):
        currentDate[i] = int(currentDate[i])

    currentDate[0] *= 60 * 24 * 30 * 365
    currentDate[1] *= 60 * 24 * 30
    currentDate[2] *= 60 * 24
    currentDate[3] *= 60

    lastDemandChangeSum = 0
    currentDateSum = 0
    for i in range(5):
        lastDemandChangeSum += lastDemandChange[i]
        currentDateSum += currentDate[i]

    if lastDemandChangeSum + 60 * 24 < currentDateSum:
        lastDemandChange = currentDate
        await changeDemand()

    with open(path + 'highDemandPokemonNames.txt', 'w') as f:
        dateString = ''
        for dateItem in lastDemandChange:
            dateString += str(dateItem) + ' '

        dateString = dateString.strip()
        f.write(dateString + '\n')

        for name in highDemandPokemons:
            f.write(name + '\n')

# endregion
##############################################################################################################################################################################
