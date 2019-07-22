#!/usr/bin/python3


# IMPORTS

import rpm
from datetime import datetime
import sys


# CLASSES

class Info:
    name = "Rpm Query"
    version = "0.1.0"
    description = (
        "Description:\n"
        "    Utility to get basic info about installed rpm packages in both human and machine readable format.\n"
    )
    usage = (
        "Usage:\n"
        "    RpmQuery.py [multiple show options] [at most one order option] [multiple misc. options]\n"
    )
    examples = (
        "Examples:\n"
        "    RpmQuery.py -sn -sv -sr\n"
        "    RpmQuery.py -sn -ss -os -c\n"
        "    RpmQuery.py -ss -st -ot -c -m\n"
    )
    options = (
        "Options:\n"
        "    -h  --help              displays this help message\n"
        "    -sn --show-name         show name in the list\n"
        "    -sv --show-version      show version in the list\n"
        "    -sr --show-release      show release in the list\n"
        "    -st --show-time         show installation time in the list\n"
        "    -ss --show-size         show size in the list\n"
        "    -on --order-by-name     order the list by name\n"
        "    -ot --order-by-time     order the list by installation time\n"
        "    -os --order-by-size     order the list by size\n"
        "    -d  --descending        sort in descending order\n"
        "    -m  --machine           show data in machine readable format\n"
        "    -c  --count             include total package count on the last line\n"
    )

class Options:
    info = False
    showName = False
    showVersion = False
    showRelease = False
    showTime = False
    showSize = False
    orderByName = False
    orderByTime = False
    orderBySize = False
    descending = False
    machine = False
    count = False
    
class Package:
    name = ""
    version = ""
    release = ""
    time = ""
    size = ""
    timeRaw = 0
    sizeRaw = 0
    
    def __init__(self, name, version, release, time, size, timeRaw, sizeRaw):
        self.name = name
        self.version = version
        self.release = release
        self.time = time
        self.size = size
        self.timeRaw = timeRaw
        self.sizeRaw = sizeRaw
    
class Padding:
    nameSize = len("NAME")
    versionSize = len("VERSION")
    releaseSize = len("RELEASE")
    timeSize = len("TIME")
    sizeSize = len("SIZE")
    
# FUNCTIONS

def printInfo():
    print(info.name + " (" + info.version + ")\n")
    print(info.description)
    print(info.usage)
    print(info.examples)
    print(info.options)
    print()
    
def addPaddingLeft(s, size):
    if len(s) < size: s = " " * (size - len(s)) + s
    return s
    
def addPaddingRight(s, size):
    if len(s) < size: s = s + " " * (size - len(s))
    return s

def reverse(s): 
    return s[::-1]

def timeToString(time):
    dateFormat = '%d. %m. %Y %H:%M:%S'
    date = datetime.fromtimestamp(time)
    return date.strftime(dateFormat)
    
def sizeToString(number):
    s = str(number)
    s = reverse(s)
    n = 3
    ch = ' '
    s = ch.join(s[i:i+n] for i in range(0, len(s), n))
    s = reverse(s)
    return s
    
# https://rpm.org/user_doc/query_format.html
    
def getName(row):
    return row[rpm.RPMTAG_NAME].decode("utf-8")
    
def getVersion(row):
    return row[rpm.RPMTAG_VERSION].decode("utf-8")
    
def getRelease(row):
    return row[rpm.RPMTAG_RELEASE].decode("utf-8")
    
def getTimeRaw(row):
    return row[rpm.RPMTAG_INSTALLTIME]
    
def getSizeRaw(row):
    return row[rpm.RPMTAG_SIZE]
    
def getTime(row):
    if options.machine == True:
        return str(getTimeRaw(row))
    else:
        return timeToString(getTimeRaw(row))
    
def getSize(row):
    if options.machine == True:
        return str(getSizeRaw(row))
    else:
        return sizeToString(getSizeRaw(row))
        
def orderPackagesByName(packages):
    packages.sort(key=lambda p: p.name, reverse = options.descending)
    
def orderPackagesByTime(packages):
    packages.sort(key=lambda p: p.timeRaw, reverse = options.descending)
    
def orderPackagesBySize(packages):
    packages.sort(key=lambda p: p.sizeRaw, reverse = options.descending)
    
