from web3 import Web3
import json
import time
from abis import pancake_router

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))
print(web3.isConnected())

pcksw_router_address = '0x10ED43C718714eb63d5aA57B78B54704E256024E' # ADDRESS OF BLOCKCHAIN ROUTER FACILITATING THE SMART CONTRACT I AM CALLING
sender_address = '???' # MASKED: ID OF MY CRYPTOCURRENCY WALLET

balance = web3.eth.get_balance(sender_address)
conv_bal = web3.fromWei(balance, 'ether')
print(conv_bal)

contract = web3.eth.contract(address = pcksw_router_address, abi = pancake_router)

tokentobuy = web3.toChecksumAddress('0x79eBC9A2ce02277A4b5b3A768b1C0A4ed75Bd936') 
tokentospend = web3.toChecksumAddress('0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82') 
trans_cnt = web3.eth.get_transaction_count(sender_address)
start = time.time()

curr_trans = contract.functions.swapExactTokensForTokens(
    web3.toWei(0.64, 'ether'), 0, [tokentospend, tokentobuy], sender_address, int(time.time() + 100000)).buildTransaction({
        'from' : sender_address, 'gas' : 200000, 'gasPrice' : web3.toWei('5', 'gwei'), 'nonce' : trans_cnt})

signed_trans = web3.eth.account.sign_transaction(curr_trans, '???') # MASKED: ID REQUIRED FOR SIGNING MY TRANSACTIONS
trans_token = web3.eth.send_raw_transaction(signed_trans.rawTransaction)
print(web3.toHex(trans_token))