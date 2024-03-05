# Появились какие то вопросы по скрипту?
# Задай любой вопрос мне в телеграмм --> @Tih000


maxGas = 75          # Максимальный газ (если газ больше этого значения, транзакции будут делаться только в моменты, когда газ <= этому значению)
delay_min = 180      # Минимальная задержка (то через сколько минимально будет сделана следующая транзакция)
delay_max = 200      # Максимальная задержка (то через сколько максимальная будет сделана следующая транзакция)
                     # Выбирается случайное число из задержек и на это время транзакции выполнятся не будут

amount_min = 0.015   # Минимальная сумма в ETH
amount_max = 0.019 # Максимальная сумма в ETH
                     # Выбирается случайное cчисло среди этих значний и это будет является наша сумма свапа или бриджа

everybody = False    # действия будут происходить асинхронно или поочереди (True - ассинхронно  False - поочереди)
useProxy = False     # Используются ли прокси в файле
numberCircles = 1   # количество кругов выполнения (то, сколько раз будет выполнятся определенное действие)
stayBalance = 0      # количество ETH, оставшегося на балансе при выводе на ОКХ

#----OKX----#
symbolWithdraw = "ETH"            # символ токена
network = "Arbitrum One"          # ID сети (Arbitrum One, zkSync, Optimism, Base, Ethereum)
okx_apikey = ""     # API KEY OKX
okx_apisecret = ""  # Секретная фраза OKX
okx_passphrase = "" # Пароль от API KEY






import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.absolute()

ABIS_DIR = os.path.join(ROOT_DIR, 'abis')

TOKEN_USDC = os.path.join(ABIS_DIR, 'USDC.json')
TOKEN_USDT = os.path.join(ABIS_DIR, 'USDT.json')
TOKEN_WBTC = os.path.join(ABIS_DIR, 'WBTC.json')
TOKEN_DAI = os.path.join(ABIS_DIR, 'DAI.json')
TOKEN_AMBIENT = os.path.join(ABIS_DIR, 'ambient.json')
TOKEN_ZKSTARS = os.path.join(ABIS_DIR, 'ZKStars19.json')
TOKEN_SKYDROME = os.path.join(ABIS_DIR, 'skydrome.json')
TOKEN_SPACEFI = os.path.join(ABIS_DIR, 'spaceFI.json')
TOKEN_PAPIRUS = os.path.join(ABIS_DIR, 'papirus.json')
TOKEN_NFTS = os.path.join(ABIS_DIR, 'nft.json')
TOKEN_OFFICIAL_BRIDGE = os.path.join(ABIS_DIR, 'officialbridge.json')
TOKEN_ONCHAIN_POWER = os.path.join(ABIS_DIR, 'onchainPower.json')
TOKEN_ZERIUS = os.path.join(ABIS_DIR, 'zerius.json')