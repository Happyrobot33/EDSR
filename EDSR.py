#python program made to interact with Elite Dangerous and act as a music version of GALnet

#TODO
#Battle music using Under Attack Event
#Fuel Scooping over detection
#

#Dependencys needed:
#pygame, mutagen, pypiwin32
import os, winsound, random, wave, contextlib, time, pygame, glob, win32com.client, sys
from sty import fg, RgbFg, Style, rs, ef
from mutagen.mp3 import MP3
clear = lambda: os.system('cls')
os.system('mode con: cols=100 lines=20') #setup default window size. this also fixes the flickering issue for some users

pygame.mixer.init()

fg.orange = Style(RgbFg(255, 90, 0))
fg.yellow = Style(RgbFg(255, 204, 0))

journal_path = ''
current_user_dir = os.path.expanduser("~")
ED_Journal_Folder = 'C:\\Users\matth\Saved Games\Frontier Developments\Elite Dangerous'
songs_path = 'C:\\Users\matth\Music\wavs'
battle_songs_path = 'C:\\Users\matth\Music\wavs'
battle_songs_enabled = True
in_battle = False
docking_reminder = False
song_volume = 0.15

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Voice = speaker.GetVoices().Item(0)
speaker.Rate = 2

def readSettings():
    global ED_Journal_Folder
    global songs_path
    global song_volume
    global battle_songs_path
    global battle_songs_enabled
    global docking_reminder

    with open(os.path.join(sys.path[0], "EDSRSETTINGS.txt"), "r") as f:
        lines = f.readlines()

    ED_Journal_Folder = lines[1].rstrip("\n")
    if ED_Journal_Folder == "":
        print("Automatically finding Journal Folder....")
        ED_Journal_Folder = current_user_dir + "\\Saved Games\\Frontier Developments\\Elite Dangerous"
        print("Journal Folder Found!")
    songs_path = lines[3].rstrip("\n")
    battle_songs_path = lines[5].rstrip("\n")
    battle_songs_enabled = lines[7].rstrip("\n") == "True"
    song_volume = float(lines[9].rstrip("\n"))
    docking_reminder = lines[11].rstrip("\n") == "True"

readSettings()

def getRecentJournal():
    global journal_path
    journal_files = glob.glob(ED_Journal_Folder + "\\*.log")
    journal_path = max(journal_files, key=os.path.getmtime)
    print(journal_path)

last_event = ""
song_list = os.listdir(songs_path)
battle_song_list = os.listdir(battle_songs_path)
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
}

fade_text_notifs_list = ["NoFireZone"]

end_combat_event_list = ["StartJump","DockingGranted","DockingCancelled","Docked","Undocked","DockingDenied","JetConeBoost","DockFighter"]

start_combat_event_list = ["UnderAttack", "LaunchFighter"]

song_duration = "Null"
current_song = "Null"
song_start_time = time.time()
song_remaining = 0
previous_line = ""
voice_previous_line = ""

def playRandSong():
    #defince global variables to change outside of the function
    global song_duration
    global current_song
    global song_start_time
    prev_song = current_song

    while current_song == prev_song:
        if not in_battle:
            current_song = random.choice(song_list)
            fname = songs_path + "\\" + current_song
        else:
            current_song = random.choice(battle_song_list)
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
        input()
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

getRecentJournal()
playRandSong()
while True:
    global sound_volume

    #if the last event should deactivate battle mode
    if last_event in end_combat_event_list and in_battle == True:
        in_battle = False
        playRandSong()

    if(song_remaining < 0):
        getRecentJournal()
        playRandSong()

    prev_last_event = last_event
    with open(journal_path, 'rb') as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b'\n':
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline().decode()

    last_event = last_line[47:].split('"')[0]

    clear()
    #ASCII ART
    print(fg.orange + "  ______   _____     _____   _____  ")
    print(" |  ____| |  __ \   / ____| |  __ \    _   ____  ")
    print(" | |__    | |  | | | (___   | |__) |  / | |___ \ ")
    print(" |  __|   | |  | |  \___ \  |  _  /   | |   __) |")
    print(" | |____  | |__| |  ____) | | | \ \   | |_ / __/ ")
    print(" |______| |_____/  |_____/  |_|  \_\\  |_(_)_____|")
    print("                                               ")

    print("------Song Info------")
    print("Current Song: " + current_song.split('.')[0])
    printProgressBar(song_duration - song_remaining, song_duration)
    print()
    print("Song Volume: " + str(round(pygame.mixer.music.get_volume() * 100)) + "%")
    print("--------------------")
    print("Event: " + last_event) #If fuel scooping, every 5 units the journal gets updated. can be used to determine if finished fuelscooping if the ammount is less than 5
    pygame.mixer.music.set_volume(song_volume)

    print("------Status---------")

    #Determine if to fade music
    if last_event in fade_event_list and last_line != previous_line:
        if last_event == "ReceiveText":
            if not "NoFireZone" in last_line:
                time.sleep(.25)
                continue
        previous_line = last_line
        unfaded_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() / 2)
        print("Fading to " + str(round(pygame.mixer.music.get_volume() / 2 * 100)) + "% For " + str(fade_event_list[last_event]) + " Seconds")
        print("--------------------")
        time.sleep(fade_event_list[last_event])
        pygame.mixer.music.set_volume(unfaded_volume)
    else:
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
        playRandSong()

    time.sleep(.25)
    song_remaining = song_duration - (time.time() - song_start_time)

input() #stop the console window from closing