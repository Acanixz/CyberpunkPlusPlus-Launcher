import os
import os.path as path
import dataManager as DM
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import asyncio
import threading
import time

launcherActive = True
isInstalling = False
def checkInstallerState():
    global isInstalling
    while launcherActive:
        if isInstalling:
            isInstalling = False
            match (launcherState):
                case -1:
                    DM.installGame("latest", False)

                case 0:
                    DM.installGame(launcherSettings["Target-Version"], True)

                case 1:
                    DM.installGame(versionList[0], True)
            DM.installGame("latest", False)
            updateLauncherStateAndButton()
        time.sleep(0.5)
thread = threading.Thread(target=checkInstallerState)
thread.start()

launcherSettings = DM.loadSettings()
versionList = DM.getVersions()
launcherState = -2
defaultCWD = os.getcwd()
installerLoop = asyncio.new_event_loop()

def getCurrentVersion():
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        with open(launcherSettings["Install-Location"] + "/gameVersion.txt") as currentVersionFile:
            currentVersion = currentVersionFile.readline()
            return currentVersion
    else:
        return "N/A"

def getLauncherState():
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        currentVersion = getCurrentVersion()
        if launcherSettings["Target-Version"] != "latest" and launcherSettings["Target-Version"] != currentVersion:
              # Has target version and downloaded version is different from target
           #DM.installGame(launcherSettings["Target-Version"], True)
            return 0

        if launcherSettings["Target-Version"] == "latest" and currentVersion != versionList[0]:
            # No target version and downloaded version differs from newest release
            #DM.installGame(versionList[0], True)
            return 1
        return 2
    else:
        #DM.installGame()
        return -1

def updateLauncherStateAndButton():
    isInstalling = False
    launcherState = getLauncherState()
    match launcherState:
        case -1:
            gameStateLabel.config(text="Game is not installed")
            currentVerButton.config(text="Installed version: N/A")
            mainButton.config(text="Install game", state=tk.NORMAL)
        case 0:
            gameStateLabel.config(text="Target version not installed")
            currentVerButton.config(text="Installed version: " + getCurrentVersion())
            mainButton.config(text="Update game to " + launcherSettings["Target-Version"], state=tk.NORMAL)

        case 1:
            gameStateLabel.config(text="New update available!")
            currentVerButton.config(text="Installed version: " + getCurrentVersion())
            mainButton.config(text="Update game", state=tk.NORMAL)

        case 2:
            gameStateLabel.config(text="Game is up to date")
            currentVerButton.config(text="Installed version: " + getCurrentVersion())
            mainButton.config(text="Start game", state=tk.NORMAL, command=mainButtonPressed)

def mainButtonPressed():
    global isInstalling
    launcherState = getLauncherState()
    match launcherState:
        case -1:
            mainButton.config(text="Installing", state=tk.DISABLED, command="")
            isInstalling = True
            #DM.installGame("latest", False, mainButton)
        case 0:
            mainButton.config(text="Changing to " + launcherSettings["Target-Version"], state=tk.DISABLED, command="")
            isInstalling = True
            #DM.installGame(launcherSettings["Target-Version"], True)
        case 1:
            mainButton.config(text="Updating", state=tk.DISABLED, command="")
            isInstalling = True
            #DM.installGame(versionList[0], True)
        case 2:
            os.chdir(launcherSettings["Install-Location"])
            os.startfile("CyberpunkPlusPlus.exe")
            os.chdir(defaultCWD)
            #window.quit()

window = tk.Tk()
window.resizable(False, False)
window.config(bg="black")
window.title("Cyberpunk++ Launcher")

backgroundImage = Image.open("src/Header.png")
backgroundImage = backgroundImage.resize((474,240))
backgroundImage = ImageTk.PhotoImage(backgroundImage)
backgroundFrame = tk.Label(image=backgroundImage, width=474, height=240, borderwidth=0)
backgroundFrame.pack()

mainFrame = tk.Frame(width=474, height=240,borderwidth=0, bg="Black")

gameStateLabel = tk.Label(mainFrame,font=("Terminal",15), bg="Black", fg="Green", height=1)
mainButton = tk.Button(mainFrame,state=tk.DISABLED, command=mainButtonPressed)

gameStateLabel.pack()
mainButton.pack()

settingsButton = tk.Button(mainFrame, text="Settings")
settingsButton.place(x=0,y=25)

mainFrame.pack(anchor=tk.S, fill="x", expand=True)

currentVerButton = tk.Label(font=("Terminal",10), bg="Black", fg="Green")
currentVerButton.place(x=0,y=0)

updateLauncherStateAndButton()

window.geometry("474x305")
window.eval('tk::PlaceWindow . center')

window.mainloop()
launcherActive = False