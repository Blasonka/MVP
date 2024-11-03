# declare inventory class
class PokemonInventory:
    def __init__(self, userID, pokeCoins=0, pokeBalls=0, incenses=0, trackers=0, potions=0, elixirs=0, lastLoginDate=list()):
        self.userID = userID
        self.pokeCoins = pokeCoins
        self.pokeBalls = pokeBalls
        self.incenses = incenses
        self.trackers = trackers
        self.potions = potions
        self.elixirs = elixirs
        self.lastLoginDate = lastLoginDate

    def listItems(self):
        return f'```Eszköztárad tartalma:\nPokéCoin-ok: {self.pokeCoins}C\nPokéBall-ok: {self.pokeBalls}\nIncense-ek: {self.incenses}\nTracker-ek: {self.trackers}\nPotion-ök: {self.potions}\nElixir-ek: {self.elixirs}\n\nUtolsó bejelentkezésed dátuma: {self.lastLoginString()}```'

    def canLogin(self, date):
        lastLoginSum = self.lastLoginDate[0] * 365 * 24 * 60 + self.lastLoginDate[1] * 30 * 24 * 60 + self.lastLoginDate[2] * 24 * 60 + self.lastLoginDate[3] * 60 + self.lastLoginDate[4]
        loginSum = int(date[0]) * 365 * 24 * 60 + int(date[1]) * 30 * 24 * 60 + int(date[2]) * 24 * 60 + int(date[3]) * 60 + int(date[4])

        if lastLoginSum + 24 * 60 < loginSum:
            return True
        else:
            return False

    def lastLoginString(self):
        loginDate = '20'
        for i in range(3):
            loginDate += str(self.lastLoginDate[i]) + '.'
        loginDate += ' ' + str(self.lastLoginDate[3]) + ':' + str(self.lastLoginDate[4])

        return loginDate
