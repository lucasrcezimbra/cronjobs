# Cronjobs

[![Coverage Status](https://coveralls.io/repos/github/lucasrcezimbra/cronjobs/badge.svg)](https://coveralls.io/github/lucasrcezimbra/cronjobs)



## Setup
```bash
poetry install
cp contrib/env-sample .env
# add your credentials to .env
```


## Usage
### agilize
#### Download prolabore
```bash
poetry run python -m cronjobs.agilize_prolabore 2021-01-01
```

#### Download taxes
```bash
poetry run python -m cronjobs.agilize_taxes 2021-01-01
```


### Gastos Nubank
```bash
pynubank  # to get a certificate
```
```bash
poetry run python -m cronjobs.gastos.nubank 2023-01-01
```


### Gastos Itaú
```bash
poetry run python -m cronjobs.gastos.itau 2023-01-01
```
