import os
import os.path as path
import json
import requests
import zipfile
import tkinter as tk
import shutil

# TO-DO: SAVE LAUNCHER SETTINGS TO FILE

launcherSettings = {
    "Install-Location": "C:/Acanixz/CyberpunkPlusPlus",
    "Language": "en-us",
    "Target-Version": "latest"
}
versionList = []

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

def getVersions():
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

def installGame(targetInstallVersion = "latest", overwriteGame = False, mainButton = None, installText = "Installing.."):

    if mainButton != None:
        mainButton.config(text=installText, state=tk.DISABLED, command="")
    
    if targetInstallVersion == "latest":
        url = "https://github.com/Acanixz/CyberpunkPlusPlus/releases/latest/download/CyberpunkPlusPlus_Compiled.zip"
    else:
        url = "https://github.com/Acanixz/CyberpunkPlusPlus/releases/download/" + targetInstallVersion + "/CyberpunkPlusPlus_Compiled.zip"

    gameData = requests.get(url, stream=True)
    if gameData.status_code == 200: # Successful download
        if mainButton != None:
            mainButton.config(text="Downloading")
        if not path.exists(launcherSettings["Install-Location"]): # Create game directory if it does not exist
            os.makedirs(launcherSettings["Install-Location"])

        with open(launcherSettings["Install-Location"] +"/downloadedGame.zip","wb") as outputFile:
            outputFile.write(gameData.content)

        if mainButton != None:
            mainButton.config(text="Extracting")
        zippedGame = zipfile.ZipFile(launcherSettings["Install-Location"] +"/downloadedGame.zip")
        zippedGame.extractall(launcherSettings["Install-Location"])
        zippedGame.close()

        os.remove(launcherSettings["Install-Location"] +"/downloadedGame.zip")

        with open(launcherSettings["Install-Location"] + "/gameVersion.txt", "w") as versionFile:
                if launcherSettings["Target-Version"] != "latest":
                    versionFile.write(launcherSettings["Target-Version"])
                else:
                    versionFile.write(versionList[0])
        return True # Installation successful
    else:
        print("DOWNLOAD FAILED, HTTP ERROR CODE:", gameData.status_code)
        print(url)
        return False # Installation failed!

def moveGame(target="C:/Acanixz"):
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"): # Game is still there
        if not path.exists(target):
            os.makedirs(target)
        shutil.move(launcherSettings["Install-Location"], target)
        launcherSettings["Install-Location"] = target + "/CyberpunkPlusPlus"
    pass

def uninstallGame():
    if path.exists(launcherSettings["Install-Location"] + "/gameVersion.txt"):
        shutil.rmtree(launcherSettings["Install-Location"])