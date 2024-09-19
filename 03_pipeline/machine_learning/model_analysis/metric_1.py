import funcs.misc as misc
import time, random

# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!
# REMEMBER TO TRACK WHAT PIP LIBRARIES YOU NEED TO HAVE INSTALLED THIS CODE TO WORK !!!

class create_metric_suite:
    def __init__(self):

        # REQUIRED YAML PARAMS
        self.REQUIRED_YAML_PARAMS = {
            'artificial_delay': float,
            'threshold': float
        }

    ########################################################################################################
    ########################################################################################################

    def measure(self, yaml_params: dict) -> bool:
        
        # VALIDATE YAML PROPS
        props: dict = misc.validate_dict(yaml_params, self.REQUIRED_YAML_PARAMS, ns=True)

        # MAKE SURE THE PROBE THRESHOLD MAKES SENSE
        if (props.threshold > 1) or (props.threshold < 0):
            raise Exception(f'PROBE THRESHOLD MUST BE BETWEEN 0 AND 1, {props.threshold } WAS GIVEN')

        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE
        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE
        ### TODO: IMPLEMENT TRY-CATCH ON PIPELINE SIDE

        # SLEEP FOR ABIT, THEN GENERATE A NUMBER BETWEEN 0 AND 1
        time.sleep(props.artificial_delay)
        result: float = random.uniform(0, 1)

        # IF THE NUMBER EXCEEDS THE THRESHOLD, PROBE FOUND A POTENTIAL PROBLEM
        # THEREFORE, TRIGGER THE NEXT STEP
        if result >= props.threshold:
            return True
        
        # OTHERWISE, NO FURTHER ACTIONS ARE NECESSARY
        return False