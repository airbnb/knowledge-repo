# -*- coding: utf-8 -*-
info = {
    "%%after-hundred": {
        "(0, 9)": "lẻ =%spellout-cardinal=;",
        "(10, 'inf')": "=%spellout-cardinal=;"
    },
    "%%after-thousand-or-more": {
        "(0, 99)": "không trăm =%%after-hundred=;",
        "(100, 'inf')": "=%spellout-cardinal=;"
    },
    "%%teen": {
        "(0, 4)": "=%spellout-cardinal=;",
        "5": "lăm;",
        "(6, 'inf')": "=%spellout-cardinal=;"
    },
    "%%x-ty": {
        "0": "=%spellout-cardinal=;",
        "1": "mốt;",
        "(2, 3)": "=%%teen=;",
        "4": "tư;",
        "(5, 'inf')": "=%%teen=;"
    },
    "%spellout-cardinal": {
        "0": "không;",
        "1": "một;",
        "2": "hai;",
        "3": "ba;",
        "4": "bốn;",
        "5": "năm;",
        "6": "sáu;",
        "7": "bảy;",
        "8": "tám;",
        "9": "chín;",
        "(10, 19)": "mười[ >%%teen>];",
        "(20, 99)": "<< mươi[ >%%x-ty>];",
        "(100, 999)": "<< trăm[ >%%after-hundred>];",
        "(1000, 999999)": "<< nghìn[ >%%after-thousand-or-more>];",
        "(1000000, 999999999)": "<< triệu[ >%%after-hundred>];",
        "(1000000000, 999999999999999999)": "<< tỷ[ >%%after-hundred>];",
        "(1000000000000000000, 'inf')": "=#,##0=;"
    },
    "%spellout-numbering": {
        "(0, 'inf')": "=%spellout-cardinal=;"
    },
    "%spellout-numbering-year": {
        "(0, 'inf')": "=%spellout-numbering=;"
    },
    "%spellout-ordinal": {
        "0": "thứ =%spellout-cardinal=;",
        "1": "thứ nhất;",
        "2": "thứ nhì;",
        "3": "thứ =%spellout-cardinal=;",
        "4": "thứ tư;",
        "(5, 'inf')": "thứ =%spellout-cardinal=;"
    }
}