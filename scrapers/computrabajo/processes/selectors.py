OFFERS_CARD = "article.box_offer"

NO_RESULTS_CONTAINER = ".bg-white.p30.tc"

STOP_TEXTS = [
    "No hay más ofertas",
    "Ya viste todas las ofertas",
]

POPUP = {
    "selector": "#pop-up-webpush-sub",
    "close_strategies": [
        "button[onclick*='webpush_subscribe_ko']",
        "button:has-text('Ahora no')"
    ],
}

BASE_URL = "https://co.computrabajo.com"
TITLE_LINK = "a.js-o-link"
COMPANY_LINK = "p.dFlex a"
RATING = "span.fwB"
LOCATION = "p.fs16.fc_base.mt5:not(.dFlex) span.mr10"
MODALITY = ".i_home_office + span"
PUBLISHED_TIME = "p.fs13.fc_aux.mt15"
DESCRIPTION = ".description_offer .fs16.t_word_wrap"