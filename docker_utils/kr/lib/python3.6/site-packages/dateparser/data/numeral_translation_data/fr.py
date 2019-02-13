# -*- coding: utf-8 -*-
info = {
    "%%cents-f": {
        "0": "s;",
        "(1, 'inf')": "' =%spellout-cardinal-feminine=;"
    },
    "%%cents-m": {
        "0": "s;",
        "(1, 'inf')": "' =%spellout-cardinal-masculine=;"
    },
    "%%cents-o": {
        "0": "ième;",
        "1": "-=%%et-unieme=;",
        "(2, 10)": "' =%%spellout-ordinal=;",
        "11": "-et-onzième;",
        "(12, 'inf')": "' =%%spellout-ordinal=;"
    },
    "%%et-un": {
        "1": "et-un;",
        "(2, 10)": "=%spellout-cardinal-masculine=;",
        "11": "et-onze;",
        "(12, 'inf')": "=%spellout-cardinal-masculine=;"
    },
    "%%et-une": {
        "1": "et-une;",
        "(2, 10)": "=%spellout-cardinal-feminine=;",
        "11": "et-onze;",
        "(12, 'inf')": "=%spellout-cardinal-feminine=;"
    },
    "%%et-unieme": {
        "1": "et-unième;",
        "(2, 10)": "=%%spellout-ordinal=;",
        "11": "et-onzième;",
        "(12, 'inf')": "=%%spellout-ordinal=;"
    },
    "%%lenient-parse": {
        "(0, 'inf')": "&[last primary ignorable ] << ' ' << ',' << '-' << '­';"
    },
    "%%mille-o": {
        "0": "ième;",
        "1": "e-=%%et-unieme=;",
        "(2, 10)": "e =%%spellout-ordinal=;",
        "11": "e-et-onzième;",
        "(12, 'inf')": "e =%%spellout-ordinal=;"
    },
    "%%spellout-leading": {
        "(0, 99)": "=%spellout-cardinal-masculine=;",
        "(100, 199)": "cent[ >>];",
        "(200, 999)": "<< cent[ >>];",
        "(1000, 'inf')": "=%spellout-cardinal-masculine=;"
    },
    "%%spellout-ordinal": {
        "1": "unième;",
        "2": "deuxième;",
        "3": "troisième;",
        "4": "quatrième;",
        "5": "cinquième;",
        "6": "sixième;",
        "7": "septième;",
        "8": "huitième;",
        "9": "neuvième;",
        "10": "dixième;",
        "11": "onzième;",
        "12": "douzième;",
        "13": "treizième;",
        "14": "quatorzième;",
        "15": "quinzième;",
        "16": "seizième;",
        "(17, 19)": "dix->>;",
        "20": "vingtième;",
        "(21, 29)": "vingt->%%et-unieme>;",
        "30": "trentième;",
        "(31, 39)": "trente->%%et-unieme>;",
        "40": "quarantième;",
        "(41, 49)": "quarante->%%et-unieme>;",
        "50": "cinquantième;",
        "(51, 59)": "cinquante->%%et-unieme>;",
        "(60, 99)": "soixantième;",
        "(100, 199)": "cent>%%cents-o>;",
        "(200, 999)": "<%spellout-cardinal-masculine< cent>%%cents-o>;",
        "(1000, 1999)": "mill>%%mille-o>;",
        "(2000, 999999)": "<%%spellout-leading< mill>%%mille-o>;",
        "(1000000, 999999999)": "<%%spellout-leading< million>%%cents-o>;",
        "(1000000000, 999999999999)": "<%%spellout-leading< milliard>%%cents-o>;",
        "(1000000000000, 999999999999999)": "<%%spellout-leading< billion>%%cents-o>;",
        "(1000000000000000, 999999999999999999)": "<%%spellout-leading< billiard>%%cents-o>;",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%%subcents-f": {
        "0": "s;",
        "(1, 'inf')": "-=%spellout-cardinal-feminine=;"
    },
    "%%subcents-m": {
        "0": "s;",
        "(1, 'inf')": "-=%spellout-cardinal-masculine=;"
    },
    "%%subcents-o": {
        "0": "ième;",
        "1": "-=%%et-unieme=;",
        "(2, 10)": "-=%%spellout-ordinal=;",
        "11": "-et-onzième;",
        "(12, 'inf')": "-=%%spellout-ordinal=;"
    },
    "%spellout-cardinal-feminine": {
        "0": "zéro;",
        "1": "une;",
        "(2, 19)": "=%spellout-cardinal-masculine=;",
        "(20, 29)": "vingt[->%%et-une>];",
        "(30, 39)": "trente[->%%et-une>];",
        "(40, 49)": "quarante[->%%et-une>];",
        "(50, 99)": "cinquante[->%%et-une>];",
        "(100, 199)": "cent[ >>];",
        "(200, 999)": "<%spellout-cardinal-masculine< cent>%%cents-f>;",
        "(1000, 1999)": "mille[ >>];",
        "(2000, 999999)": "<%%spellout-leading< mille[ >>];",
        "(1000000, 1999999)": "un million[ >>];",
        "(2000000, 999999999)": "<%%spellout-leading< millions[ >>];",
        "(1000000000, 1999999999)": "un milliard[ >>];",
        "(2000000000, 999999999999)": "<%%spellout-leading< milliards[ >>];",
        "(1000000000000, 1999999999999)": "un billion[ >>];",
        "(2000000000000, 999999999999999)": "<%%spellout-leading< billions[ >>];",
        "(1000000000000000, 1999999999999999)": "un billiard[ >>];",
        "(2000000000000000, 999999999999999999)": "<%%spellout-leading< billiards[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-cardinal-masculine": {
        "0": "zéro;",
        "1": "un;",
        "2": "deux;",
        "3": "trois;",
        "4": "quatre;",
        "5": "cinq;",
        "6": "six;",
        "7": "sept;",
        "8": "huit;",
        "9": "neuf;",
        "10": "dix;",
        "11": "onze;",
        "12": "douze;",
        "13": "treize;",
        "14": "quatorze;",
        "15": "quinze;",
        "16": "seize;",
        "(17, 19)": "dix->>;",
        "(20, 29)": "vingt[->%%et-un>];",
        "(30, 39)": "trente[->%%et-un>];",
        "(40, 49)": "quarante[->%%et-un>];",
        "(50, 99)": "cinquante[->%%et-un>];",
        "(100, 199)": "cent[ >>];",
        "(200, 999)": "<< cent>%%cents-m>;",
        "(1000, 1999)": "mille[ >>];",
        "(2000, 999999)": "<%%spellout-leading< mille[ >>];",
        "(1000000, 1999999)": "un million[ >>];",
        "(2000000, 999999999)": "<%%spellout-leading< millions[ >>];",
        "(1000000000, 1999999999)": "un milliard[ >>];",
        "(2000000000, 999999999999)": "<%%spellout-leading< milliards[ >>];",
        "(1000000000000, 1999999999999)": "un billion[ >>];",
        "(2000000000000, 999999999999999)": "<%%spellout-leading< billions[ >>];",
        "(1000000000000000, 1999999999999999)": "un billiard[ >>];",
        "(2000000000000000, 999999999999999999)": "<%%spellout-leading< billiards[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering": {
        "(0, 'inf')": "=%spellout-cardinal-masculine=;"
    },
    "%spellout-numbering-year": {
        "(0, 9999)": "=%spellout-numbering=;",
        "(10000, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-ordinal-feminine": {
        "0": "zéroième;",
        "1": "première;",
        "(2, 'inf')": "=%%spellout-ordinal=;"
    },
    "%spellout-ordinal-feminine-plural": {
        "(0, 'inf')": "=%spellout-ordinal-feminine=s;"
    },
    "%spellout-ordinal-masculine": {
        "0": "zéroième;",
        "1": "premier;",
        "(2, 'inf')": "=%%spellout-ordinal=;"
    },
    "%spellout-ordinal-masculine-plural": {
        "(0, 'inf')": "=%spellout-ordinal-masculine=s;"
    }
}