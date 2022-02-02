"""
Auxiliary module for simple max-line-based log rotation
"""
import os

class Helpers:
    def loglen(self, logpath, log):
        with open(logpath + "/" + log, 'r') as logfile:
            for count, line in enumerate(logfile):
                pass # Line content is irrelevant
        return count

    def __getlastlog(self, logpath):
        loglist = os.listdir(logpath)
        loglist.sort(reverse=True)

        if len(loglist) == 1:
            return loglist[0]
        elif len(loglist) == 0:
            return False
        else:
            return loglist[1]

    def renamelatest(self, logpath, mainlog):
        last = self.__getlastlog(logpath)
        splitfile = last.split(".")
        try:
            if len(splitfile) == 3:
                lognum = int(splitfile[1]) + 1
                if os.rename(logpath + "/" + mainlog, logpath + "/" + splitfile[0] + "." + str(lognum) + "." + splitfile[2]):
                    return True
                else:
                    return False
            else:
                if os.rename(logpath + "/" + mainlog, logpath + "/" + splitfile[0] + "." + "1" + "." + splitfile[1]):
                    return True
                else:
                    return False
        except:
            return False

class LogRotate(Helpers):
    def rotate(self, logpath, mainlog, length):
        if self.loglen(logpath, mainlog) >= length:
            if self.renamelatest(logpath, mainlog):
                return True
            else:
                return False
