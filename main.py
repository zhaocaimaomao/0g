###
# @Author: 招財猫猫
# @Date: 2024-05-01
# @LastEditTime: 2024-05-01
# @Description: 这是0g的交互脚本，分别上传文件、部署合约和给自己转账，这个脚本上传的是一个内容为0g的txt文件
###

from functions import *
import pandas as pd
from web3 import Web3
import time

input_file_path = r'~/0g/0g_exsample.csv'
df = pd.read_csv(input_file_path)
num_process = list(range(0, 10000))
with open(r'1_Storage_ABI.json', 'r') as f:
    abi = json.load(f)

if 'Upload' not in df.columns:
    df['Upload'] = None
if 'Deploy' not in df.columns:
    df['Deploy'] = None
if 'Transfer' not in df.columns:
    df['Transfer'] = None
for i in num_process:
    try:
        address = df['Address'][i]
        address_without_0x = address.split('x')[1]
        private_key = df['Private_Key'][i]
        network_config = load_network('0g')
        w3 = Web3(Web3.HTTPProvider(network_config.http_rpc))
        if pd.isna(df['Upload'][i]):
            print(i)
            transact_with_input(
                web3=w3,
                from_addr=address,
                private_key=private_key,
                to_addr='0x22C1CaF8cbb671F220789184fda68BfD7eaA2eE1',
                val_in_eth=0.000000596046447753,
                input_data='0xef3e12dc000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000060000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001b069294b86f8a3541ec25ca922d4c7f1f3e2053395108d3e1d249d23fc5c22cc0000000000000000000000000000000000000000000000000000000000000000',
                gas_params=cal_gas_params(w3, 0.2)
            )
            df.loc[i, 'Upload'] = 1
            print(i, 'Uploaded')
        if df['Upload'][i] == 1 and pd.isna(df['Deploy'][i]):
            print(i)
            create_contract(
                web3=w3,
                from_addr=address,
                private_key=private_key,
                abi=abi,  # MyToken_ABI.json
                bytecode='608060405234801561001057600080fd5b50610150806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80632e64cec11461003b5780636057361d14610059575b600080fd5b610043610075565b60405161005091906100d9565b60405180910390f35b610073600480360381019061006e919061009d565b61007e565b005b60008054905090565b8060008190555050565b60008135905061009781610103565b92915050565b6000602082840312156100b3576100b26100fe565b5b60006100c184828501610088565b91505092915050565b6100d3816100f4565b82525050565b60006020820190506100ee60008301846100ca565b92915050565b6000819050919050565b600080fd5b61010c816100f4565b811461011757600080fd5b5056fea264697066735822122040f116908b19cc0084646af6dc209d324dcccc2da9f8c6cb38a44b15cca3cf3e64736f6c63430008070033',
                gas_params=cal_gas_params(w3, 0.2)
            )
            df.loc[i, 'Deploy'] = 1
            print(i, 'Deployed')
        if df['Deploy'][i] == 1 and pd.isna(df['Transfer'][i]):
            print(i)
            transact_with_input(
                web3=w3,
                from_addr=address,
                private_key=private_key,
                to_addr=address,
                val_in_eth=0.5,
                input_data='',
                gas_params=cal_gas_params(w3, 0.2)
            )
            df.loc[i, 'Transfer'] = 1
            print(i, 'Transfer')
    except Exception as e:
        df.loc[i, 'Error_Logs'] = e
        print(e)
        time.sleep(3)
        continue
    finally:
        df.to_csv(input_file_path, index=False)