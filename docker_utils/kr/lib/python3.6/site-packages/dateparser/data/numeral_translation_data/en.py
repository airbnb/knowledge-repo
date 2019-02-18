# -*- coding: utf-8 -*-
info = {
    "%%2d-year": {
        "0": "hundred;",
        "(1, 9)": "oh-=%spellout-numbering=;",
        "(10, 'inf')": "=%spellout-numbering=;"
    },
    "%%and": {
        "(1, 99)": "' and =%spellout-cardinal-verbose=;",
        "(100, 'inf')": "' =%spellout-cardinal-verbose=;"
    },
    "%%and-o": {
        "0": "th;",
        "(1, 99)": "' and =%spellout-ordinal-verbose=;",
        "(100, 'inf')": "' =%spellout-ordinal-verbose=;"
    },
    "%%commas": {
        "(1, 99)": "' and =%spellout-cardinal-verbose=;",
        "(100, 999)": ", =%spellout-cardinal-verbose=;",
        "(1000, 999999)": ", <%spellout-cardinal-verbose< thousand[>%%commas>];",
        "(1000000, 'inf')": ", =%spellout-cardinal-verbose=;"
    },
    "%%commas-o": {
        "0": "th;",
        "(1, 99)": "' and =%spellout-ordinal-verbose=;",
        "(100, 999)": ", =%spellout-ordinal-verbose=;",
        "(1000, 999999)": ", <%spellout-cardinal-verbose< thousand>%%commas-o>;",
        "(1000000, 'inf')": ", =%spellout-ordinal-verbose=;"
    },
    "%%th": {
        "0": "th;",
        "(1, 'inf')": "' =%spellout-ordinal=;"
    },
    "%%tieth": {
        "0": "tieth;",
        "(1, 'inf')": "ty-=%spellout-ordinal=;"
    },
    "%spellout-cardinal": {
        "0": "zero;",
        "1": "one;",
        "2": "two;",
        "3": "three;",
        "4": "four;",
        "5": "five;",
        "6": "six;",
        "7": "seven;",
        "8": "eight;",
        "9": "nine;",
        "10": "ten;",
        "11": "eleven;",
        "12": "twelve;",
        "13": "thirteen;",
        "14": "fourteen;",
        "15": "fifteen;",
        "16": "sixteen;",
        "17": "seventeen;",
        "18": "eighteen;",
        "19": "nineteen;",
        "(20, 29)": "twenty[->>];",
        "(30, 39)": "thirty[->>];",
        "(40, 49)": "forty[->>];",
        "(50, 59)": "fifty[->>];",
        "(60, 69)": "sixty[->>];",
        "(70, 79)": "seventy[->>];",
        "(80, 89)": "eighty[->>];",
        "(90, 99)": "ninety[->>];",
        "(100, 999)": "<< hundred[ >>];",
        "(1000, 999999)": "<< thousand[ >>];",
        "(1000000, 999999999)": "<< million[ >>];",
        "(1000000000, 999999999999)": "<< billion[ >>];",
        "(1000000000000, 999999999999999)": "<< trillion[ >>];",
        "(1000000000000000, 999999999999999999)": "<< quadrillion[ >>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-cardinal-verbose": {
        "(0, 99)": "=%spellout-numbering=;",
        "(100, 999)": "<< hundred[>%%and>];",
        "(1000, 999999)": "<< thousand[>%%and>];",
        "(1000000, 999999999)": "<< million[>%%commas>];",
        "(1000000000, 999999999999)": "<< billion[>%%commas>];",
        "(1000000000000, 999999999999999)": "<< trillion[>%%commas>];",
        "(1000000000000000, 999999999999999999)": "<< quadrillion[>%%commas>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering": {
        "(0, 'inf')": "=%spellout-cardinal=;"
    },
    "%spellout-numbering-verbose": {
        "(0, 'inf')": "=%spellout-cardinal-verbose=;"
    },
    "%spellout-numbering-year": {
        "(0, 1999)": "=%spellout-numbering=;",
        "(2000, 2999)": "=%spellout-numbering=;",
        "(3000, 3999)": "=%spellout-numbering=;",
        "(4000, 4999)": "=%spellout-numbering=;",
        "(5000, 5999)": "=%spellout-numbering=;",
        "(6000, 6999)": "=%spellout-numbering=;",
        "(7000, 7999)": "=%spellout-numbering=;",
        "(8000, 8999)": "=%spellout-numbering=;",
        "(9000, 9999)": "=%spellout-numbering=;",
        "(10000, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-ordinal": {
        "0": "zeroth;",
        "1": "first;",
        "2": "second;",
        "3": "third;",
        "4": "fourth;",
        "5": "fifth;",
        "6": "sixth;",
        "7": "seventh;",
        "8": "eighth;",
        "9": "ninth;",
        "10": "tenth;",
        "11": "eleventh;",
        "12": "twelfth;",
        "(13, 19)": "=%spellout-numbering=th;",
        "(20, 29)": "twen>%%tieth>;",
        "(30, 39)": "thir>%%tieth>;",
        "(40, 49)": "for>%%tieth>;",
        "(50, 59)": "fif>%%tieth>;",
        "(60, 69)": "six>%%tieth>;",
        "(70, 79)": "seven>%%tieth>;",
        "(80, 89)": "eigh>%%tieth>;",
        "(90, 99)": "nine>%%tieth>;",
        "(100, 999)": "<%spellout-numbering< hundred>%%th>;",
        "(1000, 999999)": "<%spellout-numbering< thousand>%%th>;",
        "(1000000, 999999999)": "<%spellout-numbering< million>%%th>;",
        "(1000000000, 999999999999)": "<%spellout-numbering< billion>%%th>;",
        "(1000000000000, 999999999999999)": "<%spellout-numbering< trillion>%%th>;",
        "(1000000000000000, 999999999999999999)": "<%spellout-numbering< quadrillion>%%th>;",
        "(1000000000000000000, 'inf')": "=#,##0=.;"
    },
    "%spellout-ordinal-verbose": {
        "(0, 99)": "=%spellout-ordinal=;",
        "(100, 999)": "<%spellout-numbering-verbose< hundred>%%and-o>;",
        "(1000, 999999)": "<%spellout-numbering-verbose< thousand>%%and-o>;",
        "(1000000, 999999999)": "<%spellout-numbering-verbose< million>%%commas-o>;",
        "(1000000000, 999999999999)": "<%spellout-numbering-verbose< billion>%%commas-o>;",
        "(1000000000000, 999999999999999)": "<%spellout-numbering-verbose< trillion>%%commas-o>;",
        "(1000000000000000, 999999999999999999)": "<%spellout-numbering-verbose< quadrillion>%%commas-o>;",
        "(1000000000000000000, 'inf')": "=#,##0=.;"
    }
}