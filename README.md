# hearthbot
Hearthstone/Github bot for Discord


## Available commands:
- `!card [partial_name|"exact_name"|CardID|DbfID]` 
  - Use `!cardc` to search for collectible and `!cardn` for non-collectible cards only
  - Supported flags:
    - `--tags`: Lists all tags on the card
    - `--reqs`: Lists all play requirements for the card
    - `--lang=[enUS|deDE|zhCN|...]`: prints card name, text and flavor text in given language
- `!enum [EnumName] [partial_name|"exact_name"|value]` 
  - `EnumName` can be the [class name](https://github.com/HearthSim/python-hearthstone/blob/master/hearthstone/enums.py#L599) or the [original name](https://github.com/HearthSim/python-hearthstone/blob/master/hearthstone/enums.py#L600)
  - Supports multipe names/values (e.g. `!enum CardClass 1 2 3 warr`)
- `!tag [partial_name|"exact_name"|value]` (equivalent to `!enum GameTag`)


## Github issue linking:
- Automatically links the corresponding issue for `[prefix]#\d+` (see [config_example](https://github.com/azeier/hearthbot/blob/master/config_example.json))  
- Supports multiple issues per message, e.g. `We need to fix hdt#133 and hdt#1731`.
- Supports linking issues without required prefix for specific channels. E.g., `#123` in channel "hdt" will also link to the issue (using the config_example).
