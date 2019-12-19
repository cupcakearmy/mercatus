class GeneratorDict(dict):
    def __init__(self, *args, generator=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not generator:
            def generator(x): return x

        self.generator = generator

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except:
            value = self.generator(key)
            super().__setitem__(key, value)
            return value
