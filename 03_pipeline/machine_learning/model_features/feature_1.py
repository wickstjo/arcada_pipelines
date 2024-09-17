import funcs.misc as misc

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_feature_suite:
    def __init__(self):

        # REQUIRED YAML PARAMS
        self.REQUIRED_YAML_PARAMS = {
            'target_column': str,
            'multiply_by': int
        }

    ########################################################################################################
    ########################################################################################################

    def apply(self, input_row: dict, yaml_params: dict) -> dict:
        
        # VALIDATE YAML PROPS
        props: dict = misc.validate_dict(yaml_params, self.REQUIRED_YAML_PARAMS, ns=True)

        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE
        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE
        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE

        # REPLACE OLD COLUMN VALUE WITH FEATURE
        input_row[props.target_column] = input_row[props.target_column] * props.multiply_by

        return input_row