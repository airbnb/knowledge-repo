from .utils import validate_str
import re


@validate_str
def isphone(value, locale='en-US'):
    """
    Return whether or not given value is valid mobile number according to given locale. Default locale is 'en-US'.
    If the value is valid mobile number, this function returns ``True``, otherwise ``False``.
    Supported locales are: ``ar-DZ``, ``ar-SY``, ``ar-SA``, ``en-US``, ``en-CA``, ``cs-CZ``, ``de-DE``, ``da-DK``
    ``el-GR``, ``en-AU``, ``en-GB``, ``en-HK``, ``zh-HK``, ``en-IN``, ``en-NG``, ``en-NZ``, ``en-ZA``, ``en-ZM``
    ``es-ES``, ``fi-FI``, ``fr-FR``, ``he-IL``, ``hu-HU``, ``id-ID``, ``it-IT``, ``ja-JP``, ``ms-MY``, ``nb-NO``
    ``nl-BE``, ``fr-BE``, ``nn-NO``, ``pl-PL``, ``pt-BR``, ``pt-PT``, ``ro-RO``, ``en-PK``, ``ru-RU``, ``sr-RS``
    ``tr-TR``, ``vi-VN``, ``zh-CN``, ``zh-TW``, ``bn-BD``

    Examples::

        >>> isphone('+15673628910', 'en-US')
        True

        >>> isphone('+10345672645', 'en-US')
        False

    :param value: string to validate mobile number
    :param locale: locale of mobile number to validate
    """

    phones = {
        'ar-DZ': r'^(\+?213|0)(5|6|7)\d{8}$',
        'ar-SY': r'^(!?(\+?963)|0)?9\d{8}$',
        'ar-SA': r'^(!?(\+?966)|0)?5\d{8}$',
        'bn-BD': r'^(\+?88)?(01[56789]\d{2}(\s|\-)?\d{6})$',
        'en-US': r'^(\+?1)?[2-9]\d{2}[2-9](?!11)\d{6}$',
        'cs-CZ': r'^(\+?420)? ?[1-9][0-9]{2} ?[0-9]{3} ?[0-9]{3}$',
        'de-DE': r'^(\+?49[ \.\-])?([\(]{1}[0-9]{1,6}[\)])?([0-9 \.\-\']{3,20})((x|ext|extension)[ ]?[0-9]{1,4})?$',
        'da-DK': r'^(\+?45)?(\d{8})$',
        'el-GR': r'^(\+?30)?(69\d{8})$',
        'en-AU': r'^(\+?61|0)4\d{8}$',
        'en-GB': r'^(\+?44|0)7\d{9}$',
        'en-HK': r'^(\+?852\-?)?[569]\d{3}\-?\d{4}$',
        'en-IN': r'^(\+?91|0)?[789]\d{9}$',
        'en-NG': r'^(\+?234|0)?[789]\d{9}$',
        'en-NZ': r'^(\+?64|0)2\d{7,9}$',
        'en-ZA': r'^(\+?27|0)\d{9}$',
        'en-ZM': r'^(\+?26)?09[567]\d{7}$',
        'es-ES': r'^(\+?34)?(6\d{1}|7[1234])\d{7}$',
        'fi-FI': r'^(\+?358|0)\s?(4(0|1|2|4|5)?|50)\s?(\d\s?){4,8}\d$',
        'fr-FR': r'^(\+?33|0)[67]\d{8}$',
        'he-IL': r'^(\+972|0)([23489]|5[0248]|77)[1-9]\d{6}',
        'hu-HU': r'^(\+?36)(20|30|70)\d{7}$',
        'id-ID': r'^(\+?62|0[1-9])[\s|\d]+$',
        'it-IT': r'^(\+?39)?\s?3\d{2} ?\d{6,7}$',
        'ja-JP': r'^(\+?81|0)\d{1,4}[ \-]?\d{1,4}[ \-]?\d{4}$',
        'ms-MY': r'^(\+?6?01){1}(([145]{1}(\-|\s)?\d{7,8})|([236789]{1}(\s|\-)?\d{7}))$',
        'nb-NO': r'^(\+?47)?[49]\d{7}$',
        'nl-BE': r'^(\+?32|0)4?\d{8}$',
        'nn-NO': r'^(\+?47)?[49]\d{7}$',
        'pl-PL': r'^(\+?48)? ?[5-8]\d ?\d{3} ?\d{2} ?\d{2}$',
        'pt-BR': r'^(\+?55|0)\-?[1-9]{2}\-?[2-9]{1}\d{3,4}\-?\d{4}$',
        'pt-PT': r'^(\+?351)?9[1236]\d{7}$',
        'ro-RO': r'^(\+?4?0)\s?7\d{2}(\'|\s|\.|\-)?\d{3}(\s|\.|\-)?\d{3}$',
        'en-PK': r'^((\+92)|(0092))-{0,1}\d{3}-{0,1}\d{7}$|^\d{11}$|^\d{4}-\d{7}$',
        'ru-RU': r'^(\+?7|8)?9\d{9}$',
        'sr-RS': r'^(\+3816|06)[- \d]{5,9}$',
        'tr-TR': r'^(\+?90|0)?5\d{9}$',
        'vi-VN': r'^(\+?84|0)?((1(2([0-9])|6([2-9])|88|99))|(9((?!5)[0-9])))([0-9]{7})$',
        'zh-CN': r'^(\+?0?86\-?)?1[345789]\d{9}$',
        'zh-TW': r'^(\+?886\-?|0)?9\d{8}$'
    }

    phones['en-CA'] = phones['en-US']
    phones['fr-BE'] = phones['nl-BE']
    phones['zh-HK'] = phones['en-HK']

    loc = phones.get(locale)
    if loc is None:
        raise ValueError('Please provide a supported locale.')
    else:
        loc_pattern = re.compile(loc)
        return bool(loc_pattern.match(value))

