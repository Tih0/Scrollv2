from utils.getBalance import getBalance, getBalanceForNetwork
from utils.ambient import Ambient
from utils.spaceFi import SpaceFi
from utils.owlto import Owlto
from utils.official_bridge import OfficialBridge
from utils.networks import Scroll, Arbitrum, Optimism, ZKSync, Base, Ethereum
from utils.orbiter import Orbiter
from utils.nft import NFT
from client import Client, TokenAmount, logger
from config import maxGas, delay_min, delay_max, amount_min, amount_max, everybody, numberCircles, useProxy, network, stayBalance
from utils.skydrome import Skydrome
from utils.contracts import contract_USDT, contract_USDC, contractsZKStars, contractNFTs
from utils.zkstars import ZkStars
import time, sys
import asyncio, random
from utils.okx import okx_withdraw


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
    print()


clientsScroll = []
clientsArbitrum = []
clientsOptimism = []
clientsBase = []
clientsZKsync = []
clientsEthereum = []
clientsAmbient = []
clientsZkStars = []
clientsOrbiter = []
clientsSkydrome = []
clientsNFT = []
clientsOwlto = []
clientsOfficialBridge = []
clientsOrbiterScroll = []
clientsSpaceFi = []
addresses = []
proxy = []
okx_addresses = []
listToken = [contract_USDC, contract_USDT]

with open('addresses.txt', 'r') as f:
    for i in f:
        addresses.append(i)

with open('okxAddresses.txt', 'r') as f:
    for i in f:
        okx_addresses.append(i.strip())

with open('proxy.txt', 'r') as f:
    for i in f:
        proxy.append(i)

count = len(addresses)

for i in range(count):
    if useProxy == True:
        clientsScroll.append(Client(addresses[i].strip(), Scroll, proxy= proxy[i].strip()))
        clientsArbitrum.append(Client(addresses[i].strip(), Arbitrum, proxy= proxy[i].strip()))
        clientsOptimism.append(Client(addresses[i].strip(), Optimism, proxy= proxy[i].strip()))
        clientsZKsync.append(Client(addresses[i].strip(), ZKSync, proxy= proxy[i].strip()))
        clientsBase.append(Client(addresses[i].strip(), Base, proxy= proxy[i].strip()))
        clientsEthereum.append(Client(addresses[i].strip(), Ethereum, proxy= proxy[i].strip()))
    else:
        clientsScroll.append(Client(addresses[i].strip(), Scroll))
        clientsArbitrum.append(Client(addresses[i].strip(), Arbitrum))
        clientsOptimism.append(Client(addresses[i].strip(), Optimism))
        clientsZKsync.append(Client(addresses[i].strip(), ZKSync))
        clientsBase.append(Client(addresses[i].strip(), Base))
        clientsEthereum.append(Client(addresses[i].strip(), Ethereum))

for i in range(count):
    clientsZkStars.append(ZkStars(clientsScroll[i], maxGas))
    clientsAmbient.append(Ambient(clientsScroll[i], maxGas))
    clientsSkydrome.append(Skydrome(clientsScroll[i], maxGas))
    clientsSpaceFi.append((SpaceFi(clientsScroll[i], maxGas)))
    clientsNFT.append(NFT(clientsScroll[i], maxGas))
    clientsOrbiterScroll.append(Orbiter(clientsScroll[i], maxGas))
    clientsOfficialBridge.append(OfficialBridge(clientsEthereum[i], maxGas))
    if network == "Arbitrum One":
        clientsOrbiter.append(Orbiter(clientsArbitrum[i], maxGas))
        clientsOwlto.append(Owlto(clientsArbitrum[i], maxGas))
    elif network == "zkSync":
        clientsOrbiter.append(Orbiter(clientsZKsync[i], maxGas))
        clientsOwlto.append(Owlto(clientsZKsync[i], maxGas))
    elif network == "Optimism":
        clientsOrbiter.append(Orbiter(clientsOptimism[i], maxGas))
        clientsOwlto.append(Owlto(clientsOptimism[i], maxGas))
    elif network == "Base":
        clientsOrbiter.append(Orbiter(clientsBase[i], maxGas))
        clientsOwlto.append(Owlto(clientsBase[i], maxGas))
    elif network == "Ethereum":
        clientsOrbiter.append(Orbiter(clientsEthereum[i], maxGas))
        clientsOwlto.append(Owlto(clientsEthereum[i], maxGas))

