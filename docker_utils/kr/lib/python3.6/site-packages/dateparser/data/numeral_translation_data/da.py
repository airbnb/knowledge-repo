# -*- coding: utf-8 -*-
info = {
    "%%and-small": {
        "(0, 99)": "og =%spellout-cardinal-common=;",
        "(100, 'inf')": "=%spellout-cardinal-common=;"
    },
    "%%and-small-n": {
        "(0, 99)": "og =%spellout-cardinal-neuter=;",
        "(100, 'inf')": "=%spellout-cardinal-neuter=;"
    },
    "%%ord-de-c": {
        "0": "de;",
        "(1, 'inf')": "' og =%spellout-ordinal-common=;"
    },
    "%%ord-de-n": {
        "0": "de;",
        "(1, 'inf')": "' og =%spellout-ordinal-neuter=;"
    },
    "%%ord-e-c": {
        "0": "e;",
        "(1, 99)": "' og =%spellout-ordinal-common=;",
        "(100, 'inf')": "' =%spellout-ordinal-common=;"
    },
    "%%ord-e-n": {
        "0": "e;",
        "(1, 99)": "' og =%spellout-ordinal-neuter=;",
        "(100, 'inf')": "' =%spellout-ordinal-neuter=;"
    },
    "%%ord-te-c": {
        "0": "te;",
        "(1, 'inf')": "' =%spellout-ordinal-common=;"
    },
    "%%ord-te-n": {
        "0": "te;",
        "(1, 'inf')": "' =%spellout-ordinal-neuter=;"
    },
    "%%ord-teer-c": {
        "0": "te;",
        "(1, 'inf')": "er =%spellout-ordinal-common=;"
    },
    "%%ord-teer-n": {
        "0": "te;",
        "(1, 'inf')": "er =%spellout-ordinal-neuter=;"
    },
    "%spellout-cardinal-common": {
        "0": "nul;",
        "1": "en;",
        "2": "to;",
        "3": "tre;",
        "4": "fire;",
        "5": "fem;",
        "6": "seks;",
        "7": "syv;",
        "8": "otte;",
        "9": "ni;",
        "10": "ti;",
        "11": "elleve;",
        "12": "tolv;",
        "13": "tretten;",
        "14": "fjorten;",
        "15": "femten;",
        "16": "seksten;",
        "17": "sytten;",
        "18": "atten;",
        "19": "nitten;",
        "(20, 29)": "[>>­og­]tyve;",
        "(30, 39)": "[>>­og­]tredive;",
        "(40, 49)": "[>>­og­]fyrre;",
        "(50, 59)": "[>>­og­]halvtreds;",
        "(60, 69)": "[>>­og­]tres;",
        "(70, 79)": "[>>­og­]halvfjerds;",
        "(80, 89)": "[>>­og­]firs;",
        "(90, 99)": "[>>­og­]halvfems;",
        "(100, 199)": "hundrede[ og >>];",
        "(200, 999)": "<%spellout-cardinal-neuter<­hundrede[ og >>];",
        "(1000, 1999)": "tusinde[ >%%and-small>];",
        "(2000, 999999)": "<%spellout-cardinal-neuter< tusinde[ >%%and-small>];",
        "(1000000, 1999999)": "million[ >>];",
        "(2000000, 999999999)": "<< millioner[ >>];",
        "(1000000000, 1999999999)": "milliard[ >>];",
        "(2000000000, 999999999999)": "<< milliarder[ >>];",
        "(1000000000000, 1999999999999)": "billion[ >>];",
        "(2000000000000, 999999999999999)": "<< billioner[ >>];",
        "(1000000000000000, 1999999999999999)": "billiard[ >>];",
        "(2000000000000000, 999999999999999999)": "<< billiarder[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-cardinal-neuter": {
        "0": "nul;",
        "1": "et;",
        "(2, 99)": "=%spellout-cardinal-common=;",
        "(100, 199)": "hundrede[ og >>];",
        "(200, 999)": "<%spellout-cardinal-neuter<­hundrede[ og >>];",
        "(1000, 1999)": "tusind[ >%%and-small-n>];",
        "(2000, 999999)": "<%spellout-cardinal-neuter< tusind[ >%%and-small-n>];",
        "(1000000, 1999999)": "en million[ >>];",
        "(2000000, 999999999)": "<%spellout-cardinal-common< millioner[ >>];",
        "(1000000000, 1999999999)": "en milliard[ >>];",
        "(2000000000, 999999999999)": "<%spellout-cardinal-common< milliarder[ >>];",
        "(1000000000000, 1999999999999)": "en billion[ >>];",
        "(2000000000000, 999999999999999)": "<%spellout-cardinal-common< billioner[ >>];",
        "(1000000000000000, 1999999999999999)": "en billiard[ >>];",
        "(2000000000000000, 999999999999999999)": "<%spellout-cardinal-common< billiarder[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering": {
        "(0, 'inf')": "=%spellout-cardinal-common=;"
    },
    "%spellout-numbering-year": {
        "(0, 9999)": "=%spellout-numbering=;",
        "(10000, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-ordinal-common": {
        "0": "nulte;",
        "1": "første;",
        "2": "anden;",
        "3": "tredje;",
        "4": "fjerde;",
        "5": "femte;",
        "6": "sjette;",
        "7": "syvende;",
        "8": "ottende;",
        "9": "niende;",
        "10": "tiende;",
        "11": "ellevte;",
        "12": "tolvte;",
        "(13, 19)": "=%spellout-numbering=de;",
        "(20, 29)": "[>%spellout-numbering>­og­]tyvende;",
        "(30, 39)": "[>%spellout-numbering>­og­]tredivte;",
        "(40, 49)": "[>%spellout-numbering>­og­]fyrrende;",
        "(50, 99)": "=%spellout-numbering=indstyvende;",
        "(100, 199)": "hundrede>%%ord-de-c>;",
        "(200, 999)": "<%spellout-numbering< hundrede>%%ord-de-c>;",
        "(1000, 1999)": "tusind>%%ord-e-c>;",
        "(2000, 999999)": "<%spellout-numbering< tusind>%%ord-e-c>;",
        "(1000000, 1999999)": "million>%%ord-te-c>;",
        "(2000000, 999999999)": "<%spellout-numbering< million>%%ord-teer-c>;",
        "(1000000000, 1999999999)": "milliard>%%ord-te-c>;",
        "(2000000000, 999999999999)": "<%spellout-numbering< milliard>%%ord-teer-c>;",
        "(1000000000000, 1999999999999)": "billion>%%ord-te-c>;",
        "(2000000000000, 999999999999999)": "<%spellout-numbering< billion>%%ord-teer-c>;",
        "(1000000000000000, 1999999999999999)": "billiard>%%ord-te-c>;",
        "(2000000000000000, 999999999999999999)": "<%spellout-numbering< billiard>%%ord-teer-c>;",
        "(1000000000000000000, 'inf')": "=#,##0=.;"
    },
    "%spellout-ordinal-neuter": {
        "0": "nulte;",
        "1": "første;",
        "2": "andet;",
        "(3, 19)": "=%spellout-ordinal-common=;",
        "(20, 29)": "[>%spellout-cardinal-neuter>­og­]tyvende;",
        "(30, 39)": "[>%spellout-cardinal-neuter>­og­]tredivte;",
        "(40, 49)": "[>%spellout-cardinal-neuter>­og­]fyrrende;",
        "(50, 99)": "=%spellout-cardinal-neuter=indstyvende;",
        "(100, 199)": "hundrede>%%ord-de-n>;",
        "(200, 999)": "<%spellout-cardinal-neuter< hundrede>%%ord-de-n>;",
        "(1000, 1999)": "tusinde>%%ord-e-n>;",
        "(2000, 999999)": "<%spellout-cardinal-neuter< tusind>%%ord-e-n>;",
        "(1000000, 1999999)": "million>%%ord-teer-n>;",
        "(2000000, 999999999)": "<%spellout-cardinal-neuter< million>%%ord-teer-n>;",
        "(1000000000, 1999999999)": "milliard>%%ord-te-n>;",
        "(2000000000, 999999999999)": "<%spellout-cardinal-neuter< milliard>%%ord-teer-n>;",
        "(1000000000000, 1999999999999)": "billion>%%ord-te-n>;",
        "(2000000000000, 999999999999999)": "<%spellout-cardinal-neuter< billion>%%ord-teer-n>;",
        "(1000000000000000, 1999999999999999)": "billiard>%%ord-te-n>;",
        "(2000000000000000, 999999999999999999)": "<%spellout-cardinal-neuter< billiard>%%ord-teer-n>;",
        "(1000000000000000000, 'inf')": "=#,##0=.;"
    }
}