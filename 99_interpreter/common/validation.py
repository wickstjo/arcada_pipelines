type_mapping = {
    'str': str,
    'int': int,
    'float': float,
    'list': list
}

def compare_dicts(user_dict: dict, ref_dict: dict, root_path=''):
    for key in ref_dict.keys():

        # CONSTRUCT KEY PATH FOR DEBUGGING CLARITY
        path: str = f'{root_path}.{key}'
        if len(root_path) == 0: path = key

        # MAKE SURE THE KEY EXISTS
        assert key in user_dict, f"KEY '{path}' NOT FOUND"

        # KEEP UNRAVELING DICTS
        if isinstance(ref_dict[key], dict):
            compare_dicts(user_dict[key], ref_dict[key], path)

        # OTHERWISE, VERIFY THAT VALUE TYPE IS CORRECT
        else:
            type_str: str = ref_dict[key]
            assert type_str in type_mapping, f"TYPE '{type_str}' MISSING FROM MAPPING"

            intended_type = type_mapping[type_str]
            assert isinstance(user_dict[key], intended_type), f"KEY '{path}' IS OF WRONG TYPE ({type(user_dict[key])} != {intended_type})"