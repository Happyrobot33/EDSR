#python program made to interact with Elite Dangerous and act as a music version of GALnet

#TODO
#Battle music using Under Attack Event
#Fuel Scooping over detection
#

#Dependencys needed:
#pygame, mutagen, pypiwin32, sty
import os, winsound, random, wave, contextlib, time, pygame, glob, win32com.client, sys, pyfiglet, msvcrt
from sty import fg, RgbFg, Style, rs, ef
from mutagen.mp3 import MP3
clear = lambda: os.system('cls')
os.system('mode con: cols=100 lines=20') #setup default window size. this also fixes the flickering issue for some users


def getAmbientSong():
    global current_song_index
    if song_selection_method == "Shuffle":
        if current_song_index >= len(shuffled_song_list):
            current_song_index = 0

        current_song_index += 1
        return shuffled_song_list[current_song_index - 1]
    elif song_selection_method == "Random":
        return random.choice(song_list)
    elif song_selection_method == "InOrder":
        if current_song_index >= len(song_list):
            current_song_index = 0

        current_song_index += 1
        return song_list[current_song_index - 1]

def getBattleSong():
    global current_song_index_battle
    if song_selection_method == "Shuffle":
        if current_song_index_battle >= len(shuffled_battle_song_list):
            current_song_index_battle = 0

        current_song_index_battle += 1
        return shuffled_battle_song_list[current_song_index_battle - 1]
    elif song_selection_method == "Random":
        return random.choice(battle_song_list)
    elif song_selection_method == "InOrder":
        if current_song_index_battle >= len(battle_song_list):
            current_song_index_battle = 0

        current_song_index_battle += 1
        return battle_song_list[current_song_index_battle - 1]

def playSong():
    #defince global variables to change outside of the function
    global song_duration
    global current_song
    global song_start_time
    prev_song = current_song

    while current_song == prev_song:
        if not in_battle:
            current_song = getAmbientSong()
            fname = songs_path + "\\" + current_song
        else:
            current_song = getBattleSong()
            fname = battle_songs_path + "\\" + current_song


    song_start_time = time.time()
    pygame.mixer.music.load(fname)
    pygame.mixer.music.play()

    song = MP3(fname)
    song_duration = song.info.length
    song_remaining = song_duration - (time.time() - song_start_time)

