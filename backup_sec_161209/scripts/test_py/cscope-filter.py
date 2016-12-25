import os
import os.path
import sys
import getopt

dic = {"1":"1"}
findDic = {"1":"1"}
OBJ_DIR = "."
SRC_DIR = "."
def addTargetPath(targetFile):
    if targetFile in findDic :
        return
    findDic[targetFile] = "1"
    return

def findTargetPath():
#    for (path, dir, files) in os.walk(SRC_DIR):
    for (path, dir, files) in os.walk(os.getcwd()):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.h':
                if filename in findDic:
                    #print(path +"/" + filename)
                    print("%%" + path +"/" + filename)
                    del findDic[filename]
    return

# def getRootSrc():


# MAIN
opts, args = getopt.getopt(sys.argv[1:], 'o:s:z')

for opt, arg in opts:
    if opt == '-o':
        OBJ_DIR = arg
    elif opt == '-s':
        SRC_DIR = arg

for (path, dir, files) in os.walk(OBJ_DIR):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        # find o file
        if ext == '.o':
            #change ext .o -> .c
            cfile = path + "/" + filename[0:-1]+"c"

            # file exist check
            if os.path.isfile(cfile):
               print(cfile)
               f = open(cfile)
               line = f.readline()
               while line:
                   # remove white space
                   line = line.strip()
                   if not line.startswith("#include"):
                       line = f.readline()
                       continue

                   # print line
                   findDQIdx = line.find("\"")
                   # #include "  current dir header file
                   if findDQIdx != -1:
                       findDQIdx2 = line.find("\"",findDQIdx+1)
                       newPath = path + "/" + line[findDQIdx+1:findDQIdx2]
                       #newPath = SRC_DIR + "/" + relativePath +"/"+line[findDQIdx+1:findDQIdx2]
                       #newPath = newPath.replace(".//","./")
                       if newPath in dic :
                           a = 1
                       elif os.path.isfile(newPath):
                           dic[newPath] = "1"
                           print("##" + newPath)
                       else:
                           #TODO recude this path
                           addTargetPath(os.path.basename(newPath))
                   else:
                       findLTIdx = line.find("<")
                       # #include <  kernel header file
                       if findLTIdx != -1:
                           findGTIdx = line.find(">",findLTIdx+1)
                           # TODO special directory : asm -> asm-generic
                           # newPath = SRC_DIR + "/include/" + line[findLTIdx+1:findGTIdx]
                           newPath = os.getcwd() + "/include/" + line[findLTIdx+1:findGTIdx]
                           print(newPath)
                           if newPath in dic:
                               a = 1
                           elif os.path.isfile(newPath):
                               dic[newPath] = "1"
                               print("@@" + newPath)
                           else:
                               #TODO recude this path
                               addTargetPath(os.path.basename(newPath))
                   line = f.readline()
               f.close()
findTargetPath()
