from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass
class DefaultABIs:
    """
    The default ABIs.
    """
    Token = [
        {
            'constant': True,
            'inputs': [],
            'name': 'name',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'totalSupply',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'decimals',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': 'who', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': '_owner', 'type': 'address'}, {'name': '_spender', 'type': 'address'}],
            'name': 'allowance',
            'outputs': [{'name': 'remaining', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': '_spender', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': 'approve',
            'outputs': [],
            'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': 'transfer',
            'outputs': [], 'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        }]


class TokenAmount:
    Wei: int
    Ether: Decimal
    decimals: int

    def __init__(self, amount: Union[int, float, str, Decimal], decimals: int = 18, wei: bool = False) -> None:
        if wei:
            self.Wei: int = amount
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

        self.decimals = decimals


class Network:
    def __init__(self,
                 name: str,
                 rpc: str,
                 chain_id: int,
                 eip1559_tx: bool,
                 coin_symbol: str,
                 explorer: str,
                 decimals: int = 18,
                 ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_tx = eip1559_tx
        self.coin_symbol = coin_symbol
        self.decimals = decimals
        self.explorer = explorer

    def __str__(self):
        return f'{self.name}'


Arbitrum = Network(
    name='Arbitrum One',
    rpc='https://rpc.ankr.com/arbitrum/',
    chain_id=42161,
    eip1559_tx=True,
    coin_symbol='ETH',
    explorer='https://arbiscan.io/tx/',
)

ZKSync = Network(
    name = 'zkSync',
    rpc = 'https://zksync.meowrpc.com',
    chain_id = 324 ,
    eip1559_tx = True,
    coin_symbol = 'ETH',
    explorer = 'https://explorer.zksync.io/tx/',

)
Optimism = Network(
    name='Optimism',
    rpc='https://rpc.ankr.com/optimism/',
    chain_id=10,
    eip1559_tx=True,
    coin_symbol='ETH',
    explorer='https://optimistic.etherscan.io/tx/',
)

Scroll = Network(
    name='Scroll',
    rpc='https://rpc.scroll.io',
    chain_id=534352,
    eip1559_tx=False,
    coin_symbol='ETH',
    explorer='https://scrollscan.com/tx/',
)

Base = Network(
    name='Base',
    rpc='https://base.drpc.org',
    chain_id=8453,
    eip1559_tx=True,
    coin_symbol='ETH',
    explorer='https://basescan.org/tx/',
)

Ethereum = Network(
    name= 'Ethereum',
    rpc= 'https://ethereum.publicnode.com',
    chain_id=1,
    eip1559_tx=True,
    coin_symbol='ETH',
    explorer='https://etherscan.io/tx/',
)