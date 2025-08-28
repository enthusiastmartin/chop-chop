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
@click.argument('asset_ids', nargs=-1, required=True, type=click.IntRange(min=1))
@click.option('--has-farms/--no-has-farms', default=False, help='Flag to indicate if farms are present')
def remove_positions(asset_ids, has_farms):
    """Remove positions command with mandatory asset IDs and optional has_farms flag."""
    click.echo(f"🚀 Captain's log: Engaging warp drive to remove positions for asset IDs: {list(asset_ids)}")
    click.echo(f"🔧 Engineering report: Dilithium crystals configured with has_farms={has_farms}")
    click.echo("📡 Communications: Hailing frequencies open, preparing photon torpedo removal calls...")
    client = initialize_network_client()
    click.echo(f"✅ Helm: Successfully docked with starbase {client.api.chain}")
    omnipool = Omnipool(client)
    uniques = Uniques(client)
    utility = Utility(client)
    omnipool_wlm = OmnipoolWLM(client)
    omnipool_lm = OmnipoolLM(client)
    scheduler = Scheduler(client)

    dispatch_as_calls = []
    future_omni_pos_owners = {}

    split_size = 20

    # Process positions for provided asset IDs
    for asset_id in asset_ids:
        deposit_positions = omnipool_wlm.get_deposit_positions(asset_id)
        click.echo(f"🔍 Sensors: Long-range scanners detect {len(deposit_positions)} Klingon deposit positions on asset {asset_id}")

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

    click.echo("🔄 Science Officer: Analyzing quantum flux in omnipool nebula for all assets...")
    positions = omnipool.retrieve_positions()
    l = []
    for key, value in positions.items():
        if value.asset_id in asset_ids:
            l.append((key, value.shares))

    click.echo(f"📊 Data: Computing... {len(l)} hostile positions identified matching your tactical parameters")

    entries = []

    remove_liquidity_calls = []

    click.echo("⚡ Tactical: Charging phaser arrays for liquidity removal sequence...")

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

    click.echo("\n🎉 Mission accomplished! The Borg have been defeated. Here's your encoded subspace transmission:")
    click.echo("" + "="*50)
    # Batch all schedule calls in one force_batch call
    final_batch_call = utility.create_force_batch(schedule_calls)
    click.echo(final_batch_call.encode())
    click.echo("" + "="*50)
    click.echo("✨ Captain, all systems are nominal. Permission to engage and transmit to the network, sir!")
    client.api.close()

