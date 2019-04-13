# Patterns

## Casting / Typing

### environs

    max_connections = env.int("MAX_CONNECTIONS")  # => 100
    ship_date = env.date("SHIP_DATE")  # => datetime.date(1984, 6, 25)
    ttl = env.timedelta("TTL")  # => datetime.timedelta(0, 42)

### ConfigObj

See Validating below.

### Sanic Envconfig

Uses type annotations and parser extentions:

    class Color(Enum):
        RED = 0
        BLUE = 1

    class Config(EnvConfig):
        DEBUG: bool
        DB_URL: str
        WORKERS: int = 1
        COLOR: Color = None

    @Config.parse(Color)
    def parse_color(value):
        return Color[value.upper()]

### Profig

Custom DSL which appears to be similar to json/yaml:


## Validating

### environs

*simple*

    env.int("TTL", validate=lambda n: n > 0)

*external libs*

    # using marshmallow validators
    from marshmallow.validate import OneOf

    env.str(
        "NODE_ENV",
        validate=OneOf(
            ["production", "development"], error="NODE_ENV must be one of: {choices}"
        ),
    )
    # => Environment variable "NODE_ENV" invalid: ['NODE_ENV must be one of: production, development']

    # multiple validators
    from marshmallow.validate import Length, Email

    env.str("EMAIL", validate=[Length(min=4), Email()])
    # => Environment variable "EMAIL" invalid: ['Shorter than minimum length 4.', 'Not a valid email address.']

### ConfigObj

Note that this validation also converts/casts values.

*configSpec*

    name = string(min=1, max=30, default=Fred)
    age = float(min=0, max=200, default=29)
    attributes = string_list(min=5, max=5, default=list('arms', 'legs', 'head', 'body', 'others'))
    likes_cheese = boolean(default=True)
    favourite_color = option('red', 'green', 'blue', default="red")

*usage*

    import sys
    from configobj import ConfigObj
    from validate import Validator

    config = ConfigObj('config.ini', configspec='configspec.ini')

    validator = Validator()
    result = config.validate(validator)

    if result != True:
        print 'Config file validation failed!'
        sys.exit(1)

## Nesting

### ConfigObj

    name = Michael Foord
    DOB = 12th August 1974
    nationality = English

    [Favourites]
        food = Steak & chips
        color = Vaguely Purple

        [[software]]
            ide = Wing
            os = Undecided


## Application Update

Reload a config instance from external sources.

### ConfigObj

    config.reload()

## Application Reset

Restores a config instance to a freshly created state.

### ConfigObj

    config.reset()

## User Updates

### ConfigObj

Manipulate just like a dict:

    config['Favourites']['software'] = {'ide': 'Emacs'}

## Config usecases

### ConfigObj

> There are, broadly speaking, two different use cases for configuration files ...
> The first is for retrieving options set by the user, ... read-only access ...
> The second way of using config files is for persisting internal configuration data ... these may include data structures
> If you want this data to be human readable ... then you need some kind of text based serialization protocol.

## Interpolation

### Profig

Use format strings:

    >>> '{0[server.host]}:{0[server.port]}'.format(cfg)
    localhost:8080
    >>> '{c[server.host]}:{c[server.port]}'.format(c=cfg)
    localhost:8080
    >>> '{host}:{port}'.format(**c.section('server'))
    localhost:8080

## (De)Serialisation

### Profig

    >>> import json
    >>> s = json.dumps(cfg.as_dict())
    >>> cfg.update(json.loads(s))
