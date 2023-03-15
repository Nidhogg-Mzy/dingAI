# QQbot: A backend qq bot message processor.

## 0. Frontend:

To be added.

## 1. Config Files
All configurations are specified in `config.json`. There are two parts currently, `accounts`, `database`.
The configs should be self-explanatory.

You can edit from the template we provided.
```bash
cp config-template.json config.json
```

The config file should have such json structure.
```json
{
  "accounts": {
      "official_bot": 12345678,
      "official_group": 12345678,
      "testing_bot": 12345678,
      "testing_group": 12345678
  },
  "database": {
      "username": "foo",
      "password": "bar",
      "ip": "127.0.0.1",
      "database": "bot"
  }
}
```

Note that `ddl.json` and `user.json` will be used and written by the program.
Initially they should be created with content `[]`.

## 2. Install Google Driver for using Leetcode Module

TBA. Simple instructions can be found in `install-chrome-driver.md`.

## 3. Run the project
### 3.1 Install requirements
We recommend you to use a new conda environment.
All packages required can be found in `requirements.txt`.
```bash
conda create --name qqbot python=3.9  # at least 3,8
conda activate qqbot
pip install -r requirements.txt
```

### 3.2 Run the project
```bash
python3 qq_receive.py
```
Details TBA.