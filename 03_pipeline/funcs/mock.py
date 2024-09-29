class ml_model:
    def __init__(self, model_name, model_version):
        self.model_name = model_name
        self.model_version = model_version

    def predict(self, input):
        return f'{input} -> [{self.model_name}, v_{self.model_version}]'