def toOkx(clientsBase: Client, clientsScroll: Client, retry = 0):
    try:
        stayBalanceAmount = TokenAmount(0.0001)
        balance = clientsBase.w3.eth.get_balance(clientsScroll.address) - stayBalanceAmount.Wei
        tx = clientsBase.send_transaction(to=okx_addresses, eip1559=True, value=balance)
        time.sleep(5)
        verify = clientsBase.verif_tx(tx)
        if verify == False:
            retry += 1
            if retry < 5:
                print(f"{clientsBase.address} | Error. Try one more time {retry} / 5")
                logger.error(f"{clientsBase.address} | Error. Try one more time {retry} / 5")
                print('Time sleep 20 seconds')
                time.sleep(20)
                toOkx(clientsBase, clientsScroll, retry=retry)

            else:
                print(f"ERROR SWAP")
                logger.error(f"{clientsBase.address} | ERROR SWAP")
                return 0

    except ConnectionError:
            print(f'{clientsBase.address} | Internet connection error or problems with the RPC')
            logger.error(f'{clientsBase.address} | Internet connection error or problems with the RPC')
            time.sleep(120)
            print('Time sleep 120 seconds')
            retry += 1
            if retry > 5:
                return 0
            toOkx(clientsBase, clientsScroll, retry=retry)

    except Exception as error:
            print(f"{clientsBase.address} | Unknown Error:  {error} \n Mayber not Gas")
            logger.error(f'{clientsBase.address} | Unknown Error:  {error}')
            print('Time sleep 120 seconds')
            time.sleep(120)
            retry += 1
            if retry > 5:
                return 0
            toOkx(clientsBase, clientsScroll, retry=retry)

async def ZKStar():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsZkStars[i].mintZkStars(random.choice(contractsZKStars))))
    await asyncio.gather(*task)
async def AmbientEverybody():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsAmbient[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)), random.choice(listToken))))
    await asyncio.gather(*task)
async def AmbientEverybodyStableSwap():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsAmbient[i].swap_token_to_eth(random.choice(listToken))))
    await asyncio.gather(*task)
async def SkydromeEverybody():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsSkydrome[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)), random.choice(listToken))))
    await asyncio.gather(*task)
async def SkydromeEverybodyStableSwap():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsSkydrome[i].swap_token_to_eth(random.choice(listToken))))
    await asyncio.gather(*task)

async def SpaceFiEverybody():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsSpaceFi[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)), random.choice(listToken))))
    await asyncio.gather(*task)
async def SpaceFiEverybodyStableSwap():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsSpaceFi[i].swap_token_to_eth(random.choice(listToken))))
    await asyncio.gather(*task)
async def randomAllStableSell():
    task = []
    for i in range(count):
        swapalka = random.randint(1, 3)
        if swapalka == 1:
            task.append(asyncio.create_task(clientsAmbient[i].AllStableSell()))
        elif swapalka == 2:
            task.append(asyncio.create_task(clientsSkydrome[i].AllStableSell()))
        else:
            task.append(asyncio.create_task(clientsSpaceFi[i].AllStableSell()))
    await asyncio.gather(*task)
async def OnchainPower():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsNFT[i].mintOnchainPower()))
    await asyncio.gather(*task)
async def Zerius():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsNFT[i].mintZerius()))
    await asyncio.gather(*task)

async def AmbientSellAllStable():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsAmbient[i].AllStableSell()))
    await asyncio.gather(*task)

async def SkydromeSellAllStable():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsSkydrome[i].AllStableSell()))
    await asyncio.gather(*task)
async def Nft():
    task = []
    for i in range(count):
        task.append(asyncio.create_task(clientsNFT[i].mintNFT(random.choice(contractNFTs))))
    await asyncio.gather(*task)

async def withdrawBase():
    task = []
    for i in range(count):
        stayBalanceAmount = TokenAmount(stayBalance + 0.0001)
        balance = clientsScroll[i].w3.eth.get_balance(clientsScroll[i].address) - stayBalanceAmount.Wei
        task.append(asyncio.create_task(clientsOrbiterScroll[i].withdrawToNetwork(TokenAmount(balance, wei= True))))
    await asyncio.gather(*task)




