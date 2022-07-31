# Cronjobs

[![Coverage Status](https://coveralls.io/repos/github/lucasrcezimbra/cronjobs/badge.svg)](https://coveralls.io/github/lucasrcezimbra/cronjobs)


## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp contrib/env-sample .env
# add your credentials to .env
```

### nubank_spreadsheet
```bash
pynubank  # to get a certificate
```


## Usage

### agilize

#### Download prolabore

```bash
source .venv/bin/activate
python -m agilize_prolabore 2021-01-01
```

#### Download taxes

```bash
source .venv/bin/activate
python -m agilize_taxes 2021-01-01
```


### nubank_spreadsheet

```bash
source .venv/bin/activate
python -m nubank_spreadsheet 2021-01-01
```

### itau_spreadsheet

```bash
source .venv/bin/activate
python -m itau_spreadsheet 2021-01-01
```