def updatePadding(p):
    if options.machine: return
    if len(p.name) > padding.nameSize: padding.nameSize = len(p.name)
    if len(p.version) > padding.versionSize: padding.versionSize = len(p.version)
    if len(p.release) > padding.releaseSize: padding.releaseSize = len(p.release)
    if len(p.time) > padding.timeSize: padding.timeSize = len(p.time)
    if len(p.size) > padding.sizeSize: padding.sizeSize = len(p.size)
    
def loadPackages():
    packages = list()
    ts = rpm.TransactionSet()
    data = ts.dbMatch()
    for row in data:
        package = Package(getName(row), getVersion(row), getRelease(row), getTime(row), getSize(row), getTimeRaw(row), getSizeRaw(row))
        packages.append(package)
        updatePadding(package)
    return packages
    
def printTableHeader():
    if options.machine: return
    items = list()
    if options.showName: items.append(addPaddingRight("NAME", padding.nameSize))
    if options.showVersion: items.append(addPaddingRight("VERSION", padding.versionSize))
    if options.showRelease: items.append(addPaddingRight("RELEASE", padding.releaseSize))
    if options.showTime: items.append(addPaddingRight("TIME", padding.timeSize))
    if options.showSize: items.append(addPaddingRight("SIZE", padding.sizeSize))
    header = " | ".join(items)
    print("|-" + "-"*(len(header)) + "-|")
    print("| " + header + " |")
    print("|-" + "-"*(len(header)) + "-|")
    
def printPackage(p):
    leftBorder = ""
    rightBorder = ""
    items = list()
    if options.machine:
        if options.showName: items.append(p.name)
        if options.showVersion: items.append(p.version)
        if options.showRelease: items.append(p.release)
        if options.showTime: items.append(str(p.timeRaw))
        if options.showSize: items.append(str(p.sizeRaw))
    else:
        if options.showName: items.append(addPaddingRight(p.name, padding.nameSize))
        if options.showVersion: items.append(addPaddingRight(p.version, padding.versionSize))
        if options.showRelease: items.append(addPaddingRight(p.release, padding.releaseSize))
        if options.showTime: items.append(addPaddingRight(p.time, padding.timeSize))
        if options.showSize: items.append(addPaddingLeft(p.size, padding.sizeSize))
        leftBorder = "| "
        rightBorder = " |"
    print(leftBorder + " | ".join(items) + rightBorder)

def printPackages(packages):
    for p in packages:
        printPackage(p)
    
def printPackageCount(packages):
    if options.machine:
        print(str(len(packages)))
    else:
        print("Count: " + str(len(packages)))
    
    
# SCRIPT

info = Info()
options = Options()
padding = Padding()

for arg in sys.argv:
    if arg == "-h" or arg == "--help":
        options.info = True
    if arg == "-sn" or arg == "--show-name":
        options.showName = True
    if arg == "-sv" or arg == "--show-version":
        options.showVersion = True
    if arg == "-sr" or arg == "--show-release":
        options.showRelease = True
    if arg == "-st" or arg == "--show-time":
        options.showTime = True
    if arg == "-ss" or arg == "--show-size":
        options.showSize = True
    if arg == "-on" or arg == "--order-by-name":
        options.orderByName = True
    if arg == "-ot" or arg == "--order-by-time":
        options.orderByTime = True
    if arg == "-os" or arg == "--order-by-size":
        options.orderBySize = True
    if arg == "-d"  or arg == "--descending":
        options.descending = True
    if arg == "-m"  or arg == "--machine":
        options.machine = True
    if arg == "-c"  or arg == "--count":
        options.count = True
        
if options.info or len(sys.argv) <= 1:
    printInfo()
    sys.exit("")
        
orderOptionsCount = 0
if(options.orderByName): orderOptionsCount += 1
if(options.orderByTime): orderOptionsCount += 1
if(options.orderBySize): orderOptionsCount += 1
if orderOptionsCount > 1: raise Exception("Too many order by options.")

packages = loadPackages()
if(options.orderByName): orderPackagesByName(packages)
if(options.orderByTime): orderPackagesByTime(packages)
if(options.orderBySize): orderPackagesBySize(packages)

printTableHeader()
printPackages(packages)
printTableHeader()
if(options.count): printPackageCount(packages)