def dockingReminder():
    if docking_reminder:
        unfaded_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() / 2)
        print(rs.fg + fg.yellow + "REMEMBER TO REQUEST DOCKING")
        print(fg.orange + "--------------------")
        speaker.Speak("Dont forget to request docking commander")
        pygame.mixer.music.set_volume(unfaded_volume)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 30, fill = '▪', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    percent = round(song_remaining)
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '▫' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}s {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def printUI():
    global title_fig
    global current_song
    global song_duration
    global song_remaining
    global last_event
    clear()
    print(fg.orange + title_fig.renderText('EDSR   v1.32').rsplit("\n",3)[0])

    print("------Song Info------")
    print("Current Song (" + song_selection_method + "): " + current_song.split('.mp3')[0])
    printProgressBar(song_duration - song_remaining, song_duration)
    print()
    print("Song Volume: " + str(round(pygame.mixer.music.get_volume() * 100)) + "%")
    print("--------------------")
    print("Event: " + last_event) #If fuel scooping, every 5 units the journal gets updated. can be used to determine if finished fuelscooping if the ammount is less than 5
    print("------Status---------")

def readSettings():
    global ED_Journal_Folder
    global songs_path
    global song_volume
    global battle_songs_path
    global battle_songs_enabled
    global docking_reminder
    global song_selection_method
    global next_song_keybind

    try:
        with open(os.path.join(sys.path[0], "EDSRSETTINGS.txt"), "r") as f:
            lines = f.readlines()
    except:
        print(fg.yellow + "WARNING!!!! SETTINGS FILE NOT FOUND")
        input()
        end()

    ED_Journal_Folder = lines[1].rstrip("\n")
    if ED_Journal_Folder == "":
        print("Automatically finding Journal Folder....")
        ED_Journal_Folder = current_user_dir + "\\Saved Games\\Frontier Developments\\Elite Dangerous"
        print("Journal Folder Found!")
    songs_path = lines[3].rstrip("\n")
    battle_songs_path = lines[5].rstrip("\n")
    battle_songs_enabled = lines[7].rstrip("\n") == "True"
    song_volume = float(lines[9].rstrip("\n")) / 100
    docking_reminder = lines[11].rstrip("\n") == "True"
    song_selection_method = lines[13].rstrip("\n")
    next_song_keybind = lines[15].rstrip("\n").lower()

    if not os.path.isdir(battle_songs_path):
        print(fg.yellow + "WARNING!!!! BATTLE SONGS PATH IS INCORRECT")
        input()
        end()

    if not os.path.isdir(songs_path):
        print(fg.yellow + "WARNING!!!! SONGS PATH IS INCORRECT")
        input()
        end()

def getRecentJournal():
    global journal_path
    journal_files = glob.glob(ED_Journal_Folder + "\\*.log")
    journal_path = max(journal_files, key=os.path.getmtime)

pygame.mixer.init()

#style stuff
fg.orange = Style(RgbFg(255, 90, 0))
fg.yellow = Style(RgbFg(255, 204, 0))
title_fig = pyfiglet.Figlet(font='big')

journal_path = ''
current_user_dir = os.path.expanduser("~")
ED_Journal_Folder = ''
songs_path = ''
battle_songs_path = ''
battle_songs_enabled = True
in_battle = False
docking_reminder = False
song_selection_method = "Shuffle"
song_volume = 0.15
next_song_keybind = "l"

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Voice = speaker.GetVoices().Item(0)
speaker.Rate = 2

last_event = ""
readSettings()
song_list = os.listdir(songs_path)
battle_song_list = os.listdir(battle_songs_path)
shuffled_song_list = song_list.copy()
shuffled_battle_song_list = battle_song_list.copy()
random.shuffle(shuffled_song_list)
random.shuffle(shuffled_battle_song_list)
#name is event name, key is how long song should be faded for in seconds
fade_event_list = {
  "StartJump": 6,
  "DockingGranted": 6,
  "DockingCancelled": 6,
  "Docked": 13,
  "Undocked": 10,
  "ReceiveText": 5,
  "DockingDenied": 13,
  "JetConeBoost": 3,
  "FighterDestroyed": 3
}

fade_text_notifs_list = ["NoFireZone"]

end_combat_event_list = ["StartJump","DockingGranted","DockingCancelled","Docked","Undocked","DockingDenied","JetConeBoost","DockFighter"]

start_combat_event_list = ["UnderAttack", "LaunchFighter"]

song_duration = "Null"
current_song = "Null"
current_song_index = 0 #if using song mode other than random
current_song_index_battle = 0 #if using song mode other than random
song_start_time = time.time()
song_remaining = 0
previous_line = ""
voice_previous_line = ""

getRecentJournal()
playSong()
execution_count = 0
print_on_count = 4
while True:
    global sound_volume
    execution_count += 1

    #if the last event should deactivate battle mode
    if last_event in end_combat_event_list and in_battle == True:
        in_battle = False
        playSong()

    if(song_remaining < 0):
        getRecentJournal()
        playSong()


    if msvcrt.kbhit():
        if str(msvcrt.getch())[2:3] == next_song_keybind:
            getRecentJournal()
            playSong()

    prev_last_event = last_event
    with open(journal_path, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline().decode()

    last_event = last_line[47:].split('"')[0]

    if execution_count >= print_on_count:
        printUI()

    pygame.mixer.music.set_volume(song_volume)

    #Determine if to fade music
    if last_event in fade_event_list and last_line != previous_line:
        if last_event == "ReceiveText":
            if execution_count >= print_on_count:
                print("Running Normally")
                print("--------------------")
            if not "NoFireZone" in last_line:
                continue
        previous_line = last_line
        unfaded_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() / float(2.0))
        printUI()
        print("Fading to " + str(round((pygame.mixer.music.get_volume() * float(100.0)), 1)) + "% For " + str(fade_event_list[last_event]) + " Seconds")
        print("--------------------")
        time.sleep(fade_event_list[last_event])
        pygame.mixer.music.set_volume(unfaded_volume)
    elif execution_count >= print_on_count:
        if not in_battle:
            print("Running Normally")
        else:
            print("BATTLE MODE")
        print("--------------------")

    if "NoFireZone_entered" in last_line and last_line != voice_previous_line:
        voice_previous_line = last_line
        dockingReminder()

    #if the last event should trigger battle mode
    if last_event in start_combat_event_list and in_battle == False and battle_songs_enabled:
        in_battle = True
        playSong()

    time.sleep(.0625)
    song_remaining = song_duration - (time.time() - song_start_time)

    if execution_count >= print_on_count:
        execution_count = 0

input() #stop the console window from closing