# -*- coding: utf-8 -*-
info = {
    "name": "gd",
    "date_order": "DMY",
    "january": [
        "am faoilleach",
        "faoi",
        "dhen fhaoilleach"
    ],
    "february": [
        "an gearran",
        "gearr",
        "dhen ghearran"
    ],
    "march": [
        "am màrt",
        "màrt",
        "dhen mhàrt"
    ],
    "april": [
        "an giblean",
        "gibl",
        "dhen ghiblean"
    ],
    "may": [
        "an cèitean",
        "cèit",
        "dhen chèitean"
    ],
    "june": [
        "an t-ògmhios",
        "ògmh",
        "dhen ògmhios"
    ],
    "july": [
        "an t-iuchar",
        "iuch",
        "dhen iuchar"
    ],
    "august": [
        "an lùnastal",
        "lùna",
        "dhen lùnastal"
    ],
    "september": [
        "an t-sultain",
        "sult",
        "dhen t-sultain"
    ],
    "october": [
        "an dàmhair",
        "dàmh",
        "dhen dàmhair"
    ],
    "november": [
        "an t-samhain",
        "samh",
        "dhen t-samhain"
    ],
    "december": [
        "an dùbhlachd",
        "dùbh",
        "dhen dùbhlachd"
    ],
    "monday": [
        "diluain",
        "dil"
    ],
    "tuesday": [
        "dimàirt",
        "dim"
    ],
    "wednesday": [
        "diciadain",
        "dic"
    ],
    "thursday": [
        "diardaoin",
        "dia"
    ],
    "friday": [
        "dihaoine",
        "dih"
    ],
    "saturday": [
        "disathairne",
        "dis"
    ],
    "sunday": [
        "didòmhnaich",
        "did"
    ],
    "am": [
        "m"
    ],
    "pm": [
        "f"
    ],
    "year": [
        "bliadhna",
        "blia",
        "bl"
    ],
    "month": [
        "mìos",
        "mì"
    ],
    "week": [
        "seachdain",
        "seachd",
        "sn"
    ],
    "day": [
        "latha",
        "là"
    ],
    "hour": [
        "uair a thìde",
        "uair",
        "u"
    ],
    "minute": [
        "mionaid",
        "mion",
        "m"
    ],
    "second": [
        "diog",
        "d"
    ],
    "relative-type": {
        "1 year ago": [
            "an-uiridh",
            "an-uir"
        ],
        "0 year ago": [
            "am bliadhna",
            "am bl"
        ],
        "in 1 year": [
            "an ath-bhliadhna",
            "an ath-bhl"
        ],
        "1 month ago": [
            "am mìos seo chaidh",
            "am mìos sa chaidh",
            "mì ch"
        ],
        "0 month ago": [
            "am mìos seo",
            "am mì seo"
        ],
        "in 1 month": [
            "an ath-mhìos",
            "ath-mhì"
        ],
        "1 week ago": [
            "an t-seachdain seo chaidh",
            "seachd sa chaidh",
            "sn ch"
        ],
        "0 week ago": [
            "an t-seachdain seo",
            "an t-seachd seo",
            "an t-sn seo"
        ],
        "in 1 week": [
            "an ath-sheachdain",
            "an ath-sheachd",
            "ath-shn"
        ],
        "1 day ago": [
            "an-dè"
        ],
        "0 day ago": [
            "an-diugh"
        ],
        "in 1 day": [
            "a-màireach"
        ],
        "0 hour ago": [
            "this hour"
        ],
        "0 minute ago": [
            "this minute"
        ],
        "0 second ago": [
            "an-dràsta"
        ]
    },
    "relative-type-regex": {
        "in \\1 year": [
            "an ceann (\\d+) bhliadhna",
            "an ceann (\\d+) bliadhna",
            "an (\\d+) bhlia",
            "an (\\d+) blia"
        ],
        "\\1 year ago": [
            "(\\d+) bhliadhna air ais",
            "(\\d+) bliadhna air ais",
            "o (\\d+) bhlia",
            "o (\\d+) blia"
        ],
        "in \\1 month": [
            "an ceann (\\d+) mhìosa",
            "an ceann (\\d+) mìosa",
            "an (\\d+) mhìos",
            "an (\\d+) mìos"
        ],
        "\\1 month ago": [
            "(\\d+) mhìos air ais",
            "(\\d+) mìos air ais",
            "o (\\d+) mhìos",
            "o (\\d+) mìos"
        ],
        "in \\1 week": [
            "an ceann (\\d+) seachdain",
            "an (\\d+) sheachd",
            "an (\\d+) seachd"
        ],
        "\\1 week ago": [
            "(\\d+) seachdain air ais",
            "o (\\d+) sheachd",
            "o (\\d+) seachd"
        ],
        "in \\1 day": [
            "an ceann (\\d+) latha",
            "an (\\d+) là"
        ],
        "\\1 day ago": [
            "(\\d+) latha air ais",
            "o (\\d+) là"
        ],
        "in \\1 hour": [
            "an ceann (\\d+) uair a thìde",
            "an (\\d+) uair"
        ],
        "\\1 hour ago": [
            "(\\d+) uair a thìde air ais",
            "o (\\d+) uair"
        ],
        "in \\1 minute": [
            "an ceann (\\d+) mhionaid",
            "an ceann (\\d+) mionaid",
            "an (\\d+) mhion",
            "an (\\d+) mion"
        ],
        "\\1 minute ago": [
            "(\\d+) mhionaid air ais",
            "(\\d+) mionaid air ais",
            "o (\\d+) mhion",
            "o (\\d+) mion"
        ],
        "in \\1 second": [
            "an ceann (\\d+) diog",
            "an (\\d+) diog"
        ],
        "\\1 second ago": [
            "(\\d+) diog air ais",
            "o (\\d+) diog"
        ]
    },
    "locale_specific": {},
    "skip": [
        " ",
        ".",
        ",",
        ";",
        "-",
        "/",
        "'",
        "|",
        "@",
        "[",
        "]",
        "，"
    ]
}