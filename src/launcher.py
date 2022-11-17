import os.path as path
import dataManager as DM
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import subprocess

launcherSettings = DM.loadSettings()
versionList = DM.getVersions()

launcherState = -2

def getLauncherState():
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        with open(launcherSettings["Install-Location"] + "/gameVersion.txt") as currentVersionFile:
            currentVersion = currentVersionFile.readline()
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
    launcherState = getLauncherState()
    match launcherState:
        case -1:
            gameStateLabel.config(text="Game is not installed")
            mainButton.config(text="Install game", state=tk.NORMAL)
        case 0:
            gameStateLabel.config(text="Target version not installed")
            mainButton.config(text="Update game to " + launcherSettings["Target-Version"], state=tk.NORMAL)

        case 1:
            gameStateLabel.config(text="New update available!")
            mainButton.config(text="Update game", state=tk.NORMAL)

        case 2:
            gameStateLabel.config(text="Game is up to date")
            mainButton.config(text="Start game", state=tk.NORMAL)

def mainButtonPressed():
    launcherState = getLauncherState()
    match launcherState:
        case -1:
            mainButton.config(text="Installing", state=tk.DISABLED, command="")
            mainButton.pack()
            DM.installGame()
            updateLauncherStateAndButton()
        case 0:
            mainButton.config(text="Changing to " + launcherSettings["Target-Version"], state=tk.DISABLED, command="")
            mainButton.pack()
            DM.installGame(launcherSettings["Target-Version"], True)
            updateLauncherStateAndButton()

        case 1:
            mainButton.config(text="Updating", state=tk.DISABLED, command="")
            mainButton.pack()
            DM.installGame(versionList[0], True)
            updateLauncherStateAndButton()

        case 2:
            #gameProcess = subprocess.Popen(launcherSettings["Install-Location"] + "/CyberpunkPlusPlus.exe")
            pass
    pass
window = tk.Tk()
window.resizable(False, False)
window.config(bg="black")
window.title("Cyberpunk++ Launcher")

backgroundImage = Image.open("src/Header.png")
backgroundImage = backgroundImage.resize((474,240))
backgroundImage = ImageTk.PhotoImage(backgroundImage)
backgroundFrame = tk.Label(image=backgroundImage, width=474, height=240, borderwidth=0)
backgroundFrame.pack()

mainFrame = ttk.Frame(width=474, height=240,borderwidth=0)
mainFrame.pack(anchor=tk.S)

gameStateLabel = tk.Label(mainFrame,font=("Terminal",15), bg="Black", fg="Green")
mainButton = tk.Button(mainFrame,state=tk.DISABLED, command=mainButtonPressed)

updateLauncherStateAndButton()
gameStateLabel.pack()
mainButton.pack()

window.geometry("474x305")
window.eval('tk::PlaceWindow . center')

window.mainloop()