import yaml, composer
class Loader(yaml.reader.Reader, yaml.scanner.Scanner, yaml.parser.Parser, composer.Composer, yaml.constructor.Constructor, yaml.resolver.Resolver):
    def __init__(self, stream):
        yaml.reader.Reader.__init__(self, stream)
        yaml.scanner.Scanner.__init__(self)
        yaml.parser.Parser.__init__(self)
        composer.Composer.__init__(self)
        yaml.constructor.Constructor.__init__(self)
        yaml.resolver.Resolver.__init__(self)
