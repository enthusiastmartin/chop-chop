import os
from dataclasses import dataclass

from substrateinterface import SubstrateInterface, Keypair
from substrateinterface.exceptions import SubstrateRequestException

@dataclass
class Client:
    api: SubstrateInterface

custom_type_registry = {
    "runtime_id": 1,
    "types": {
        "Address": "AccountId",
        "LookupSource": "AccountId",
        "Price": "u128",
        "AssetId": "u32",
        "Currency": "AssetId",
        "CurrencyId": "AssetId",
        "MultiLocation": "MultiLocationV1",
        "AssetNativeLocation": "MultiLocation",
        "AssetType": {"type": "enum", "value_list": ["Token", "ShareToken"]},
        "IntentionType": {"type": "enum", "value_list": ["SELL", "BUY"]},
        "IntentionId": "Hash",
    },
    "versioning": [],
}

karura_type_registry = {
    "runtime_id": 1,
    "types": {
        "Address": "MultiAddress",
        "LookupSource": "MultiAddress",
        "Price": "u128",
        "MultiLocation": "MultiLocationV1",
        "TokenSymbol": {
            "type": "enum",
            "value_list": {
                "ACA": 0,
                "KAR": 128,
                "KUSD": 129,
            },
        },
        "CurrencyId": {"type": "enum", "type_mapping": [["Token", "TokenSymbol"]]},
        "CurrencyIdOf": "CurrencyId",
        "AmountOf": "Balance",
        "IntentionType": {"type": "enum", "value_list": ["SELL", "BUY"]},
        "IntentionId": "Hash",
    },
    "versioning": [],
}

LOCAL_RPC = "ws://127.0.0.1:9988"
CHOPSTICKS = "http://127.0.0.1:8000"
HYDRA_MAINNET= "wss://hydration.ibp.network:443"
LARK1 = "https://1.lark.hydration.cloud"
LARK2 = "https://2.lark.hydration.cloud"
NICE = 'wss://rpc.nice.hydration.cloud:443'

RPC = HYDRA_MAINNET

NETWORK_MAP = {
    "mainnet": HYDRA_MAINNET,
    "lark1": LARK1,
    "lark2": LARK2,
    "nice": NICE,
    "local": LOCAL_RPC,
    "chopsticks": CHOPSTICKS,
}

def resolve_network_rpc(network: str | None = None, custom_rpc: str | None = None) -> str:
    """Resolve network parameter to RPC URL."""
    if custom_rpc:
        return custom_rpc
    if network and network in NETWORK_MAP:
        return NETWORK_MAP[network]
    return RPC

def initialize_network_client(r: str | None = None, network: str | None = None, custom_rpc: str | None = None) -> Client:
    rpc = r or resolve_network_rpc(network, custom_rpc)
    try:
        api = SubstrateInterface(
            url=rpc,
        )
    except ConnectionRefusedError as e:
        raise SubstrateRequestException(f"⚠️ Failed to connect to {rpc}") from e
    except Exception as e:
        raise RuntimeError(str(e)) from e

    return Client(api=api)


def root_origin(use_alice=False):
    if use_alice:
        return Keypair.create_from_uri("//Alice", ss58_format=63)

    DEVNET_ROOT = os.getenv("DEVNET_ROOT")

    return Keypair.create_from_mnemonic(DEVNET_ROOT, ss58_format=63)


def create_call(client, module, func, params):
    return client.api.compose_call(
        call_module=module, call_function=func, call_params=params
    )


def submit_extrinsic(client, sender, call, wait_for_inc=True):
    extrinsic = client.api.create_signed_extrinsic(
        call=call, keypair=sender, era={"period": 64}
    )

    receipt = client.api.submit_extrinsic(extrinsic, wait_for_inclusion=wait_for_inc)

    if wait_for_inc:
        print(f"Ex: {receipt.error_message}")
        return receipt.is_success


def create_and_submit_ex(client, sender, module, func, params, wait_for_inc=True):
    return submit_extrinsic(
        client,
        sender,
        create_call(client, module, func, params),
        wait_for_inc=wait_for_inc,
    )
