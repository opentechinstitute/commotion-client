#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import config



def testGetAll(confType):
    checkConf = config.findConfigs("global")
    return checkConf
    
def testGetSingle(confType, name):
    checkName = config.findConfigs("global", "testme")
    return checkName

def runTests():
    #Move test conf files into data folder
    fs.move(testFiles, newTestLocation) #NOT REAL
    confTypes = ["global", "user", "extension"]
    brokenConfTypes = ["brokenString", 5, "\n", "\0", "badFormatFile", "missingNameValueJsonFile"]
    for CT in confTypes:
        assertNotFail(testGetAll(CT)) #NOT REAL
    for CT in brokenConfTypes:
        assertFailNicely(testGetAll(CT)) #NOT REAL

    correctNames = ["GlobalName01", "UserName01", "extensionName01"]
    brokeNames = ["GlobalBROKEName01", "UserBROKEName01", "extensionBROKEName01"]
    #working conf broken name
    for CT in confTypes:
        for CN in correctNames:
            assertNotFail(testGetSingle(CT, CN)) #NOT REAL
    #working name broken conf
    for CT in confTypes:
        for CN in brokenNames:
            assertNotFail(testGetSingle(CT, CN)) #NOT REAL
    #Both broken
    for CT in brokenConfTypes:
        for CN in brokenNames:
            assertNotFail(testGetSingle(CT, CN)) #NOT REAL
        
