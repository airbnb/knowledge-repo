# -*- coding: utf-8 -*-
info = {
    "name": "da",
    "date_order": "DMY",
    "january": [
        "januar",
        "jan"
    ],
    "february": [
        "februar",
        "feb"
    ],
    "march": [
        "marts",
        "mar"
    ],
    "april": [
        "april",
        "apr"
    ],
    "may": [
        "maj"
    ],
    "june": [
        "juni",
        "jun"
    ],
    "july": [
        "juli",
        "jul"
    ],
    "august": [
        "august",
        "aug"
    ],
    "september": [
        "september",
        "sep"
    ],
    "october": [
        "oktober",
        "okt"
    ],
    "november": [
        "november",
        "nov"
    ],
    "december": [
        "december",
        "dec"
    ],
    "monday": [
        "mandag",
        "man"
    ],
    "tuesday": [
        "tirsdag",
        "tir"
    ],
    "wednesday": [
        "onsdag",
        "ons"
    ],
    "thursday": [
        "torsdag",
        "tor"
    ],
    "friday": [
        "fredag",
        "fre"
    ],
    "saturday": [
        "lørdag",
        "lør"
    ],
    "sunday": [
        "søndag",
        "søn"
    ],
    "am": [
        "am"
    ],
    "pm": [
        "pm"
    ],
    "year": [
        "år"
    ],
    "month": [
        "måned",
        "md",
        "måneder"
    ],
    "week": [
        "uge",
        "uger"
    ],
    "day": [
        "dag",
        "dage"
    ],
    "hour": [
        "time",
        "t",
        "timer"
    ],
    "minute": [
        "minut",
        "min",
        "minutter"
    ],
    "second": [
        "sekund",
        "sek",
        "s",
        "sekunder"
    ],
    "relative-type": {
        "1 year ago": [
            "sidste år"
        ],
        "0 year ago": [
            "i år"
        ],
        "in 1 year": [
            "næste år"
        ],
        "1 month ago": [
            "sidste måned",
            "sidste md"
        ],
        "0 month ago": [
            "denne måned",
            "denne md"
        ],
        "in 1 month": [
            "næste måned",
            "næste md"
        ],
        "1 week ago": [
            "sidste uge"
        ],
        "0 week ago": [
            "denne uge"
        ],
        "in 1 week": [
            "næste uge"
        ],
        "1 day ago": [
            "i går"
        ],
        "0 day ago": [
            "i dag"
        ],
        "in 1 day": [
            "i morgen"
        ],
        "0 hour ago": [
            "i den kommende time"
        ],
        "0 minute ago": [
            "i det kommende minut"
        ],
        "0 second ago": [
            "nu"
        ]
    },
    "relative-type-regex": {
        "in \\1 year": [
            "om (\\d+) år"
        ],
        "\\1 year ago": [
            "for (\\d+) år siden"
        ],
        "in \\1 month": [
            "om (\\d+) måned",
            "om (\\d+) måneder",
            "om (\\d+) md",
            "om (\\d+) mdr"
        ],
        "\\1 month ago": [
            "for (\\d+) måned siden",
            "for (\\d+) måneder siden",
            "for (\\d+) md siden",
            "for (\\d+) mdr siden"
        ],
        "in \\1 week": [
            "om (\\d+) uge",
            "om (\\d+) uger"
        ],
        "\\1 week ago": [
            "for (\\d+) uge siden",
            "for (\\d+) uger siden"
        ],
        "in \\1 day": [
            "om (\\d+) dag",
            "om (\\d+) dage"
        ],
        "\\1 day ago": [
            "for (\\d+) dag siden",
            "for (\\d+) dage siden"
        ],
        "in \\1 hour": [
            "om (\\d+) time",
            "om (\\d+) timer"
        ],
        "\\1 hour ago": [
            "for (\\d+) time siden",
            "for (\\d+) timer siden",
            "for (\\d+)\\s*h",
            "for (\\d+) timer"
        ],
        "in \\1 minute": [
            "om (\\d+) minut",
            "om (\\d+) minutter",
            "om (\\d+) min"
        ],
        "\\1 minute ago": [
            "for (\\d+) minut siden",
            "for (\\d+) minutter siden",
            "for (\\d+) min siden",
            "for (\\d+)\\s*m",
            "for (\\d+) minutter"
        ],
        "in \\1 second": [
            "om (\\d+) sekund",
            "om (\\d+) sekunder",
            "om (\\d+) sek"
        ],
        "\\1 second ago": [
            "for (\\d+) sekund siden",
            "for (\\d+) sekunder siden",
            "for (\\d+) sek siden",
            "for (\\d+)\\s*s",
            "for (\\d+) sekunder"
        ]
    },
    "locale_specific": {
        "da-GL": {
            "name": "da-GL"
        }
    },
    "skip": [
        "kl",
        "kl.",
        "cirka",
        "d.",
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
    ],
    "sentence_splitter_group": 1,
    "ago": [
        "siden"
    ],
    "in": [
        "i"
    ],
    "simplifications": [
        {
            "en": "1"
        },
        {
            "et": "1"
        },
        {
            "(\\d+)\\s*hr(s?)": "\\1 time\\2"
        },
        {
            "(\\d+)\\s*min(s?)": "\\1 minut\\2"
        },
        {
            "(\\d+)\\s*sec(s?)": "\\1 sekund\\2"
        },
        {
            "middag": "12:00"
        },
        {
            "midnat": "00:00"
        },
        {
            "(\\d+)h(\\d+)m?": "\\1:\\2"
        },
        {
            "mindre end 1 minut siden": "45 seconds"
        }
    ]
}