# -*- coding: utf-8 -*-
info = {
    "%%2d-year": {
        "0": "honderd[ >%spellout-numbering>];",
        "(1, 9)": "nul =%spellout-numbering=;",
        "(10, 'inf')": "=%spellout-numbering=;"
    },
    "%%ord-ste": {
        "0": "ste;",
        "1": "' en =%spellout-ordinal=;",
        "(2, 'inf')": "' =%spellout-ordinal=;"
    },
    "%spellout-cardinal": {
        "0": "nul;",
        "1": "een;",
        "2": "twee;",
        "3": "drie;",
        "4": "vier;",
        "5": "vyf;",
        "6": "ses;",
        "7": "sewe;",
        "8": "agt;",
        "9": "nege;",
        "10": "tien;",
        "11": "elf;",
        "12": "twaalf;",
        "13": "dertien;",
        "14": "veertien;",
        "15": "vyftien;",
        "16": "sestien;",
        "17": "sewentien;",
        "18": "agttien;",
        "19": "negentien;",
        "(20, 29)": "[>>-en-]twintig;",
        "(30, 39)": "[>>-en-]dertig;",
        "(40, 49)": "[>>-en-]veertig;",
        "(50, 59)": "[>>-en-]vyftig;",
        "(60, 69)": "[>>-en-]sestig;",
        "(70, 79)": "[>>-en-]sewentig;",
        "(80, 89)": "[>>-en-]tagtig;",
        "(90, 99)": "[>>-en-]negentig;",
        "(100, 199)": "honderd[ >>];",
        "(200, 999)": "<<honderd[ >>];",
        "(1000, 1999)": "duisend[ >>];",
        "(2000, 999999)": "<<­duisend[ >>];",
        "(1000000, 999999999)": "<< miljoen[ >>];",
        "(1000000000, 999999999999)": "<< miljard[ >>];",
        "(1000000000000, 999999999999999)": "<< biljoen[ >>];",
        "(1000000000000000, 999999999999999999)": "<< biljard[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering": {
        "(0, 'inf')": "=%spellout-cardinal=;"
    },
    "%spellout-numbering-year": {
        "(0, 9999)": "=%spellout-numbering=;",
        "(10000, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-ordinal": {
        "0": "nulste;",
        "1": "eerste;",
        "2": "tweede;",
        "3": "derde;",
        "(4, 19)": "=%spellout-numbering=de;",
        "(20, 101)": "=%spellout-numbering=ste;",
        "(102, 999)": "<%spellout-numbering< honderd>%%ord-ste>;",
        "(1000, 999999)": "<%spellout-numbering< duisend>%%ord-ste>;",
        "(1000000, 999999999)": "<%spellout-numbering< miljoen>%%ord-ste>;",
        "(1000000000, 999999999999)": "<%spellout-numbering< miljard>%%ord-ste>;",
        "(1000000000000, 999999999999999)": "<%spellout-numbering< biljoen>%%ord-ste>;",
        "(1000000000000000, 999999999999999999)": "<%spellout-numbering< biljard>%%ord-ste>;",
        "(1000000000000000000, 'inf')": "=#,##0=.;"
    }
}