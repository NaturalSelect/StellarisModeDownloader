import subprocess
import logging

class StreamCmd:
    cmdProc:subprocess.Popen

    def __init__(self,path:str) -> None:
        self.cmdProc = subprocess.Popen(path,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        _ = self.recvAll()
        return

    def Wait(self) -> None:
        self.cmdProc.wait()

    def Close(self) -> None:
        self.cmdProc.terminate()
        self.cmdProc.wait()

    def recvAll(self) -> str:
        text:str = ""
        while self.cmdProc.stdout.readable():
            line:bytes = self.cmdProc.stdout.readline()
            r:str = line.decode()
            logging.info("[recvAll] recv line {} bytes {}".format(r,line))
            text += r
            text += "\n"
            if line.endswith(b'\x1b[1m\n'):
                break
        logging.info("[recvAll] recevive message {}".format(text))
        return text

    def writeLineToStdin(self,content:str) ->None:
        self.cmdProc.stdin.write("{}\n".format(content).encode())
        self.cmdProc.stdin.flush()

    def Login(self,name:str,passwd:str) -> bool:
        self.writeLineToStdin("login {} {}".format(name,passwd))
        ret:str = self.recvAll()
        okCnt = ret.count("OK")
        return okCnt >= 3

    def LoginAnonymous(self) -> bool:
        self.writeLineToStdin("login {}".format("anonymous"))
        ret:str = self.recvAll()
        okCnt = ret.count("OK")
        return okCnt >= 0

    def Download(self,appId:str,modId:str) -> tuple[str,bool]:
        cmdLine = "workshop_download_item {} {}".format(appId,modId)
        self.writeLineToStdin(cmdLine)
        ret:str = self.recvAll()
        resultLine = "Downloaded item {} to ".format(modId)
        pos = ret.find(resultLine)
        if pos == -1:
            return "",False
        ret = ret[pos+len(resultLine):]
        if not ret.startswith("\""):
            return "",False
        ret = ret[1:]
        pos = ret.find("\"")
        if pos == -1:
            return "",False
        ret = ret[0:pos]
        return ret,True
