import random
import time, sys
from web3.exceptions import TransactionNotFound
from web3 import Web3
from client import Client, TokenAmount, logger
from config import TOKEN_ZKSTARS
from utils.read_json import read_json
from utils.contracts import contractsZKStars
import asyncio
def chek_gas_eth(max_gas_):
    RPC_ETH = 'https://rpc.builder0x69.io'
    try:
        eth_w3 = Web3(Web3.HTTPProvider(RPC_ETH, request_kwargs={'timeout': 120}))
        while True:
            res = int(round(Web3.from_wei(eth_w3.eth.gas_price, 'gwei')))
            if res <= max_gas_:
                break
            else:
                print((f'Газ сейчас - {res} gwei\n'))
                time.sleep(60)
                continue
    except:
        return 0
def show_progress(total_time):
    start_time = time.time()
    elapsed_time = 0
    while elapsed_time < total_time:
        elapsed_time = time.time() - start_time
        remaining_time = total_time - elapsed_time
        progress = elapsed_time / total_time * 100

        # Очистить предыдущий вывод
        sys.stdout.write("\r")
        sys.stdout.flush()

        # Отображение временной шкалы и оставшегося времени
        sys.stdout.write("[{:20s}] {:.2f}% ({:.2f}/{:.2f} sec)".format(
            '#' * int(progress / 5),
            progress,
            elapsed_time,
            total_time
        ))
        sys.stdout.flush()

        time.sleep(1)

class ZkStars:
    abi = read_json(TOKEN_ZKSTARS)

    def __init__(self, client: Client, maxGas):
        self.client = client
        self.maxGas = maxGas

    async def mintZkStars(self, contract_star: str,  retry=0):
        try:
            contract = self.client.w3.eth.contract(address=contract_star, abi=ZkStars.abi)
            amount = contract.functions.getPrice().call()
            name = contract.functions.name().call()
            print(f'{self.client.address} | mint {name}...')
            logger.info(f'{self.client.address} | mint {name}...')
            chek_gas_eth(self.maxGas)
            tx = self.client.send_transaction(
                to=contract_star,
                data=contract.encodeABI('safeMint',
                                        args=[self.client.address]
                                        ),
                value=amount
            )

            await asyncio.sleep(5)
            verify = self.client.verif_tx(tx)
            if verify == False:
                retry += 1
                if retry < 5:
                    print(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    logger.error(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    print('Time sleep 20 seconds')
                    asyncio.sleep(20)
                    self.mintZkStars(contract_star, retry)

                else:
                    print(f"ERROR MINT")
                    logger.error(f"{self.client.address} | ERROR MINT")
                    return 0


        except TransactionNotFound:
            print(
                f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            logger.error(
                f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            self.mintZkStars(contract_star, retry)


        except ConnectionError:
            print(f'{self.client.address} | Internet connection error or problems with the RPC')
            logger.error(f'{self.client.address} | Internet connection error or problems with the RPC')
            await asyncio.sleep(120)
            print('Time sleep 120 seconds')
            retry += 1
            if retry > 5:
                return 0
            self.mintZkStars(contract_star, retry)

        except Exception as error:
            print(f"{self.client.address} | Unknown Error:  {error} \n Mayber not Gas")
            logger.error(f'{self.client.address} | Unknown Error:  {error}')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)

            retry += 1
            if retry > 5:
                return 0
            self.mintZkStars(contract_star, retry)



