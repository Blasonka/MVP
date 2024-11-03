# declare pokemon class
class PokemonClass:
    def __init__(self, name, cp, home, owner=None, tier=0, hp=None, pp=None):
        self.name = name
        self.cp = int(cp)
        self.home = int(home)
        self.owner = owner

        if self.cp <= 1000:
            self.tier = 1
        elif self.cp <= 2000:
            self.tier = 2
        elif self.cp <= 3000:
            self.tier = 3
        else:
            self.tier = 4

        if hp == None:
            self.hp = self.cp
        else:
            self.hp = hp

        if pp == None:
            self.pp = self.tier * 5
        else:
            self.pp = pp

    def compareValues(self, name, cp, home):
        if self.name is not name:
            return False
        if self.cp is not cp:
            return False
        if self.home is not home:
            return False

        return True

    def getIdentity(self):
        return self.name + ' CP: ' + str(self.cp) + ' Home: ' + str(self.home)

    identity = property(getIdentity)

    def getInfo(self):
        return f'{self.name} - CP: {self.cp} HP: {self.hp} PP: {self.pp} Szint: {self.tier}'

    def getInfoTag(self):
        return f'{self.name}\tCP: {self.cp}\tHP: {self.hp}\tPP: {self.pp}\tSzint: {self.tier}\t({self.tier} {self.name.strip()} {self.cp})'

    def getInfoBrief(self):
        return f'{self.name} - HP: {self.hp} PP: {self.pp}'
