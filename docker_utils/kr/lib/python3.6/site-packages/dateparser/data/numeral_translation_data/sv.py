# -*- coding: utf-8 -*-
info = {
    "%%lenient-parse": {
        "(0, 'inf')": "&[last primary ignorable ] << ' ' << ',' << '-' << '­';"
    },
    "%%ord-fem-de": {
        "0": "de;",
        "(1, 'inf')": "' =%spellout-ordinal-feminine=;"
    },
    "%%ord-fem-nde": {
        "0": "nde;",
        "(1, 'inf')": "­=%spellout-ordinal-feminine=;"
    },
    "%%ord-fem-te": {
        "0": "te;",
        "(1, 'inf')": "' =%spellout-ordinal-feminine=;"
    },
    "%%ord-fem-teer": {
        "0": "te;",
        "(1, 'inf')": "er =%spellout-ordinal-feminine=;"
    },
    "%%ord-masc-de": {
        "0": "de;",
        "(1, 'inf')": "' =%spellout-ordinal-masculine=;"
    },
    "%%ord-masc-nde": {
        "0": "nde;",
        "(1, 'inf')": "­=%spellout-ordinal-masculine=;"
    },
    "%%ord-masc-te": {
        "0": "te;",
        "(1, 'inf')": "' =%spellout-ordinal-masculine=;"
    },
    "%%ord-masc-teer": {
        "0": "te;",
        "(1, 'inf')": "er =%spellout-ordinal-masculine=;"
    },
    "%%spellout-numbering-t": {
        "1": "et;",
        "2": "två;",
        "3": "tre;",
        "4": "fyra;",
        "5": "fem;",
        "6": "sex;",
        "7": "sju;",
        "8": "åtta;",
        "9": "nio;",
        "10": "tio;",
        "11": "elva;",
        "12": "tolv;",
        "13": "tretton;",
        "14": "fjorton;",
        "15": "femton;",
        "16": "sexton;",
        "17": "sjutton;",
        "18": "arton;",
        "19": "nitton;",
        "(20, 29)": "tjugo[­>>];",
        "(30, 39)": "trettio[­>>];",
        "(40, 49)": "fyrtio[­>>];",
        "(50, 59)": "femtio[­>>];",
        "(60, 69)": "sextio[­>>];",
        "(70, 79)": "sjuttio[­>>];",
        "(80, 89)": "åttio[­>>];",
        "(90, 99)": "nittio[­>>];",
        "(100, 999)": "<%spellout-numbering<­hundra[­>>];",
        "(1000, 'inf')": "ERROR;"
    },
    "%spellout-cardinal-feminine": {
        "(0, 'inf')": "=%spellout-cardinal-reale=;"
    },
    "%spellout-cardinal-masculine": {
        "(0, 'inf')": "=%spellout-cardinal-reale=;"
    },
    "%spellout-cardinal-neuter": {
        "(0, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-cardinal-reale": {
        "0": "noll;",
        "1": "en;",
        "(2, 19)": "=%spellout-numbering=;",
        "(20, 29)": "tjugo[­>>];",
        "(30, 39)": "trettio[­>>];",
        "(40, 49)": "fyrtio[­>>];",
        "(50, 59)": "femtio[­>>];",
        "(60, 69)": "sextio[­>>];",
        "(70, 79)": "sjuttio[­>>];",
        "(80, 89)": "åttio[­>>];",
        "(90, 99)": "nittio[­>>];",
        "(100, 999)": "<%spellout-cardinal-neuter<­hundra[­>>];",
        "(1000, 1999)": "ettusen[ >>];",
        "(2000, 999999)": "<%spellout-cardinal-reale<­tusen[ >>];",
        "(1000000, 1999999)": "en miljon[ >>];",
        "(2000000, 999999999)": "<%spellout-cardinal-reale< miljoner[ >>];",
        "(1000000000, 1999999999)": "en miljard[ >>];",
        "(2000000000, 999999999999)": "<%spellout-cardinal-reale< miljarder[ >>];",
        "(1000000000000, 1999999999999)": "en biljon[ >>];",
        "(2000000000000, 999999999999999)": "<%spellout-cardinal-reale< biljoner[ >>];",
        "(1000000000000000, 1999999999999999)": "en biljard[ >>];",
        "(2000000000000000, 999999999999999999)": "<%spellout-cardinal-reale< biljarder[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering": {
        "0": "noll;",
        "1": "ett;",
        "2": "två;",
        "3": "tre;",
        "4": "fyra;",
        "5": "fem;",
        "6": "sex;",
        "7": "sju;",
        "8": "åtta;",
        "9": "nio;",
        "10": "tio;",
        "11": "elva;",
        "12": "tolv;",
        "13": "tretton;",
        "14": "fjorton;",
        "15": "femton;",
        "16": "sexton;",
        "17": "sjutton;",
        "18": "arton;",
        "19": "nitton;",
        "(20, 29)": "tjugo[­>>];",
        "(30, 39)": "trettio[­>>];",
        "(40, 49)": "fyrtio[­>>];",
        "(50, 59)": "femtio[­>>];",
        "(60, 69)": "sextio[­>>];",
        "(70, 79)": "sjuttio[­>>];",
        "(80, 89)": "åttio[­>>];",
        "(90, 99)": "nittio[­>>];",
        "(100, 999)": "<%spellout-numbering<­hundra[­>>];",
        "(1000, 999999)": "<%%spellout-numbering-t<­tusen[ >>];",
        "(1000000, 1999999)": "en miljon[ >>];",
        "(2000000, 999999999)": "<%spellout-cardinal-reale< miljoner[ >>];",
        "(1000000000, 1999999999)": "en miljard[ >>];",
        "(2000000000, 999999999999)": "<%spellout-cardinal-reale< miljarder[ >>];",
        "(1000000000000, 1999999999999)": "en biljon[ >>];",
        "(2000000000000, 999999999999999)": "<%spellout-cardinal-reale< biljoner[ >>];",
        "(1000000000000000, 1999999999999999)": "en biljard[ >>];",
        "(2000000000000000, 999999999999999999)": "<%spellout-cardinal-reale< biljarder[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering-year": {
        "(0, 9999)": "=%spellout-numbering=;",
        "(10000, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-ordinal-feminine": {
        "(0, 'inf')": "=%spellout-ordinal-neuter=;"
    },
    "%spellout-ordinal-masculine": {
        "0": "nollte;",
        "1": "förste;",
        "2": "andre;",
        "3": "tredje;",
        "4": "fjärde;",
        "5": "femte;",
        "6": "sjätte;",
        "7": "sjunde;",
        "8": "åttonde;",
        "9": "nionde;",
        "10": "tionde;",
        "11": "elfte;",
        "12": "tolfte;",
        "(13, 19)": "=%spellout-cardinal-neuter=de;",
        "(20, 29)": "tjugo>%%ord-masc-nde>;",
        "(30, 39)": "trettio>%%ord-masc-nde>;",
        "(40, 49)": "fyrtio>%%ord-masc-nde>;",
        "(50, 59)": "femtio>%%ord-masc-nde>;",
        "(60, 69)": "sextio>%%ord-masc-nde>;",
        "(70, 79)": "sjuttio>%%ord-masc-nde>;",
        "(80, 89)": "åttio>%%ord-masc-nde>;",
        "(90, 99)": "nittio>%%ord-masc-nde>;",
        "(100, 999)": "<%spellout-numbering<­hundra>%%ord-masc-de>;",
        "(1000, 999999)": "<%%spellout-numbering-t<­tusen>%%ord-masc-de>;",
        "(1000000, 1999999)": "en miljon>%%ord-masc-te>;",
        "(2000000, 999999999)": "<%spellout-cardinal-reale< miljon>%%ord-masc-teer>;",
        "(1000000000, 1999999999)": "en miljard>%%ord-masc-te>;",
        "(2000000000, 999999999999)": "<%spellout-cardinal-reale< miljard>%%ord-masc-teer>;",
        "(1000000000000, 1999999999999)": "en biljon>%%ord-masc-te>;",
        "(2000000000000, 999999999999999)": "<%spellout-cardinal-reale< biljon>%%ord-masc-teer>;",
        "(1000000000000000, 1999999999999999)": "en biljard>%%ord-masc-te>;",
        "(2000000000000000, 999999999999999999)": "<%spellout-cardinal-reale< biljard>%%ord-masc-teer>;",
        "(1000000000000000000, 'inf')": "=#,##0=':e;"
    },
    "%spellout-ordinal-neuter": {
        "0": "nollte;",
        "1": "första;",
        "2": "andra;",
        "(3, 19)": "=%spellout-ordinal-masculine=;",
        "(20, 29)": "tjugo>%%ord-fem-nde>;",
        "(30, 39)": "trettio>%%ord-fem-nde>;",
        "(40, 49)": "fyrtio>%%ord-fem-nde>;",
        "(50, 59)": "femtio>%%ord-fem-nde>;",
        "(60, 69)": "sextio>%%ord-fem-nde>;",
        "(70, 79)": "sjuttio>%%ord-fem-nde>;",
        "(80, 89)": "åttio>%%ord-fem-nde>;",
        "(90, 99)": "nittio>%%ord-fem-nde>;",
        "(100, 999)": "<%spellout-numbering<­hundra>%%ord-fem-de>;",
        "(1000, 999999)": "<%%spellout-numbering-t<­tusen>%%ord-fem-de>;",
        "(1000000, 1999999)": "en miljon>%%ord-fem-te>;",
        "(2000000, 999999999)": "<%spellout-cardinal-reale< miljon>%%ord-fem-teer>;",
        "(1000000000, 1999999999)": "en miljard>%%ord-fem-te>;",
        "(2000000000, 999999999999)": "<%spellout-cardinal-reale< miljard>%%ord-fem-teer>;",
        "(1000000000000, 1999999999999)": "en biljon>%%ord-fem-te>;",
        "(2000000000000, 999999999999999)": "<%spellout-cardinal-reale< biljon>%%ord-fem-teer>;",
        "(1000000000000000, 1999999999999999)": "en biljard>%%ord-fem-te>;",
        "(2000000000000000, 999999999999999999)": "<%spellout-cardinal-reale< biljard>%%ord-fem-teer>;",
        "(1000000000000000000, 'inf')": "=#,##0=':e;"
    },
    "%spellout-ordinal-reale": {
        "(0, 'inf')": "=%spellout-ordinal-neuter=;"
    }
}