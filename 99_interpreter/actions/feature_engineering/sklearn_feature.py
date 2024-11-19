from base_feature import base_feature

class to_feature_vectors(base_feature):
    def __init__(self, input_params: dict):
        assert isinstance(input_params, dict)
        assert 'required_keys' in input_params
        assert isinstance(input_params['required_keys'], list)
        assert len(input_params['required_keys']) > 0
        
        self.required_keys = input_params['required_keys']

    def transform(self, input_data):
        assert isinstance(input_data, list)
        assert len(input_data) > 0
        assert isinstance(input_data[0], dict)

        # CONVERT LIST OF DICTS TO LIST OF PURE VALUES 
        return [self.vectorize(row_as_dict) for row_as_dict in input_data]

    def vectorize(self, dict_row: dict):
        container = []

        for key in self.required_keys:
            assert key in dict_row, f"KEY '{key}' MISSING FROM INPUT ROW"
            container.append(dict_row[key])
        
        return container