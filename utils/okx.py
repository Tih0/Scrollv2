from utils.networks import Arbitrum, ZKSync, Scroll, Base, Ethereum, Optimism
from client import logger
import ccxt
from config import symbolWithdraw, network, okx_apikey, okx_apisecret, okx_passphrase
mas = [Arbitrum, ZKSync, Scroll, Base, Ethereum, Optimism]
class API:
    # okx API
    okx_apikey = okx_apikey
    okx_apisecret = okx_apisecret
    okx_passphrase = okx_passphrase
def okx_withdraw(address, amount_to_withdrawal, wallet_number):
    for i in range(len(mas)):
        if mas[i].name == network:
            explorer = mas[i].explorer
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
    })

    try:
        print(f"{address} -- Вывод {amount_to_withdrawal} ETH с ОКХ")
        logger.info(f"{address} -- Вывод {amount_to_withdrawal} ETH с ОКХ")
        chainName = symbolWithdraw + "-" + network
        fee = get_withdrawal_fee(symbolWithdraw, chainName)
        tx = exchange.withdraw(symbolWithdraw, amount_to_withdrawal, address,
            params={
                "toAddress": address,
                "chainName": chainName,
                "dest": 4,
                "fee": fee,
                "pwd": '-',
                "amt": amount_to_withdrawal,
                "network": network
            }
        )

        print(f'\n>>>[OKX] Вывел {amount_to_withdrawal} {symbolWithdraw} ', flush=True)
        logger.info(f'>>>[OKX] Withdraw {amount_to_withdrawal} {symbolWithdraw} ')
        print(f'    [{wallet_number}]{address}', flush=True)
        print(f'https://arbiscan.io/address/{address}')
        logger.info(f'[{wallet_number}]{address} : {explorer}{tx["txid"]}')
    except Exception as error:
        print(f'\n>>>[OKx] Не удалось вывести {amount_to_withdrawal} {symbolWithdraw}: {error} ', flush=True)
        print(f'    [{wallet_number}]{address}', flush=True)
        logger.error(f'>>>[OKX] Error in Withdraw OKX: {amount_to_withdrawal} {symbolWithdraw}: {error} ')



def get_withdrawal_fee(symbolWithdraw, chainName):
    exchange = ccxt.okx({
        'apiKey': API.okx_apikey,
        'secret': API.okx_apisecret,
        'password': API.okx_passphrase,
        'enableRateLimit': True,
    })
    currencies = exchange.fetch_currencies()
    for currency in currencies:
        if currency == symbolWithdraw:
            currency_info = currencies[currency]
            network_info = currency_info.get('networks', None)
            if network_info:
                for network in network_info:
                    network_data = network_info[network]
                    network_id = network_data['id']
                    if network_id == chainName:
                        withdrawal_fee = currency_info['networks'][network]['fee']
                        if withdrawal_fee == 0:
                            return 0
                        else:
                            return withdrawal_fee
    raise ValueError(f"     не могу получить сумму комиссии, проверьте значения symbolWithdraw и network")

