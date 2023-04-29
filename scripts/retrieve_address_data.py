from dotenv import load_dotenv
from ens import ENS
import os
from web3 import Web3


load_dotenv()
ALCHEMY_KEY    = os.environ['ALCHEMY_KEY']
ALCHEMY_KEY_OP = os.environ['ALCHEMY_KEY_OP']

# create a web3 connection
alchemy_url = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"
w3 = Web3(Web3.HTTPProvider(alchemy_url))
ns = ENS.fromWeb3(w3)
op = Web3(Web3.HTTPProvider(f"https://opt-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"))

# get hex codes for checking address/wallet types
SPLITS_CODE = w3.eth.get_code("0xD2584c1CF7E3fF11957195732d380DC886F5f05b")
EOA_CODE = w3.eth.get_code("0xEAF9830bB7a38A3CEbcaCa3Ff9F626C424F3fB55")

SAFES = [w3.eth.get_code(Web3.toChecksumAddress(x.lower())) for x in [
         "0x4D9339dd97db55e3B9bCBE65dE39fF9c04d1C2cd", 
         "0x7DAC9Fc15C1Db4379D75A6E3f330aE849dFfcE18"]]


def get_ens(addr):
    try:
        return ns.name(addr)
    except:
        return None


def get_address_type(addr):

    try:
        code = w3.eth.get_code(addr)
    except:
        return "Unknown"
    if code == EOA_CODE:
        return "EOA"
    if code == SPLITS_CODE:
        return "0xSplits"
    if code in SAFES:
        return "Safe"
    print(code.hex())
    

def get_transaction_count(client, addr):
    try:
        return client.eth.get_transaction_count(addr)
    except:
        return None

def retrieve_address_data(address):
    
    try:
        addr = Web3.toChecksumAddress(address.lower())
    except:
        addr = address
        print(f"Checksum address {address} not found on Ethereum Mainnet.")

    result = dict(
        address=address,
        type=get_address_type(addr),
        ens=get_ens(addr),
        transaction_count=get_transaction_count(w3, addr),
        op_transaction_count=get_transaction_count(op, addr),
    )
    print("Success:", result)
    return result


if __name__ == "__main__":
    a = "0x4D9339dd97db55e3B9bCBE65dE39fF9c04d1C2cd"
    retrieve_address_data(a)
    #print(get_transaction_count(op, a))