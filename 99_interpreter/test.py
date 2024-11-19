from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import random, time

class my_model:
    def fit(self, features, labels=None):
        # raise NotImplementedError()
        return self

    def predict(self, features):
        # raise NotImplementedError()
        print(features)
        return features
    
class base_feature:
    
    # REQUIRED METHOD, EVEN THO IT DOES NOTHING FOR FEATURES
    # ...TO COMPLY WITH SKLEARN PIPELINES
    def fit(self, features, labels=None):
        return self

    def transform(self, features):
        raise NotImplementedError()
    
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
    
def dict_dataset(length: int):
    return [{
        'symbol': 'SYNTH',
        'timestamp': int(time.time()) + x,
        'open': round(random.uniform(1, 10), 3),
        'close': round(random.uniform(1, 10), 3),
        'high': round(random.uniform(1, 10), 3),
        'low': round(random.uniform(1, 10), 3),
        'volume': random.randrange(50, 200),
    } for x in range(length)]

foo = Pipeline([
    ('feature', to_feature_vectors({ 'required_keys': ['open', 'close'] })),
    ('scaler', StandardScaler()),
    ('custom_regressor', my_model())
])

dataset = dict_dataset(20)
train_data = dataset[:16]
test_data = dataset[16:]

pipe = foo.fit(train_data)
print('----')
pipe.predict(test_data)