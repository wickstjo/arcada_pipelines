from common import misc
from datetime import datetime
import time

########################################################################################################
########################################################################################################

# VALIDATE AN INPUT DICT BASED ON A REFERENCE DICT
def validate_dict(input_data: dict, reference: dict, ns=False):
    container = {}

    # REFERENCE DICT: KEY_NAME => TYPE_FUNC
    for prop_name, type_cast_func in reference.items():

        # MAKE SURE DICT KEY EXIST
        if prop_name not in input_data:
            raise Exception(f'KEY ERROR: MISSING PROPERTY ({prop_name})')
        
        # MAKE SURE EVERY VALUE CAN BE CAST TO ITS EXPECTED TYPE
        try:
            input_value = input_data[prop_name]
            container[prop_name] = type_cast_func(input_value)

        except Exception as error:
            raise Exception(f'CASTING ERROR (prop: {prop_name}): {error}')
    
    # CONVERT TO NAMESPACE ON-REQUEST
    if ns: return misc.TO_NAMESPACE(container)

    return container

########################################################################################################
########################################################################################################

# CONVERT STRING TEXT TO UNIX TIMESTAMP
def string_to_unix(date_text: str|int) -> int:

    if type(date_text) == int:
        return date_text

    date_tuple = datetime.strptime(date_text, '%Y-%m-%d')
    return int(time.mktime(date_tuple.timetuple()))

# WHAT SHOULD CLEAN STOCK DATA LOOK LIKE?
REFINED_STOCK_DATA: dict = {
    'symbol': str,
    'timestamp': string_to_unix,
    'high': float,
    'low': float,
    'open': float,
    'close': float,
    'adjusted_close': float,
    'volume': lambda x: int(float(x)),
}

########################################################################################################
########################################################################################################