# Qtum Orphan Blocks - QtumOB

Qtum blockchain orphan blocks finder for all Qtum core debug files.

### Installation

```shell
$ pip install -r requirements.txt
```

### Configuration

```json5
"debugs": [
    {
      "debug_name": "CBlock grep 2000 matches.txt",
      "save_name": "CBlock grep 2000 matches OB"
    },
    {
      "debug_name": "debug.log qMUR73.txt",
      "start_index": 0,
      "stop_index": 100,
      "save_name": "debug.log qMUR73 OB"
    }
]
```

### Run

```shell
$ python main.py
```
