# -*- coding: utf-8 -*-
info = {
    "%%2d-year": {
        "(0, 9)": "agus =%spellout-numbering=;",
        "(10, 'inf')": "=%%spellout-numbering-no-a=;"
    },
    "%%billions": {
        "1": "billiún;",
        "(2, 10)": "=%%spellout-cardinal-prefixpart= billiún;",
        "(11, 19)": "=%%spellout-cardinal-prefixpart= billiún déag;",
        "(20, 99)": "=%%spellout-cardinal-prefixpart= billiún;",
        "(100, 'inf')": "<%%hundreds<>%%is-billions>;"
    },
    "%%hundreds": {
        "1": "céad;",
        "2": "dhá chéad;",
        "3": "trí chéad;",
        "4": "ceithre chéad;",
        "5": "cúig chéad;",
        "6": "sé chéad;",
        "7": "seacht gcéad;",
        "8": "ocht gcéad;",
        "(9, 'inf')": "naoi gcéad;"
    },
    "%%is": {
        "0": "' is;",
        "(1, 9)": ";",
        "(10, 'inf')": ">>;"
    },
    "%%is-billions": {
        "0": "' billiún;",
        "(1, 10)": "' is =%%spellout-cardinal-prefixpart= billiún;",
        "(11, 19)": "' is =%%billions=;",
        "(20, 'inf')": "=%%is= =%%billions=;"
    },
    "%%is-millions": {
        "0": "' =%%million=;",
        "(1, 10)": "' is =%%spellout-cardinal-prefixpart= =%%million=;",
        "(11, 19)": "' is =%%millions=;",
        "(20, 'inf')": "=%%is= =%%millions=;"
    },
    "%%is-number": {
        "0": "' is =%spellout-numbering=;",
        "(1, 'inf')": "' =%spellout-numbering=;"
    },
    "%%is-numberp": {
        "0": "' is =%%numberp=;",
        "(1, 'inf')": "' =%%numberp=;"
    },
    "%%is-quadrillions": {
        "0": "' quadrilliún;",
        "(1, 10)": "' is =%%spellout-cardinal-prefixpart= quadrilliún;",
        "(11, 19)": "' is =%%quadrillions=;",
        "(20, 'inf')": "=%%is= =%%quadrillions=;"
    },
    "%%is-thousands": {
        "0": "' =%%thousand=;",
        "(1, 10)": "' is =%%spellout-cardinal-prefixpart= =%%thousand=;",
        "(11, 19)": "' is =%%thousands=;",
        "(20, 'inf')": "=%%is= =%%thousands=;"
    },
    "%%is-trillions": {
        "0": "' =%%trillion=;",
        "(1, 10)": "' is =%%spellout-cardinal-prefixpart= =%%trillion=;",
        "(11, 19)": "' is =%%trillions=;",
        "(20, 'inf')": "=%%is= =%%trillions=;"
    },
    "%%lenient-parse": {
        "(0, 'inf')": "& ' ' , ',' ;"
    },
    "%%million": {
        "0": "milliún;",
        "(1, 6)": "mhilliún;",
        "(7, 10)": "milliún;",
        "(11, 'inf')": ">>;"
    },
    "%%millions": {
        "1": "milliún;",
        "(2, 99)": "=%%spellout-cardinal-prefixpart= =%%millionsp=;",
        "(100, 'inf')": "<%%hundreds<>%%is-millions>;"
    },
    "%%millionsp": {
        "(2, 10)": "=%%million=;",
        "(11, 19)": "=%%million= déag;",
        "(20, 'inf')": "=%%million=;"
    },
    "%%numberp": {
        "(0, 11)": "=%%spellout-cardinal-prefixpart=;",
        "12": "dó dhéag;",
        "(13, 19)": "=%%spellout-cardinal-prefixpart= déag;",
        "(20, 'inf')": "=%%spellout-cardinal-prefixpart=;"
    },
    "%%quadrillions": {
        "1": "quadrilliún;",
        "(2, 10)": "=%%spellout-cardinal-prefixpart= quadrilliún;",
        "(11, 19)": "=%%spellout-cardinal-prefixpart= quadrilliún déag;",
        "(20, 99)": "=%%spellout-cardinal-prefixpart= quadrilliún;",
        "(100, 'inf')": "<%%hundreds<>%%is-quadrillions>;"
    },
    "%%spellout-cardinal-prefixpart": {
        "0": "náid;",
        "1": "aon;",
        "2": "dhá;",
        "3": "trí;",
        "4": "ceithre;",
        "5": "cúig;",
        "6": "sé;",
        "7": "seacht;",
        "8": "ocht;",
        "9": "naoi;",
        "10": "deich;",
        "(11, 19)": ">>;",
        "(20, 29)": "fiche[ is >>];",
        "(30, 39)": "tríocha[ is >>];",
        "(40, 49)": "daichead[ is >>];",
        "(50, 59)": "caoga[ is >>];",
        "(60, 69)": "seasca[ is >>];",
        "(70, 79)": "seachtó[ is >>];",
        "(80, 89)": "ochtó[ is >>];",
        "(90, 99)": "nócha[ is >>];",
        "(100, 999)": "<%%hundreds<[>%%is-numberp>];",
        "(1000, 999999)": "<%%thousands<[, >%%numberp>];",
        "(1000000, 999999999)": "<%%millions<[, >%%numberp>];",
        "(1000000000, 999999999999)": "<%%billions<[, >%%numberp>];",
        "(1000000000000, 999999999999999)": "<%%trillions<[, >%%numberp>];",
        "(1000000000000000, 999999999999999999)": "<%%quadrillions<[, >%%numberp>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%%spellout-numbering-no-a": {
        "0": "náid;",
        "1": "aon;",
        "2": "dó;",
        "3": "trí;",
        "4": "ceathair;",
        "5": "cúig;",
        "6": "sé;",
        "7": "seacht;",
        "8": "ocht;",
        "9": "naoi;",
        "10": "deich;",
        "11": ">> déag;",
        "12": ">> dhéag;",
        "(13, 19)": ">> déag;",
        "(20, 'inf')": "=%spellout-numbering=;"
    },
    "%%thousand": {
        "0": "míle;",
        "(1, 6)": "mhíle;",
        "(7, 10)": "míle;",
        "(11, 'inf')": ">>;"
    },
    "%%thousandp": {
        "(2, 10)": "=%%thousand=;",
        "(11, 19)": "=%%thousand= dhéag;",
        "(20, 'inf')": "=%%thousand=;"
    },
    "%%thousands": {
        "1": "míle;",
        "(2, 99)": "=%%spellout-cardinal-prefixpart= =%%thousandp=;",
        "(100, 'inf')": "<%%hundreds<>%%is-thousands>;"
    },
    "%%trillion": {
        "0": "dtrilliún;",
        "(1, 6)": "thrilliún;",
        "(7, 10)": "dtrilliún;",
        "(11, 'inf')": ">>;"
    },
    "%%trillions": {
        "1": "thrilliún;",
        "(2, 99)": "=%%spellout-cardinal-prefixpart= =%%trillionsp=;",
        "(100, 'inf')": "<%%hundreds<>%%is-trillions>;"
    },
    "%%trillionsp": {
        "(2, 10)": "=%%trillion=;",
        "(11, 19)": "=%%trillion= déag;",
        "(20, 'inf')": "=%%trillion=;"
    },
    "%spellout-cardinal": {
        "(0, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-numbering": {
        "0": "a náid;",
        "1": "a haon;",
        "2": "a dó;",
        "3": "a trí;",
        "4": "a ceathair;",
        "5": "a cúig;",
        "6": "a sé;",
        "7": "a seacht;",
        "8": "a hocht;",
        "9": "a naoi;",
        "10": "a deich;",
        "11": ">> déag;",
        "12": ">> dhéag;",
        "(13, 19)": ">> déag;",
        "(20, 29)": "fiche[ >>];",
        "(30, 39)": "tríocha[ >>];",
        "(40, 49)": "daichead[ >>];",
        "(50, 59)": "caoga[ >>];",
        "(60, 69)": "seasca[ >>];",
        "(70, 79)": "seachtó[ >>];",
        "(80, 89)": "ochtó[ >>];",
        "(90, 99)": "nócha[ >>];",
        "(100, 999)": "<%%hundreds<[>%%is-number>];",
        "(1000, 999999)": "<%%thousands<[, >%spellout-numbering>];",
        "(1000000, 999999999)": "<%%millions<[, >%spellout-numbering>];",
        "(1000000000, 999999999999)": "<%%billions<[, >%spellout-numbering>];",
        "(1000000000000, 999999999999999)": "<%%trillions<[, >%spellout-numbering>];",
        "(1000000000000000, 999999999999999999)": "<%%quadrillions<[, >%spellout-numbering>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering-year": {
        "(0, 9999)": "=%spellout-numbering=;",
        "(10000, 'inf')": "=%spellout-numbering=;"
    }
}