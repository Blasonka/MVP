import platform

# filepath
generalPath = ''

if platform.system() == 'Windows':
    generalPath = 'F:/Programming/mvp_bot/'
else:
    generalPath = '//MVP/mvp_bot/homes/mvp_bot/mvp_bot/'

# audio
audioPath = generalPath + 'audio/'
ffmExe = audioPath + 'ffmpeg/bin/ffmpeg.exe'

    # join effects
joinPath = audioPath + 'join/'

    # audio effects
effectPath = audioPath + 'effects/'

    # other effects
otherPath = audioPath + 'other/'

# saves
txtPath = generalPath + 'saves/'

    # pokemon event saves
pokemonPath = txtPath + 'pokemonevent/'
