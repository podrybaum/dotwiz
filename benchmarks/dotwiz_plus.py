"""DotWizPlus - a high performance dict class with dot notation, and serialization."""


class DotWizPlus:
    def __init__(self, input_dict=None, preprocess=False, **kwargs):
        self.dict = input_dict or {}
        self.dict.update(kwargs)
        self.preprocess = preprocess
        if preprocess:
            self.dict = self._preprocess(self.dict)

    def _preprocess(self, d):
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = DotWizPlus(value, preprocess=True)
        return d

    def __getattr__(self, name):
        if name in self.dict:
            value = self.dict[name]
            if isinstance(value, dict) and not self.preprocess:
                value = DotWizPlus(value)
                self.dict[name] = value
            return value
        raise AttributeError(f"'DotWiz' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in ('dict', 'preprocess'):
            super().__setattr__(name, value)
        else:
            self.dict[name] = value

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def to_dict(self):
        return self.dict
