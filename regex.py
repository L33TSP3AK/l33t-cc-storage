
CREDIT_CARD_PATTERNS = {
    "Amex Card": r"^3[47][0-9]{13}$",
    "BCGlobal": r"^(6541|6556)[0-9]{12}$",
    "Carte Blanche Card": r"^389[0-9]{11}$",
    "Diners Club Card": r"^3(?:0[0-5]|[68][0-9])[0-9]{11}$",
    "Discover Card": r"^65[4-9][0-9]{13}|64[4-9][0-9]{13}|6011[0-9]{12}|(622(?:12[6-9]|1[3-9][0-9]|[2-8][0-9][0-9]|9[01][0-9]|92[0-5])[0-9]{10})$",
    "Insta Payment Card": r"^63[7-9][0-9]{13}$",
    "JCB Card": r"^(?:2131|1800|35\d{3})\d{11}$",
    "KoreanLocalCard": r"^9[0-9]{15}$",
    "Laser Card": r"^(6304|6706|6709|6771)[0-9]{12,15}$",
    "Maestro Card": r"^(5018|5020|5038|6304|6759|6761|6763)[0-9]{8,15}$",
    "Mastercard": r"^(5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12}))$",
    "Solo Card": r"^(6334|6767)[0-9]{12}|(6334|6767)[0-9]{14}|(6334|6767)[0-9]{15}$",
    "Switch Card": r"^(4903|4905|4911|4936|6333|6759)[0-9]{12}|(4903|4905|4911|4936|6333|6759)[0-9]{14}|(4903|4905|4911|4936|6333|6759)[0-9]{15}|564182[0-9]{10}|564182[0-9]{12}|564182[0-9]{13}|633110[0-9]{10}|633110[0-9]{12}|633110[0-9]{13}$",
    "Union Pay Card": r"^(62[0-9]{14,17})$",
    "Visa Card": r"^4[0-9]{12}(?:[0-9]{3})?$",
    "Visa, MasterCard, American Express, Diners Club, Discover, and JCB cards": "^(?:4[0-9]{12}(?:[0-9]{3})?|[25][1-7][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})$",
    "Visa Master Card": r"^(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})$"
}




CREDIT_CARD_PATTERNS_TOOLTIPS = {
    "Amex Card": "Starts with 3, followed by 4 or 7, then 13 more digits",
    "BCGlobal": "Starts with 6541 or 6556, followed by 12 digits",
    "Carte Blanche Card": "Starts with 389, followed by 11 digits",
    "Diners Club Card": "Starts with 3, followed by 00-05, 60-69, or 80-89, then 11 more digits",
    "Discover Card": "Complex pattern for various Discover card formats",
    "Insta Payment Card": "Starts with 63, followed by 7, 8, or 9, then 13 more digits",
    "JCB Card": "Starts with 2131, 1800, or 35 followed by 3 digits, then 11 more digits",
    "KoreanLocalCard": "Starts with 9, followed by 15 digits",
    "Laser Card": "Starts with 6304, 6706, 6709, or 6771, followed by 12 to 15 digits",
    "Maestro Card": "Starts with 5018, 5020, 5038, 6304, 6759, 6761, or 6763, followed by 8 to 15 digits",
    "Mastercard": "Complex pattern for various Mastercard formats",
    "Solo Card": "Starts with 6334 or 6767, followed by 12, 14, or 15 digits",
    "Switch Card": "Complex pattern for various Switch card formats",
    "Union Pay Card": "Starts with 62, followed by 14 to 17 digits",
    "Visa Card": "Starts with 4, followed by 12 digits, optionally followed by 3 more digits",
    "Visa, MasterCard, American Express, Diners Club, Discover, and JCB cards": "Visa, MasterCard, American Express, Diners Club, Discover, and JCB cards",
    "Visa Master Card": "Combines Visa and Mastercard patterns"
}