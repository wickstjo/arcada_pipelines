import funcs.misc as misc

########################################################################################################
########################################################################################################

# FETCH YAML CONFIG AND CONVERT IT INTO A NAMESPACE
def global_config():
    data_dict = misc.load_yaml('../00_configs/global_config.yaml')
    return misc.DICT_NAMESPACE(data_dict)

########################################################################################################
########################################################################################################