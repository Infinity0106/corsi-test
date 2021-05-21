# RUN

## install dependencies

```shell
pip install -r requirements.txt
```

open three terminal

```shell
# demo of lsl data posting
$ python lsl/LSL_write.py
```

## run saver

para captar aura_power y aura_corsi para eventos y guardar csv

```shell
$ cd src && python saver.py
```

## run corsi test

```shell
$ python main.py
```

to change language change variable in `translate.py` DEFAULT_LANGUAGE select one of [en, jp]
