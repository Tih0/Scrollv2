from web3 import Web3
from config import TOKEN_DAI, TOKEN_USDT, TOKEN_WBTC
from utils.contracts import contract_WBTC, contract_DAI, contract_USDT, contract_USDC
from client import Client
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
import time
from utils.networks import Network


def getBalanceForOne(client: Client, count):
    balance_usdc = client.balance_of(contract_USDC)
    balance_usdt = client.balance_of(contract_USDT)
    balance_wbtc = client.balance_of(contract_WBTC)
    balance_dai = client.balance_of(contract_DAI)
    balance_usdc = format(balance_usdc.Ether, '.4f')
    balance_usdt = format(balance_usdt.Ether, '.4f')
    balance_wbtc = format(balance_wbtc.Ether, '.4f')
    balance_dai = format(balance_dai.Ether, '.4f')
    count_tx = client.w3.eth.get_transaction_count(client.address)
    eth = format(client.w3.eth.get_balance(client.address) / 10 ** 18, '.6f')
    res = (f'{client.address} |-->   ETH: {eth}    USDC: {balance_usdc}    USDT: {balance_usdt}    DAI: {balance_dai}    WBTC: {balance_wbtc}')
    if count == False:
        return res
    else:
        res2 = (f"                                           |-->   Count TXs: {count_tx}")
        return res, res2

def getBalance(client_list: list[Client], num_clients: int, count=False):
    print('BALANCE: \n------------------------------------------')
    threads = []
    mas = []
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = [executor.submit(getBalanceForOne, client_list[i], True) for i in range(num_clients)]
        for future in futures:
            result = future.result()
            time.sleep(1)
            mas.append(result)

    for i in range(num_clients):
        print(mas[i][0])
        print(mas[i][1])
    print('\n\n\n')



def getBalanceForOneNetwork(client: Client, count: int):
    eth = format(client.w3.eth.get_balance(client.address) / 10 ** 18, '.6f')
    res = (f'{client.address} |-->   ETH: {eth}')
    return res
def getBalanceForNetwork(clients: list[Client], count: int):
    print('BALANCE: \n------------------------------------------')
    mas = []
    for i in range(count):
        with ThreadPoolExecutor(max_workers=count) as executor:
            futures = [executor.submit(getBalanceForOneNetwork, clients[i], count)]
            for future in futures:
                result = future.result()
                mas.append(result)

    for i in range(count):
        print(mas[i])
    print('\n\n\n')

