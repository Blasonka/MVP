import random as r
from pokemon import PokemonClass

# declare fightClass
class FightClass:
    def __init__(self, p1, p1pok, p2, p2pok, turnID = None, defMultiplier = [1, 1]):
        self.players = [p1, p2]
        self.pokemons = [p1pok, p2pok]

        if turnID == None:
            self.turnID = self.players[r.randint(0, 1)]
        else:
            self.turnID = turnID

        self.tier = p1pok.tier

        self.defMultiplier = defMultiplier

        self.successfulTurn = False

    def whosTurn(self):
        return self.turnID

    def changeTurn(self):
        if self.turnID == self.players[0]:
            self.turnID = self.players[1]
        else:
            self.turnID = self.players[0]

        self.successfulTurn = True

    def checkWinner(self):
        if self.pokemons[0].hp <= 0:
            return self.players[1]
        if self.pokemons[1].hp <= 0:
            return self.players[0]
        else:
            return None

    def getUserIndex(self, idOfUser):
        if idOfUser == self.players[0]:
            return 0
        elif idOfUser == self.players[1]:
            return 1
        else:
            return None

    def getOtherUser(self, idOfUser):
        if idOfUser == self.players[0]:
            return self.players[1]
        elif idOfUser == self.players[1]:
            return self.players[0]
        else:
            return None

    def getFightState(self):
        return f'{self.pokemons[0].getInfoBrief()}\n{self.pokemons[1].getInfoBrief()}'

    def doTurn(self, userID, action):
        self.successfulTurn = False

        if userID not in self.players:
            return 'Te nem veszel részt ebben a harcban, kérlek várd meg, amíg vége lesz.'
        elif self.whosTurn() != userID and action != 'surr' and action != 'surrender':
            return 'Jelenleg nem a te köröd van.'

        userIndex = self.getUserIndex(userID)

        self.defMultiplier[userIndex] = 1

        if action == 'att' or action == 'attack':
            atckDmg = int(r.randint(int(self.pokemons[userIndex].cp / 20), int(self.pokemons[userIndex].cp / 10)) * self.defMultiplier[userIndex - 1])
            self.pokemons[userIndex - 1].hp -= atckDmg
            self.changeTurn()
            return f'{self.pokemons[userIndex].name} {str(atckDmg)} sebzést ejtett {self.pokemons[userIndex - 1].name}-n!'

        elif action == 'spec' or action == 'special':
            if self.pokemons[userIndex].pp < 5:
                return 'Nincs elég PP a támadásra!'

            self.pokemons[userIndex].pp -= 5

            atckDmg = int(r.randint(int(self.pokemons[userIndex].cp / 10), int(self.pokemons[userIndex].cp / 5)) * self.defMultiplier[userIndex - 1])

            self.pokemons[userIndex - 1].hp -= atckDmg
            self.changeTurn()
            return f'{self.pokemons[userIndex].name} {str(atckDmg)} sebzést ejtett {self.pokemons[userIndex - 1].name}-n a különleges támadásával!'

        elif action == 'def':
            self.defMultiplier[userIndex] = r.uniform(0.4, 0.6)
            self.changeTurn()
            return f'{self.pokemons[userIndex].name} védekezik! Hatékonyság: {int(100 - self.defMultiplier[userIndex] * 100)}%'

        elif action == 'heal':
            if self.pokemons[userIndex].hp == self.pokemons[userIndex].cp:
                return 'A pokémonodat nem kell gyógyítani.'

            self.pokemons[userIndex].hp = self.pokemons[userIndex].cp
            self.changeTurn()
            return f'{self.pokemons[userIndex].name} élete feltöltődött!'

        elif action == 'charge':
            if self.pokemons[userIndex].pp == self.pokemons[userIndex].tier * 5:
                return 'A pokémonod harci erejét nem kell visszatölteni.'

            self.pokemons[userIndex].pp = self.pokemons[userIndex].tier * 5
            self.changeTurn()
            return f'{self.pokemons[userIndex].name} PP-je feltöltődött!'

        elif action == 'surr' or action == 'surrender':
            self.pokemons[userIndex].hp = 0
            self.changeTurn()
            return f'{self.pokemons[userIndex].name} feladta a harcot!'

        else:
            return 'Ismeretlen akció.'

    def getSaveString(self):
        p1pok = f'{self.pokemons[0].name} {self.pokemons[0].cp} {self.pokemons[0].home} {self.pokemons[0].owner} {self.pokemons[0].tier} {self.pokemons[0].hp} {self.pokemons[0].pp}'
        p2pok = f'{self.pokemons[1].name} {self.pokemons[1].cp} {self.pokemons[1].home} {self.pokemons[1].owner} {self.pokemons[1].tier} {self.pokemons[1].hp} {self.pokemons[1].pp}'
        p1 = str(self.players[0])
        p2 = str(self.players[1])
        turnID = str(self.turnID)
        defMultiplier = f'{self.defMultiplier[0]} {self.defMultiplier[1]}'

        return f'{p1} {p1pok} {p2} {p2pok} {turnID} {defMultiplier}\n'
