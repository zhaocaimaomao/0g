import json
import os.path
from hexbytes import HexBytes
from web3.gas_strategies.rpc import rpc_gas_price_strategy

USE_EIP1559 = False


def sign_and_send_txn(web3, transaction, private_key, estimate=False):
    # 兼容1559
    print(transaction)
    gas_limit_key = 'gas'

    if estimate or 'gas' not in transaction:
        gas_estimate = web3.eth.estimate_gas(transaction)
        gas_preset = transaction.get(gas_limit_key, 0)
        if gas_estimate > gas_preset:
            transaction[gas_limit_key] = gas_estimate
        elif gas_estimate < gas_preset:
            resp = input(f'你输入的gas({gas_preset})比预计的({gas_estimate})要高，是否使用推荐值？y/n')
            if resp.lower() == 'y':
                transaction[gas_limit_key] = gas_estimate
    signed_txn = web3.eth.account.sign_transaction(
        transaction, private_key=private_key
    )
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return HexBytes(tx_receipt["transactionHash"]).hex()


def cal_gas_params(web3, priority_fee, timeout=3):
    if USE_EIP1559:
        # use eip-1559
        block = web3.eth.get_block('latest')
        baseFeePerGas = block.get('baseFeePerGas', 0)
        maxFeePerGas = int(baseFeePerGas * (1.125 ** timeout) + web3.to_wei(priority_fee, 'GWEI'))
        return {
            "maxPriorityFeePerGas": web3.to_wei(priority_fee, 'GWEI'),
            "maxFeePerGas": maxFeePerGas,
        }
    else:
        # use traditional
        web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
        price = web3.eth.generate_gas_price()
        return {
            "gasPrice": price + web3.to_wei(priority_fee, 'GWei'),
        }


class BlockChainNetwork:
    def __init__(self, name, rpc, chainid, symbol='ETH', ws=None, apiurl='', **kwargs):
        self.name = name
        self.http_rpc = rpc
        self.symbol = symbol
        self.chain_id = int(chainid)
        self.api_url = apiurl
        self.wss = ws
        self.params = kwargs


def load_network(network_name='eth') -> BlockChainNetwork:
    networks_filename = os.path.join(os.path.dirname(__file__), 'networks.json')
    with open(networks_filename, 'r') as f:
        networks = json.load(f)
        for network in networks:
            if network['name'].lower() == network_name.lower():
                return BlockChainNetwork(**network)
        f.close()
    print(network_name, '没有定义', '请检查文件：')
    print(networks_filename)
    raise ValueError(f'{network_name} is not defined!')


def transact_with_input(
        web3, from_addr, private_key, to_addr, val_in_eth: float, input_data,
        gas_params=None):
    nonce = web3.eth.get_transaction_count(from_addr)
    if gas_params is None:
        gas_params = cal_gas_params(web3, 0.1)
    raw_txn = {
        'from': from_addr,
        'to': to_addr,
        'value': web3.to_wei(val_in_eth, 'ether'),
        **gas_params,
        'nonce': nonce,
        'data': input_data,
        'chainId': web3.eth.chain_id
    }
    sign_and_send_txn(web3, raw_txn, private_key=private_key, estimate=True)


def create_contract(
        web3, from_addr, private_key, abi, bytecode,
        gas_params=None
):
    nonce = web3.eth.get_transaction_count(from_addr)
    if gas_params is None:
        gas_params = cal_gas_params(web3, 0.2)
    contract = web3.eth.contract(abi=abi, bytecode=bytecode)
    transaction = contract.constructor().build_transaction({
        'from': from_addr,
        **gas_params,
        'nonce': nonce,
        'chainId': web3.eth.chain_id
    })

    sign_and_send_txn(web3, transaction, private_key=private_key, estimate=True)