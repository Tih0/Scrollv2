import time
from web3.exceptions import TransactionNotFound
from web3 import Web3
from client import Client, TokenAmount, logger
from config import TOKEN_SPACEFI
from typing import Optional
from utils.contracts import contract_USDC, contract_USDT, contract_ETH, contract_WBTC, contract_spacefi
from utils.read_json import read_json
import asyncio, random
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
        print('Проверка на газ не произшла!')
        return False


class SpaceFi:
    abi = read_json(TOKEN_SPACEFI)
    def __init__(self, client: Client, maxGas):
        self.client = client
        self.maxGas = maxGas

    async def swap_eth_to_token(self, amount: TokenAmount, contract_token: str, retry = 0, slippage = 0.1):
        print(f"{self.client.address} | SpaceFi Swap | {format(float(amount.Ether), '.5f')} ETH --> {self.client.name(contract_token)}...")
        logger.info(f"{self.client.address} | SpaceFi Swap | {format(float(amount.Ether), '.5f')} ETH --> {self.client.name(contract_token)}...")
        try:
             contract = self.client.w3.eth.contract(address=contract_spacefi, abi=SpaceFi.abi)
             eth_price = self.client.get_eth_price()
             if contract_token == contract_WBTC:
                 wbtc_price = self.client.get_eth_price("BTC")
                 min_to_amount = TokenAmount(
                     amount= (eth_price * float(amount.Ether)) /  wbtc_price * (1 - slippage / 100),
                     decimals= self.client.get_decimals(contract_token)
                 )
             else:
                 min_to_amount = TokenAmount(
                     amount= eth_price * float(amount.Ether) * (1 - slippage / 100),
                     decimals= self.client.get_decimals(contract_token)
                 )
             chek = chek_gas_eth(self.maxGas)
             if chek == False:
                 return 0

             tx = self.client.send_transaction(
                to=contract_spacefi,
                data= contract.encodeABI('swapExactETHForTokens',
                                         args=(
                                             min_to_amount.Wei,
                                             ['0x5300000000000000000000000000000000000004', contract_token],
                                             self.client.address,
                                             int(time.time()) + random.randint(1180, 1185),
                                         )),
                value=amount.Wei
            )

             await asyncio.sleep(5)
             verify = self.client.verif_tx(tx)
             if verify == False:
                 retry+=1
                 if retry < 5:
                    print(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    logger.error(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    print('Time sleep 20 seconds')
                    await asyncio.sleep(20)
                    await self.swap_eth_to_token(amount, contract_token, retry)

                 else:
                     print(f"ERROR SWAP")
                     logger.error(f"{self.client.address} | ERROR SWAP")
                     return 0

        except TransactionNotFound:
            print(f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            logger.error(f'{self.client.address} | The transaction has not been remembered for a long period of time, trying again')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            await self.swap_eth_to_token(amount, contract_token, retry)

        except ConnectionError:
            print(f'{self.client.address} | Internet connection error or problems with the RPC')
            logger.error(f'{self.client.address} | Internet connection error or problems with the RPC')
            await asyncio.sleep(120)
            print('Time sleep 120 seconds')
            retry += 1
            if retry > 5:
                return 0
            await self.swap_eth_to_token(amount, contract_token, retry)

        except Exception as error:
            print(f"{self.client.address} | Unknown Error:  {error}")
            logger.error(f'{self.client.address} | Unknown Error:  {error}')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            await self.swap_eth_to_token(amount, contract_token, retry)

    async def swap_token_to_eth(self, contract_token: str, amount: Optional[TokenAmount] = None, retry=0, slippage=0.1):
        balance_value = self.client.balance_of(contract_address=contract_token).Wei
        if amount == None:
            value = TokenAmount(
                amount=balance_value,
                decimals=self.client.get_decimals(contract_token),
                wei=True
            )
        else:
            value = amount

        print(f"{self.client.address} | SpaceFi Swap | {format(float(value.Ether), '.5f')} {self.client.name(contract_token)} --> ETH...")
        logger.info(f"{self.client.address} | SpaceFi Swap | {format(float(value.Ether), '.5f')} {self.client.name(contract_token)} --> ETH...")
        try:
            chek = chek_gas_eth(self.maxGas)
            if chek == False:
                return 0
            res = self.client.approve_interface(
                token_address=contract_token,
                spender=contract_spacefi,
                amount=value
            )
            if res == False:
                retry +=1
                print(f'{self.client.address} | Unsuccessfull approve! Try one more time')
                logger.error(f'{self.client.address} | Unsuccessfull approve! Try one more time')
                await asyncio.sleep(10)
                if retry < 5:
                    res = self.client.approve_interface(
                        token_address=contract_token,
                        spender=contract_spacefi,
                        amount=value
                    )

        except Exception as error:
            print(f'{self.client.address} | ERROR IN APROVE! -- > {error}')
            logger.error(f'{self.client.address} | ERROR IN APROVE! -- > {error}')
            return False

        await asyncio.sleep(10)

        try:
            contract = self.client.w3.eth.contract(address=contract_spacefi, abi=SpaceFi.abi)
            eth_price = self.client.get_eth_price()
            if (contract_token == contract_WBTC):
                btc_price = self.client.get_eth_price("WBTC")
                min_amount = (float(value.Ether) * btc_price) / eth_price * (1 - slippage / 100)
            else:
                min_amount = float(value.Ether) / eth_price * (1 - slippage / 100)

            min_to_amount = TokenAmount(
                amount= min_amount,
            )

            chek = chek_gas_eth(self.maxGas)
            if chek == False:
                return 0
            tx = self.client.send_transaction(
                to=contract_spacefi,
                data=contract.encodeABI('swapExactTokensForETH',
                                        args=(
                                            value.Wei,
                                            min_to_amount.Wei,
                                            [contract_token, '0x5300000000000000000000000000000000000004'],
                                            self.client.address,
                                            int(time.time()) + random.randint(1180, 1185),
                                        )),
                value=0,
            )
            await asyncio.sleep(5)
            verify = self.client.verif_tx(tx)
            if verify == False:
                retry += 1
                if retry < 5:
                    print(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    logger.error(f"{self.client.address} | Error. Try one more time {retry} / 5")
                    print('Time sleep 20 seconds')
                    await asyncio.sleep(20)
                    await self.swap_token_to_eth(contract_token, retry=retry)

                else:
                    print(f"ERROR SWAP")
                    logger.error(f"{self.client.address} | ERROR SWAP")
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
            await self.swap_token_to_eth(contract_token, retry=retry)

        except ConnectionError:
            print(f'{self.client.address} | Internet connection error or problems with the RPC')
            logger.error(f'{self.client.address} | Internet connection error or problems with the RPC')
            await asyncio.sleep(120)
            print('Time sleep 120 seconds')
            retry += 1
            if retry > 5:
                return 0
            await self.swap_token_to_eth(contract_token, retry=retry)

        except Exception as error:
            print(f"{self.client.address} | Unknown Error:  {error} \n Mayber not Gas")
            logger.error(f'{self.client.address} | Unknown Error:  {error}')
            print('Time sleep 120 seconds')
            await asyncio.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            await self.swap_token_to_eth(contract_token, retry=retry)

    async def AllStableSell(self):
        print(f"{self.client.address} | SpaceFi AllStableSell...")
        logger.info(f"{self.client.address} | SpaceFi AllStableSell...")
        try:
            if (self.client.balance_of(contract_USDC).Ether > 0.5):
                await self.swap_token_to_eth(contract_USDC)
            await asyncio.sleep(5)
            if (self.client.balance_of(contract_USDT).Ether > 0.5):
                await self.swap_token_to_eth(contract_USDT)
            await asyncio.sleep(5)
            if (self.client.balance_of(contract_WBTC).Ether > 0.5):
                await self.swap_token_to_eth(contract_WBTC)
        except Exception as error:
            print(f"{self.client.address} | Error AllStableSell: {error}")
            logger.error(f"{self.client.address} | Error AllStableSell: {error}")