def menu():
    print('1. Вывод с OKX на все кошельки')
    print('2. Вывод с OKX на все кошельки + Orbiter Finance Bridge')
    print('3. Вывод с OKX на все кошельки + Owlto Bridge')
    print('4. Вывод с OKX на все кошельки + OFFICIAL Bridge')
    print('5. Отдельно Orbiter Finance Bridge')
    print('6. Отдельно Owlto Bridge')
    print('7. Отдельно Official Bridge')
    print('8. Случайный Swap + обратный Swap')
    print('9. Swap Ambient')
    print('10. Swap Skydrome')
    print('11. Swap SpaceFi')
    print('12. Обмен стейблов на Ambient (обратный свап)')
    print('13. Обмен стейблов на Skydrome (обратный свап)')
    print('14. Обмен стейблов на SpaceFi (обратный свап)')
    print('15. Обмен всех стейблкоинов (Ambient/Skydrome - случайный выбор)')
    print('16. Mint ZkStars')
    print("17. Mint NFT Onchain power from Scroll")
    print("18. Mint NFT Zerius")
    print("19. Mint случайной NFT (10 отдельных различных NFT)")
    print('20. Вывод OKX + Orbiter/Owlto Bridge (случайный выбор) + случайное действие (mint, swap) + Обратно на OKX')
    print("21. Баланс в определенной сети")
    print("22. Баланс в сети Scroll")
    print('23. Вывод ETH на OKX')
    print('0. Выход')
    print('------------------------------------------------')
    print('Введи номер действия...')
    v = int(input())
    k = 0
    match(v):
        case 1:
            while (k < numberCircles):
                for i in range(count):
                    okx_withdraw(clientsScroll[i].address, amount_to_withdrawal=round(random.uniform(amount_min, amount_max), 5), wallet_number=i)
                    timesleep = random.randint(delay_min, delay_max)
                    if i + 1 == count and k + 1 < numberCircles: break
                    show_progress(timesleep)
                k+=1
        case 2:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    okx_withdraw(clientsScroll[i].address, amount_to_withdrawal=bramount, wallet_number=i)
                    print("Ожидаем подтверждения с биржи...")
                    time.sleep(120)
                    clientsOrbiter[i].bridge(amount=TokenAmount(bramount - 0.0006))
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1

        case 3:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    okx_withdraw(clientsScroll[i].address, amount_to_withdrawal=bramount, wallet_number=i)
                    print("Ожидаем подтверждения с биржи...")
                    time.sleep(120)
                    clientsOwlto[i].bridge(amount=TokenAmount(bramount- 0.0006))
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1

        case 4:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    okx_withdraw(clientsScroll[i].address, amount_to_withdrawal=bramount, wallet_number=i)
                    print("Ожидаем подтверждения с биржи...")
                    time.sleep(120)
                    clientsOfficialBridge[i].bridge(amount=TokenAmount(bramount- 0.0006))
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1
        case 5:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    clientsOrbiter[i].bridge(amount=TokenAmount(bramount- 0.0006))
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1
        case 6:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    clientsOwlto[i].bridge(amount=TokenAmount(bramount- 0.0006))
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1

        case 7:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    clientsOfficialBridge[i].bridge(amount=TokenAmount(bramount- 0.0006))
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1

        case 8:
            while (k < numberCircles):
                for i in range(count):
                    swapalka = random.randint(1, 3)
                    if swapalka == 1:
                        if everybody == True:
                            asyncio.run(AmbientEverybody())
                            timesleep = random.randint(delay_min, delay_max)
                            show_progress(timesleep)
                            asyncio.run(AmbientEverybodyStableSwap())
                        else:
                            for i in range(count):
                                contract_token = random.choice(listToken)
                                asyncio.run(clientsAmbient[i].swap_eth_to_token(
                                    TokenAmount(random.uniform(amount_min, amount_max)), contract_token=contract_token))
                                timesleep = random.randint(delay_min, delay_max)
                                show_progress(timesleep)
                                asyncio.run(clientsAmbient[i].swap_token_to_eth(contract_token))

                    if swapalka == 2:
                        if everybody == True:
                            asyncio.run(SkydromeEverybody())
                            timesleep = random.randint(delay_min, delay_max)
                            show_progress(timesleep)
                            asyncio.run(SkydromeEverybodyStableSwap())
                        else:
                            for i in range(count):
                                contract_token = random.choice(listToken)
                                asyncio.run(clientsSkydrome[i].swap_eth_to_token(
                                    TokenAmount(random.uniform(amount_min, amount_max)),
                                    contract_token=contract_token))
                                timesleep = random.randint(delay_min, delay_max)
                                show_progress(timesleep)
                                asyncio.run(clientsSkydrome[i].swap_token_to_eth(contract_token))

                    else:
                        if everybody == True:
                            asyncio.run(SpaceFiEverybody())
                            timesleep = random.randint(delay_min, delay_max)
                            show_progress(timesleep)
                            asyncio.run(SpaceFiEverybodyStableSwap())
                        else:
                            for i in range(count):
                                contract_token = random.choice(listToken)
                                asyncio.run(clientsSpaceFi[i].swap_eth_to_token(
                                    TokenAmount(random.uniform(amount_min, amount_max)),
                                    contract_token=contract_token))
                                timesleep = random.randint(delay_min, delay_max)
                                show_progress(timesleep)
                                asyncio.run(clientsSpaceFi[i].swap_token_to_eth(contract_token))

                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k += 1

        case 9:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(AmbientEverybody())
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                    asyncio.run(AmbientEverybodyStableSwap())
                else:
                    for i in range(count):
                        contract_token = random.choice(listToken)
                        asyncio.run(clientsAmbient[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)), contract_token=contract_token))
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                        asyncio.run(clientsAmbient[i].swap_token_to_eth(contract_token))
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 10:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(SkydromeEverybody())
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                    asyncio.run(SkydromeEverybodyStableSwap())
                else:
                    for i in range(count):
                        contract_token = random.choice(listToken)
                        asyncio.run(clientsSkydrome[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)),
                                                                        contract_token=contract_token))
                        timesleep = random.randint(delay_min, delay_max)
                        asyncio.run(clientsSkydrome[i].swap_token_to_eth(contract_token))
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 11:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(SpaceFiEverybody())
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                    asyncio.run(SpaceFiEverybodyStableSwap())
                else:
                    for i in range(count):
                        contract_token = random.choice(listToken)
                        asyncio.run(clientsSpaceFi[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)),
                                                                         contract_token=contract_token))
                        timesleep = random.randint(delay_min, delay_max)
                        asyncio.run(clientsSpaceFi[i].swap_token_to_eth(contract_token))
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 12:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(AmbientEverybodyStableSwap())
                else:
                    for i in range(count):
                        asyncio.run(clientsAmbient[i].AllStableSell())
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 13:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(SkydromeEverybodyStableSwap())
                else:
                    for i in range(count):
                        asyncio.run(clientsSkydrome[i].AllStableSell())
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 14:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(SpaceFiEverybodyStableSwap())
                else:
                    for i in range(count):
                        asyncio.run(clientsSpaceFi[i].AllStableSell())
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 15:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(randomAllStableSell())
                else:
                    for i in range(count):
                        swapalka = random.randint(1, 3)
                        if swapalka == 1:
                            asyncio.run(clientsAmbient[i].AllStableSell())
                        elif swapalka == 2:
                            asyncio.run(clientsSkydrome[i].AllStableSell())
                        else:
                            asyncio.run(clientsSpaceFi[i].AllStableSell())
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 16:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(ZKStar())
                    show_progress(random.randint(delay_min, delay_max))
                else:
                    for i in range(count):
                        asyncio.run(clientsZkStars[i].mintZkStars(contractsZKStars[random.randint(0, 19)]))
                        if i + 1 == count and k + 1 == numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1
            menu()
        case 17:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(OnchainPower())
                    show_progress(random.randint(delay_min, delay_max))
                else:
                    for i in range(count):
                        asyncio.run(clientsNFT[i].mintOnchainPower())
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1

        case 18:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(Zerius())
                    show_progress(random.randint(delay_min, delay_max))
                else:
                    for i in range(count):
                        asyncio.run(clientsNFT[i].mintZerius())
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1
        case 19:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(Nft())
                    show_progress(random.randint(delay_min, delay_max))
                else:
                    for i in range(count):
                        asyncio.run(clientsNFT[i].mintNFT(random.choice(contractNFTs)))
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1
        case 20:
            while (k < numberCircles):
                for i in range(count):
                    bramount = round(random.uniform(amount_min, amount_max), 5)
                    okx_withdraw(clientsScroll[i].address, amount_to_withdrawal=bramount, wallet_number=i)
                    print('Ожидаем вывода...')
                    time.sleep(60)
                    choice = random.randint(1,2)
                    if choice == 1:
                        clientsOrbiter[i].bridge(TokenAmount(bramount))
                    else:
                        clientsOwlto[i].bridge(TokenAmount(bramount))
                    print('Ожидаем бридж...')
                    time.sleep(60)
                    choice = random.randint(1, 2)
                    if choice == 1:
                        swapalka = random.randint(1, 3)
                        if swapalka == 1:
                            contract_token = random.choice(listToken)
                            asyncio.run(clientsAmbient[i].swap_eth_to_token(TokenAmount(random.uniform(amount_min, amount_max)),contract_token=contract_token))
                            timesleep = random.randint(delay_min, delay_max)
                            show_progress(timesleep)
                            asyncio.run(clientsAmbient[i].swap_token_to_eth(contract_token))

                        if swapalka == 2:
                            contract_token = random.choice(listToken)
                            asyncio.run(clientsSkydrome[i].swap_eth_to_token(
                                TokenAmount(random.uniform(amount_min, amount_max)),
                                contract_token=contract_token))
                            timesleep = random.randint(delay_min, delay_max)
                            show_progress(timesleep)
                            asyncio.run(clientsSkydrome[i].swap_token_to_eth(contract_token))
                        else:
                            contract_token = random.choice(listToken)
                            asyncio.run(clientsSpaceFi[i].swap_eth_to_token(
                                TokenAmount(random.uniform(amount_min, amount_max)),
                                contract_token=contract_token))
                            timesleep = random.randint(delay_min, delay_max)
                            show_progress(timesleep)
                            asyncio.run(clientsSpaceFi[i].swap_token_to_eth(contract_token))
                    else:
                        collection = random.randint(1,3)
                        if collection == 1:
                            asyncio.run(clientsNFT[i].mintZerius())
                        elif collection == 2:
                            asyncio.run(clientsZkStars[i].mintZkStars(contractsZKStars[random.randint(0, 19)]))
                        else:
                            asyncio.run(clientsNFT[i].mintNFT(random.choice(contractNFTs)))

                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                    stayBalanceAmount = TokenAmount(stayBalance + 0.0001)
                    balance = clientsScroll[i].w3.eth.get_balance(clientsScroll[i].address) - stayBalanceAmount.Wei
                    asyncio.run(clientsOrbiterScroll[i].withdrawToNetwork(balance))
                    print('Ожидаем превод в Base...')
                    time.sleep(60)
                    toOkx(clientsBase[i], clientsScroll[i])
                    if i + 1 == count and k + 1 < numberCircles: break
                    timesleep = random.randint(delay_min, delay_max)
                    show_progress(timesleep)
                k+=1

        case 21:
            l = 0
            while l > 5 or l < 1:
                print("Баланс какой сети вы хотите посмотреть:")
                print("1. Arbitrum One")
                print("2. zkSync")
                print("3. Optimism")
                print("4. Base")
                print("5. Ethereum")
                l = int(input())
            if l == 1:
                getBalanceForNetwork(clientsArbitrum, count)
            elif l == 2:
                getBalanceForNetwork(clientsZKsync, count)
            elif l == 3:
                getBalanceForNetwork(clientsOptimism, count)
            elif l == 4:
                getBalanceForNetwork(clientsBase, count)
            else:
                getBalanceForNetwork(clientsEthereum, count)
            print("Нажмите Enter, чтобы выйти в меню")
            vim = input()
            menu()

        case 22:
            getBalance(clientsScroll, count, True)
            print("Нажмите Enter, чтобы выйти в меню")
            vim = input()
            menu()
        case 23:
            while (k < numberCircles):
                if everybody == True:
                    asyncio.run(withdrawBase())
                    print("Ожидания вывода в сеть Base...")
                    time.sleep(60)
                    for i in range(count):
                        toOkx(clientsBase[i], clientsScroll[i])
                    show_progress(random.randint(delay_min, delay_max))
                else:
                    for i in range(count):
                        stayBalanceAmount = TokenAmount(stayBalance + 0.0001)
                        balance = clientsScroll[i].w3.eth.get_balance(clientsScroll[i].address) - stayBalanceAmount.Wei
                        asyncio.run(clientsOrbiterScroll[i].withdrawToNetwork(balance))
                        print('Ожидаем превод в Base...')
                        time.sleep(60)
                        toOkx(clientsBase[i], clientsScroll[i])
                        if i + 1 == count and k + 1 < numberCircles: break
                        timesleep = random.randint(delay_min, delay_max)
                        show_progress(timesleep)
                k+=1
        case 0:
            pass

menu()