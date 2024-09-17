import funcs.misc as misc

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_feature_suite:
    def __init__(self):

        # REQUIRED YAML PARAMS
        self.REQUIRED_YAML_PARAMS = {
            'first_column': str,
            'second_column': str,
            'new_column_name': str,
        }

    ########################################################################################################
    ########################################################################################################

    def apply(self, input_row: dict, yaml_params: dict) -> dict:
        
        # VALIDATE YAML PROPS
        props: dict = misc.validate_dict(yaml_params, self.REQUIRED_YAML_PARAMS, ns=True)

        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE
        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE
        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE

        # CREATE NEW FEATURE
        input_row[props.new_column_name] = input_row[props.first_column] * input_row[props.second_column]

        return input_row