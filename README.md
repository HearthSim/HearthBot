# hearthbot
Hearthstone/Github bot for Discord


## Available commands:
- `!card [CardId|partial_name]` (alternatively use `cardc` or `cardn` for collectible/non-collectible cards only)
- `!enum [EnumName] [partial_name|value]` EnumName support the [class name](https://github.com/HearthSim/python-hearthstone/blob/master/hearthstone/enums.py#L599) as well as the [doc](https://github.com/HearthSim/python-hearthstone/blob/master/hearthstone/enums.py#L600)
- `!tag [partial_name|value]` (equivalent to `!enum GameTag`)

## Github issue linking:
- Automatically links the corresponding issue for `[prefix]#\d+` (see [config_example](https://github.com/azeier/hearthbot/blob/master/config_example.json))  
- Supports multiple issues per message, e.g. `We need to fix hdt#133 and hdt#1731`.
- Supports linking issues without required prefix for specific channels. E.g., `#123` in channel "hdt" will also link to the issue (using the config_example).
