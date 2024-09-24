from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

class my_custom_feature(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        pass
    
    def transform(self, X, y=None):
        pass

pipeline = Pipeline(steps=[
    ('feature_1', my_custom_feature()),
    ('scaler', StandardScaler()),
    ('model', RandomForestClassifier())
])