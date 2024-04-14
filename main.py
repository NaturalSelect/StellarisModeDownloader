import logging
import os
from optparse import OptionParser

import steamcmd

appId:str = "281990"

def parseLogLevel(v:str)->int:
    level = logging.WARN
    levels:dict[str,int] = dict()
    levels["info"] = logging.INFO
    levels["warn"] = logging.WARNING
    levels["error"] = logging.ERROR
    for i,j in levels.items():
        if i.lower() == v:
            level = j
            break
    return level

def Main() -> None:
    parser = OptionParser()
    parser.add_option("-s","--steam",help="the path of steam cmd",dest="steamPath")
    parser.add_option("-m","--modList",help="the path of mod list",dest="modList")
    parser.add_option("-u","--user",help="steam username",dest="user",default="")
    parser.add_option("-p","--passwd",help="steam password",dest="passwd")
    parser.add_option("-l","--logLevel",help="log level",dest="logLevel",default="info")
    parser.add_option("-d","--dir",help="download dir",dest="downloadDir",default="")
    (options,args) = parser.parse_args()
    logging.basicConfig(level=parseLogLevel(options.logLevel))
    logging.info("[Main] using log level {}".format(options.logLevel))

    if options.steamPath == None:
        logging.error("[Main] please set steam cmd path")
        proc.Close()
        return

    logging.info("[Main] steam path is {}".format(options.steamPath))
    proc = steamcmd.StreamCmd(options.steamPath)

    userName = options.user
    ok = False
    if userName == "":
        userName="anonymous"
        logging.info("[Main] login user {}".format(userName))
        ok = proc.LoginAnonymous()
    else:
        logging.info("[Main] login user {}".format(userName))
        passwd = options.passwd
        if passwd == "":
            logging.error("[Main] please input passwd of {}".format(userName))
            proc.Close()
            return

    if not ok:
        logging.error("[Main] failed to login user {}".format(userName))
        proc.Close()
        return

    modList = options.modList
    if modList == None:
        logging.error("[Main] please input mod list file")
        proc.Close()
        return

    downloadDir = options.downloadDir

    mods:dict[str,str] = dict()
    file = open(modList)
    modUrl = "https://steamcommunity.com/sharedfiles/filedetails/?id="
    while file.readable():
        modId:str = file.readline().strip()
        if modId == "":
            break
        if modId.startswith(modUrl):
            modId = modId[len(modUrl):]
        if not modId.isdecimal():
            logging.error("[Main] wrong mod id {}".format(modId))
            break
        logging.info("[Main] download {}".format(modId))
        (filePath,ok) = proc.Download(appId,modId)
        if not ok:
            logging.error("[Main] failed to download {}".format(modId))
            break
        print("Download {} to {}".format(modId,filePath))
        mods[modId] = filePath
    file.close()
    proc.Close()

    if len(mods) != 0 and downloadDir != "":
        for modId,modPath in mods.items():
            placePath = os.path.join(downloadDir,modId)
            if os.access(placePath,os.F_OK):
                logging.warn("[Main] place path {} already exists, rename skip".format(placePath))
                continue
            os.rename(modPath,placePath)

if __name__ == "__main__":
    Main()