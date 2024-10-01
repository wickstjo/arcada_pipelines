class ml_model:
    def __init__(self, model_name, version_alias, version_number):
        self.model_name = model_name
        self.version_alias = version_alias
        self.version_number = version_number

    def predict(self, input):
        return f'{input} -> [{self.model_name}, v_{self.version_number}]'