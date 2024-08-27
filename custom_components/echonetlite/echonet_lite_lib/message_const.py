EHD1 = {
    0x00: 'Not available',
    0x10: 'Conventional ECHONET Lite Specification'
}

EHD2 = {
    0x81: 'Format 1 (specified message format)',
    0x82: 'Format 2 (arbitrary message format)'
}

GETC = 0x60
SETC = 0x61
GET = 0x62
INFREQ = 0x63
SETGET = 0x6E
SETRES = 0x71
GETRES = 0x72
INF = 0x73
INFC = 0x74
INFC_RES = 0x7A
SETGET_RES = 0x7E
SETI_SNA = 0x50
SETC_SND = 0x51
GET_SNA = 0x52
INF_SNA = 0x53
SETGET_SNA = 0x5E

ESV_CODES = [
    GETC,
    SETC,
    GET,
    INFREQ,
    SETGET,
    SETRES,
    GETRES,
    INF,
    INFC,
    INFC_RES,
    SETGET_RES,
    SETI_SNA,
    SETC_SND,
    GET_SNA,
    INF_SNA,
    SETGET_SNA,
]