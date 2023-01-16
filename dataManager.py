import os
import os.path as path # Path checking
import json
import requests # Download files
import zipfile # Extract files
from tkinter import messagebox
import shutil

launcherSettings = {
    "Install-Location": "C:/Acanixz/CyberpunkPlusPlus",
    "Language": "en-us",
    "Target-Version": "latest"
}
versionList = []

def isGameClosed():
    finalState = False
    if not path.exists(launcherSettings["Install-Location"] + "/CyberpunkPlusPlus.exe"):
        return True

    try:
        file = open(launcherSettings["Install-Location"] + "/CyberpunkPlusPlus.exe", "wb")
        finalState = True
        file.close()
    except OSError:
        finalState = False
    return finalState

def loadSettings():
    if path.exists("src/settings.json"): # Load settings.json
        settingsFile = open("src/settings.json", "r")

        settingsJson = json.load(settingsFile)
        for i in settingsJson:
            launcherSettings[i] = settingsJson[i]
        settingsFile.close()

        return launcherSettings
    else: # Create new settings.json if one is not found
        settingsFile = open("src/settings.json","x")
        json.dump(launcherSettings, settingsFile)
        settingsFile.close()

        return launcherSettings

def saveSettings(): # Save launcherSettings to json file
    settingsFile = open("src/settings.json","w")
    json.dump(launcherSettings, settingsFile)
    settingsFile.close()

def getVersions():
    global versionList
    versionList = ["latest"]
    url = "https://api.github.com/repos/Acanixz/CyberpunkPlusPlus/tags"
    response = requests.get(url)
    if response.status_code == 200:
        versionListJSON = response.json()
        for i in versionListJSON:
            versionName = i["name"]
            versionList.append(versionName)
        return versionList
    else:
        print("GET VERSIONS FAILED, HTTP ERROR CODE:", response.status_code, "with the reason:", response.reason)
        return False

def setTargetVersion(version="latest"):
    launcherSettings["Target-Version"] = version
    saveSettings()

def installGame(targetInstallVersion = "latest", overwriteGame = False):

    if not isGameClosed():
        messagebox.showerror("Installation failed!", "Cyberpunk++ is open, please close the game and try again")
        return False # Cannot update game, file is open
    
    if targetInstallVersion == "latest":
        url = "https://github.com/Acanixz/CyberpunkPlusPlus/releases/latest/download/CyberpunkPlusPlus_Compiled.zip"
    else:
        url = "https://github.com/Acanixz/CyberpunkPlusPlus/releases/download/" + targetInstallVersion + "/CyberpunkPlusPlus_Compiled.zip"

    gameData = requests.get(url, stream=True)
    if gameData.status_code == 200: # Successful download
        if not path.exists(launcherSettings["Install-Location"]): # Create game directory if it does not exist
            os.makedirs(launcherSettings["Install-Location"])

        with open(launcherSettings["Install-Location"] +"/downloadedGame.zip","wb") as outputFile:
            outputFile.write(gameData.content)
        
        zippedGame = zipfile.ZipFile(launcherSettings["Install-Location"] +"/downloadedGame.zip")
        zippedGame.extractall(launcherSettings["Install-Location"])
        zippedGame.close()

        os.remove(launcherSettings["Install-Location"] +"/downloadedGame.zip")

        with open(launcherSettings["Install-Location"] + "/gameVersion.txt", "w") as versionFile:
                if launcherSettings["Target-Version"] != "latest":
                    versionFile.write(launcherSettings["Target-Version"])
                else:
                    versionFile.write(versionList[1])
        return True # Installation successful
    else:
        print("DOWNLOAD FAILED, HTTP ERROR CODE:", gameData.status_code)
        messagebox.showerror("Installation failed!", "Download request failed, HTTP error code: " + gameData.status_code)
        return False # Installation failed!

def moveGame(target="C:/Acanixz"):
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"): # Game is still there
        if not path.exists(target):
            os.makedirs(target)
        
        try:
            shutil.move(launcherSettings["Install-Location"], target)
        except (shutil.Error, PermissionError):
            messagebox.showerror("Path change failed", "Please make sure the selected path does not need admin privileges and that the game is closed")
            return False # Cannot move game, file is open
        
        launcherSettings["Install-Location"] = target + "/CyberpunkPlusPlus"
        saveSettings()
        return True
    else:
        launcherSettings["Install-Location"] = target + "/CyberpunkPlusPlus"
        saveSettings()
        return True

def uninstallGame():
    response = messagebox.askyesno("Uninstall game", "Are you sure you want to uninstall Cyberpunk++ from the current path?")
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        if response:
            try:
                shutil.rmtree(launcherSettings["Install-Location"])
            except (shutil.Error, PermissionError):
                messagebox.showerror("Uninstaller failed", "Please make sure Cyberpunk++ is closed")
                return False # Cannot uninstall game, file is open
            
            messagebox.showinfo("Game uninstalled", "Cyberpunk++ was uninstalled sucessfully")
            return True # Game uninstalled
        else:
            return False # User choice: No
    else:
        messagebox.showerror("Uninstaller failed", "Could not find the game version file inside the current path")
        return False # Game path invalid, uninstallation failed