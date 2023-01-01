import os
import os.path as path # Path checking
import dataManager as DM # File-related functions
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from tkinter import messagebox
from PIL import Image, ImageTk # Image processing
import threading # Secondary thread, for installing
import time # Secondary thread while loop

launcherActive = True
isInstalling = False
def checkInstallerState():
    global isInstalling
    global launcherState
    while launcherActive:
        if isInstalling:
            isInstalling = False
            print(launcherState)
            match (launcherState):
                case -1:
                    DM.installGame(launcherSettings["Target-Version"], False)

                case 0:
                    DM.installGame(launcherSettings["Target-Version"], True)

                case 1:
                    DM.installGame(versionList[0], True)
            updateLauncherStateAndButton()
        time.sleep(0.5)
thread = threading.Thread(target=checkInstallerState)
thread.start() # Run installer thread in the background

launcherSettings = DM.loadSettings()
versionList = DM.getVersions()

if versionList == False:
    messagebox.showerror("Cyberpunk++ Launcher", "Could not fetch version list, please make sure you are connected to the internet and wait a few minutes before trying again")
    launcherActive = False
launcherState = -2
defaultCWD = os.getcwd() # Original "Current Working Directory"

def getCurrentVersion():
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        with open(launcherSettings["Install-Location"] + "/gameVersion.txt") as currentVersionFile:
            currentVersion = currentVersionFile.readline()
            if currentVersion == "latest":
                currentVersion = versionList[1]
            return currentVersion
    else:
        return "N/A"

def getLauncherState():
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        currentVersion = getCurrentVersion()
        if launcherSettings["Target-Version"] != "latest" and launcherSettings["Target-Version"] != currentVersion:
            # Has target version and downloaded version is different from target
            return 0

        if launcherSettings["Target-Version"] == "latest" and currentVersion != versionList[1]:
            # No target version and downloaded version differs from newest release
            return 1
        return 2
    else:
        # Game not installed
        return -1

def updateLauncherStateAndButton():
    launcherState = getLauncherState()
    match launcherState:
        case -1:
            gameStateLabel.config(text="Game is not installed")
            currentVerButton.config(text="Installed version: N/A")
            mainButton.config(text="Install game", state=tk.NORMAL, command=mainButtonPressed)
        case 0:
            gameStateLabel.config(text="Target version not installed")
            currentVerButton.config(text="Installed version: " + getCurrentVersion())
            mainButton.config(text="Update game to " + launcherSettings["Target-Version"], state=tk.NORMAL, command=mainButtonPressed)

        case 1:
            gameStateLabel.config(text="New update available!")
            currentVerButton.config(text="Installed version: " + getCurrentVersion())
            mainButton.config(text="Update game", state=tk.NORMAL, command=mainButtonPressed)

        case 2:
            gameStateLabel.config(text="Game is up to date")
            currentVerButton.config(text="Installed version: " + getCurrentVersion())
            mainButton.config(text="Start game", state=tk.NORMAL, command=mainButtonPressed)

def mainButtonPressed():
    global isInstalling
    global launcherState
    launcherState = getLauncherState()
    match launcherState:
        case -1: # New installation
            mainButton.config(text="Installing", state=tk.DISABLED, command="")
            isInstalling = True
        case 0: # Change version
            mainButton.config(text="Changing to " + launcherSettings["Target-Version"], state=tk.DISABLED, command="")
            isInstalling = True
        case 1: # Update to latest
            mainButton.config(text="Updating", state=tk.DISABLED, command="")
            isInstalling = True
        case 2: # Start game
            os.chdir(launcherSettings["Install-Location"])
            os.startfile("CyberpunkPlusPlus.exe")
            os.chdir(defaultCWD)

settingsWindowOpen = False
currentPathLabel = None
def openSettingsWindow():
    global launcherSettings
    global settingsWindowOpen
    global currentPathLabel
    if settingsWindowOpen: # Do not open 2 setting windows
        return False

    # Create a PhotoImage with a transparent color
    transparent_img = tk.PhotoImage(width=1, height=1)
    transparent_img.put("#ffffff", to=(0, 0, 1, 1))
    transparent_img.transparency = 1

    settingsWindow = tk.Toplevel(window)
    settingsWindow.config(bg="black")
    settingsWindow.title("Cyberpunk++ Launcher Settings")
    settingsWindow.resizable(False, False)
    settingsWindow.geometry("474x305")
    settingsWindow.protocol("WM_DELETE_WINDOW", lambda: settingsWindowClosed(settingsWindow))

    sbackgroundImage = Image.open("src/SettingsHeader.png")
    sbackgroundImage = sbackgroundImage.resize((474,240))
    sbackgroundImage = ImageTk.PhotoImage(sbackgroundImage)
    sbackgroundFrame = tk.Label(settingsWindow, image=sbackgroundImage, borderwidth=0)
    sbackgroundFrame.img = sbackgroundImage
    sbackgroundFrame.place(x=237,y=152, anchor="center")

    titleLabel = tk.Label(settingsWindow, text="Settings", font=("Terminal",20), bg="Black", fg="White")
    titleLabel.pack()

    currentPathLabel = tk.Label(settingsWindow, text="Current installation path\n" + launcherSettings["Install-Location"], font=("Terminal",8), bg=transparent_img, fg="White")
    currentPathLabel.pack()

    changePathButton = tk.Button(settingsWindow, text="Change installation path", command=moveRequest)
    changePathButton.place(x=237,y=90, anchor="center")

    selectedVersionLabel = tk.Label(settingsWindow, text="Current target version", font=("Terminal",8), highlightbackground="transparent", fg="White")
    selectedVersionLabel.place(x=237,y=170, anchor="center")

    selectedVersion = tk.StringVar(settingsWindow, launcherSettings["Target-Version"])
    versionSelector = tk.OptionMenu(settingsWindow, selectedVersion, *versionList, command=versionChangeCallback)
    versionSelector.place(x=237,y=190, anchor="center")

    uninstallButton = tk.Button(settingsWindow, text="Uninstall game", fg="Red", command=uninstallRequest)
    uninstallButton.place(x=237,y=130, anchor="center")

    settingsWindowOpen = True
    return True

def moveRequest():
    global launcherSettings
    global currentPathLabel
    askResult = fd.askdirectory()
    if askResult != "":
        result = DM.moveGame(askResult)
        if result: # Game moved successfully, update settings and label
            launcherSettings = DM.loadSettings()
            if currentPathLabel != None:
                currentPathLabel.config(text="Current installation path\n" + launcherSettings["Install-Location"])

def versionChangeCallback(versionRequested):
    global launcherSettings
    DM.setTargetVersion(versionRequested)
    launcherSettings = DM.loadSettings()
    updateLauncherStateAndButton()

def uninstallRequest():
    result = DM.uninstallGame()
    if result:
        updateLauncherStateAndButton()

def settingsWindowClosed(settingsWindow):
    global settingsWindowOpen
    settingsWindowOpen = False
    settingsWindow.destroy()

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

settingsButton = tk.Button(mainFrame, text="Settings", command=openSettingsWindow)
settingsButton.place(x=0,y=25)

mainFrame.pack(anchor=tk.S, fill="x", expand=True)

currentVerButton = tk.Label(font=("Terminal",10), bg="Black", fg="Green")
currentVerButton.place(x=0,y=0)

updateLauncherStateAndButton()

window.geometry("474x305")
window.eval('tk::PlaceWindow . center')

if launcherActive:
    window.mainloop()
launcherActive = False # Finish background proccess