# -*- coding: utf-8 -*-
info = {
    "%%spellout-cardinal-initial": {
        "1": "egy;",
        "2": "két;",
        "(3, 'inf')": "=%spellout-cardinal=;"
    },
    "%%spellout-ordinal-adik": {
        "0": "adik;",
        "(1, 'inf')": "=%%spellout-ordinal-larger=;"
    },
    "%%spellout-ordinal-larger": {
        "0": "edik;",
        "1": "egyedik;",
        "2": "kettedik;",
        "3": "harmadik;",
        "4": "negyedik;",
        "5": "ötödik;",
        "6": "hatodik;",
        "7": "hetedik;",
        "8": "nyolcadik;",
        "9": "kilencedik;",
        "10": "tizedik;",
        "(11, 19)": "tizen>>;",
        "20": "huszadik;",
        "(21, 29)": "huszon>>;",
        "(30, 39)": "harminc>%%spellout-ordinal-adik>;",
        "(40, 49)": "negyven>>;",
        "(50, 59)": "ötven>>;",
        "(60, 69)": "hatvan>%%spellout-ordinal-adik>;",
        "(70, 79)": "hetven>>;",
        "(80, 89)": "nyolcvan>%%spellout-ordinal-adik>;",
        "(90, 99)": "kilencven>>;",
        "(100, 199)": "száz>%%spellout-ordinal-adik>;",
        "(200, 999)": "<%%spellout-cardinal-initial<száz>%%spellout-ordinal-adik>;",
        "(1000, 1999)": "ezr>>;",
        "(2000, 999999)": "<%%spellout-cardinal-initial<ezr>>;",
        "(1000000, 999999999)": "<%%spellout-cardinal-initial< milliom>%%spellout-ordinal-odik>;",
        "(1000000000, 'inf')": "=#,##0=.;"
    },
    "%%spellout-ordinal-odik": {
        "0": "odik;",
        "(1, 'inf')": "=%%spellout-ordinal-larger=;"
    },
    "%%spellout-ordinal-verbose-adik": {
        "0": "adik;",
        "(1, 'inf')": "=%%spellout-ordinal-verbose-larger=;"
    },
    "%%spellout-ordinal-verbose-larger": {
        "(0, 99)": "=%%spellout-ordinal-larger=;",
        "(100, 999)": "<%spellout-cardinal-verbose<száz>%%spellout-ordinal-verbose-adik>;",
        "(1000, 999999)": "<%spellout-cardinal-verbose<ezr>>;",
        "(1000000, 999999999)": "<%spellout-cardinal-verbose< milliom>%%spellout-ordinal-verbose-odik>;",
        "(1000000000, 'inf')": "=#,##0=.;"
    },
    "%%spellout-ordinal-verbose-odik": {
        "0": "odik;",
        "(1, 'inf')": "=%%spellout-ordinal-verbose-larger=;"
    },
    "%spellout-cardinal": {
        "0": "nulla;",
        "1": "egy;",
        "2": "kettő;",
        "3": "három;",
        "4": "négy;",
        "5": "öt;",
        "6": "hat;",
        "7": "hét;",
        "8": "nyolc;",
        "9": "kilenc;",
        "10": "tíz;",
        "(11, 19)": "tizen­>>;",
        "20": "húsz;",
        "(21, 29)": "huszon­>>;",
        "(30, 39)": "harminc[­>>];",
        "(40, 49)": "negyven[­>>];",
        "(50, 59)": "ötven[­>>];",
        "(60, 69)": "hatvan[­>>];",
        "(70, 79)": "hetven[­>>];",
        "(80, 89)": "nyolcvan[­>>];",
        "(90, 99)": "kilencven[­>>];",
        "(100, 199)": "száz[­>>];",
        "(200, 999)": "<%%spellout-cardinal-initial<­száz[­>>];",
        "(1000, 1999)": "ezer[ >>];",
        "(2000, 999999)": "<%%spellout-cardinal-initial<­ezer[ >>];",
        "(1000000, 999999999)": "<%%spellout-cardinal-initial< millió[ >>];",
        "(1000000000, 999999999999)": "<%%spellout-cardinal-initial< milliárd[ >>];",
        "(1000000000000, 999999999999999)": "<%%spellout-cardinal-initial< billió[ >>];",
        "(1000000000000000, 999999999999999999)": "<%%spellout-cardinal-initial< billiárd[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-cardinal-verbose": {
        "(0, 99)": "=%spellout-cardinal=;",
        "(100, 999)": "<<­száz[­>>];",
        "(1000, 999999)": "<<­ezer[ >>];",
        "(1000000, 999999999)": "<< millió[ >>];",
        "(1000000000, 999999999999)": "<< milliárd[ >>];",
        "(1000000000000, 999999999999999)": "<< billió[ >>];",
        "(1000000000000000, 999999999999999999)": "<< billiárd[ >>];",
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
        "0": "nulla;",
        "1": "első;",
        "2": "második;",
        "(3, 'inf')": "=%%spellout-ordinal-larger=;"
    },
    "%spellout-ordinal-verbose": {
        "0": "nulla;",
        "1": "első;",
        "2": "második;",
        "(3, 'inf')": "=%%spellout-ordinal-verbose-larger=;"
    }
}