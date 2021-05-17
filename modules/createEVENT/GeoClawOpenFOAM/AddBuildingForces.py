#!/usr/bin/env python
from __future__ import print_function
import os, sys
import argparse
import json

def validateCaseDirectoryStructure(caseDir):
    """
    This method validates that the provided case directory is valid and contains the 0, constant and system directory
    It also checks that system directory contains the controlDict
    """
    if not os.path.isdir(caseDir):
        return False
    
    caseDirList = os.listdir(caseDir)
    necessaryDirs = ["0", "constant", "system"]
    if any(not aDir in caseDirList for aDir in necessaryDirs):
        return False

    controlDictPath = os.path.join(caseDir, "system/controlDict")
    if not os.path.exists(controlDictPath):
        return False
    
    return True

def findFunctionsDictionary(controlDictLines):
    """
    This method will find functions dictionary in the controlDict 
    """
    for line in controlDictLines:
        if line.startswith("functions"):
            return (True, controlDictLines.index(line) + 2)

    return [False, len(controlDictLines)]


def writeForceDictionary(controlDictLines, lineIndex, floorsCount, patches):
    """
    This method will write the force dictionary
    """

    for line in ["\t\n", "\tbuildingsForces\n", "\t{\n", "\t}\n", "\n"]:
        controlDictLines.insert(lineIndex, line)
        lineIndex += 1

    forceDictionary = {
        "type": "forces",
        "libs": '("libforces.so")',
        "writeControl": "timeStep",
        "writeInterval": 1,
        "patches": "({})".format(patches),
        "rho": "rhoInf",
        "log": "true",
        "rhoInf": 1,
        "CofR": "(0 0 0)",
    }

    lineIndex -= 2
    for key, value in forceDictionary.items():
        controlDictLines.insert(lineIndex, "\t\t" + key + "\t" + str(value)+ ";\n")
        lineIndex += 1

    for line in ["\n", "\t\tbinData\n", "\t\t{\n", "\t\t}\n", "\n"]:
        controlDictLines.insert(lineIndex, line)
        lineIndex += 1

    lineIndex -= 2
    binDictionary = {
        "nBin": str(floorsCount),
        "direction": '(0 0 1)',
        "cumulative": "no"
    }

    for key, value in binDictionary.items():
        controlDictLines.insert(lineIndex, "\t\t\t" + key + "\t" + str(value)+ ";\n")
        lineIndex += 1

#def AddBuildingsForces(caseDir, floorsCount, patches):
def AddBuildingsForces(floorsCount, patches):
    """
    First, we need to validate the case directory structure
    """
    # if not validateCaseDirectoryStructure(caseDir):
    #     print("Invalid OpenFOAM Case Directory!")
    #     sys.exit(-1)


    #controlDictPath = os.path.join(caseDir, "system/controlDict")
    controlDictPath = "system/controlDict"
    with open(controlDictPath, 'r') as controlDict:
        controlDictLines = controlDict.readlines()

    [isFound, lineIndex] = findFunctionsDictionary(controlDictLines)

    #If we cannot find the function dictionary, we will create one
    if not isFound:
        for line in ["\n", "functions\n", "{\n", "}\n"]:
            controlDictLines.insert(lineIndex, line)
            lineIndex += 1


    #Now we can add the building forces
    writeForceDictionary(controlDictLines, lineIndex, floorsCount, patches)

    #Writing updated controlDict
    with open(controlDictPath, 'w') as controlDict:
        controlDict.writelines(controlDictLines)

def GetFloorsCount(BIMFilePath):
    with open(BIMFilePath,'r') as BIMFile:
	    bim = json.load(BIMFile)

    return int(bim["GeneralInformation"]["stories"])

if __name__ == "__main__":
    #CLI parser
    parser = argparse.ArgumentParser(description="Add forces postprocessing to OpenFOAM controlDict")
    #parser.add_argument('-c', '--case', help="OpenFOAM case directory", required=True)
    parser.add_argument('-f', '--floors', help= "Number of Floors", type=int, required=False)
    parser.add_argument('-b', '--bim', help= "path to BIM file", required=False)
    parser.add_argument('-p', '--patches', help= "Patches used for extracting forces on building", required=False)

    #Parsing arguments
    arguments, unknowns = parser.parse_known_args()
    floors = arguments.floors
    if not floors:
        floors = GetFloorsCount(arguments.bim)

    patches = arguments.patches
    if not patches:
        patches = "Building"

    #Add building forces to post-processing
    # AddBuildingsForces(arguments.case, floors, patches)
    AddBuildingsForces(floors, patches)
