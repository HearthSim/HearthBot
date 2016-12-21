# hearthbot
Hearthstone/Github bot for Discord


## Available commands:
- `!card [CardId|partial_name]`
- `!enum [EnumName] [partial_name|value]`
- `!tag [partial_name|value]` (equivalent to `!enum GameTag`)

## Github issue linking:
- Automatically links the corresponding issue for `[prefix]#\d+` (see [config_example](https://github.com/azeier/hearthbot/blob/master/config_example.json))  
- Supports multiple issues per message, e.g. `We need to fix hdt#133 and hdt#1731`.
- Supports linking issues without required prefix for specific channels. E.g., `#123` in channel "hdt" will also link to the issue (using the config_example).
