from dateutil import parser
import pytz

utc=pytz.UTC

def is_datestring(string):
    try:
        parser.parse(string)
        return True
    except:
        return False

def generate_utc_date(datestring):
    try:
        return utc.localize(parser.parse(datestring))
    except:
        return parser.parse(datestring)