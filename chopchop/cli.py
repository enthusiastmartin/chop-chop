import click

from chopchop.client import initialize_network_client
from chopchop.pallets.omnipool import Omnipool
from chopchop.pallets.omnipool_lm import OmnipoolWLM, OmnipoolLM
from chopchop.pallets.scheduler import Scheduler
from chopchop.pallets.uniques import Uniques
from chopchop.pallets.utility import Utility


@click.group()
def cli():
    """Chop-chop CLI utility."""
    pass


KILT_ID = 27
CFG_ID = 21

@cli.command()
@click.argument('position', type=click.IntRange(min=1))
@click.option('--has-farms/--no-has-farms', default=False, help='Flag to indicate if farms are present')
def remove_positions(position, has_farms):
    """Remove positions command with a mandatory positive number and optional has_farms flag."""
    click.echo(f"-- remove_positions executed with position={position}, has_farms={has_farms}")
    print(f"Preparing call to remove_positions for assets: {position}")
    client = initialize_network_client()
    print(f"Connected to: {client.api.chain}")
    omnipool = Omnipool(client)
    uniques = Uniques(client)
    utility = Utility(client)
    omnipool_wlm = OmnipoolWLM(client)
    omnipool_lm = OmnipoolLM(client)
    scheduler = Scheduler(client)

    dispatch_as_calls = []
    future_omni_pos_owners = {}

    split_size = 20

    # Process positions for both KILT_ID and CFG_ID
    for asset_id in [KILT_ID, CFG_ID]:
        deposit_positions = omnipool_wlm.get_deposit_positions(asset_id)
        print(f"Asset {asset_id} - found {len(deposit_positions)} deposit positions")

        for (deposit_id, farms) in deposit_positions:
            owner = uniques.query_owner(2584, deposit_id)
            farm_ids = []
            for farm in farms:
                farm_ids.append(farm["yield_farm_id"].value)
            call = omnipool_lm.create_exit_farm_call(deposit_id, farm_ids)
            dispatch_call = utility.create_dispatch_as_call(owner, call)
            dispatch_as_calls.append(dispatch_call)

            omni_pos = omnipool_lm.get_omnipool_position_id(deposit_id)
            future_omni_pos_owners[omni_pos] = owner

    sublists = []
    for i in range(0, len(dispatch_as_calls), split_size):
        sublists.append(dispatch_as_calls[i:i + split_size])

    # Create schedule calls for each sublist with increasing block delays
    schedule_calls = []
    for i, sublist in enumerate(sublists):
        force_batch_call = utility.create_force_batch(sublist)
        block_delay = i + 1  # 1,2,3
        schedule_call = scheduler.create_schedule_after_call(block_delay, force_batch_call)
        schedule_calls.append(schedule_call)

    print("Retrieving omnipool positions for all assets ... ")
    positions = omnipool.retrieve_positions()
    l = []
    for key, value in positions.items():
        if value.asset_id == KILT_ID or value.asset_id == CFG_ID:
            l.append((key, value.shares))

    print(f"{len(l)} positions retrieved")

    entries = []

    remove_liquidity_calls = []

    print("Preparing remove_liquidity_calls... ")

    for (position_id, shares) in l:
        if position_id in future_omni_pos_owners:
            owner = future_omni_pos_owners[position_id]
        else:
            owner = uniques.query_owner(1337, position_id)
        entry = {"owner": owner, "shares": shares, "id": position_id}
        entries.append(entry)
        call = omnipool.remove_liquidity_call(position_id, shares)
        dispatch_call = utility.create_dispatch_as_call(owner, call)
        remove_liquidity_calls.append(dispatch_call)

    subremovals = []
    # block delay should be after all previous delays
    for i in range(0, len(remove_liquidity_calls), split_size):
        subremovals.append(remove_liquidity_calls[i:i + split_size])

    start_delay = len(sublists) + 1
    for i, subremoval in enumerate(subremovals):
        force_batch_call = utility.create_force_batch(subremoval)
        block_delay = start_delay + (i + 1)
        schedule_call = scheduler.create_schedule_after_call(block_delay, force_batch_call)
        schedule_calls.append(schedule_call)

    print("Here is your encoded call, sir! Enjoy!\n\n")
    # Batch all schedule calls in one force_batch call
    final_batch_call = utility.create_force_batch(schedule_calls)
    print(final_batch_call.encode())
    client.api.close()

