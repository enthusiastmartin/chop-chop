import click

from chopchop.client import initialize_network_client
from chopchop.pallets.omnipool import Omnipool
from chopchop.pallets.omnipool_lm import OmnipoolWLM, OmnipoolLM
from chopchop.pallets.scheduler import Scheduler
from chopchop.pallets.uniques import Uniques
from chopchop.pallets.utility import Utility
from chopchop.pallets.circuit_breaker import CircuitBreaker
from chopchop.pallets.asset_registry import AssetRegistry
from substrateinterface.exceptions import SubstrateRequestException


@click.group()
def cli():
    """Chop-chop CLI utility."""
    pass


KILT_ID = 27
CFG_ID = 21

@cli.command()
@click.argument('asset_ids', nargs=-1, required=True, type=click.IntRange(min=1))
@click.option('--check-farms', default=True, help='Flag to indicate if farms are present')
@click.option('--remove-token', is_flag=True, help='Remove token from Omnipool after removing positions (also sets tradability to 0)')
@click.option('--lark1', 'network', flag_value='lark1', help='Connect to Lark1 network')
@click.option('--lark2', 'network', flag_value='lark2', help='Connect to Lark2 network')
@click.option('--mainnet', 'network', flag_value='mainnet', help='Connect to Hydra Mainnet (default)')
@click.option('--nice', 'network', flag_value='nice', help='Connect to Nice network')
@click.option('--local', 'network', flag_value='local', help='Connect to local network')
@click.option('--chopsticks', 'network', flag_value='chopsticks', help='Connect to Chopsticks network')
@click.option('--rpc', 'custom_rpc', help='Connect to custom RPC URL')
def remove_positions(asset_ids, check_farms, remove_token, network, custom_rpc):
    """Remove positions command with mandatory asset IDs and optional configuration flags.
    
    Optionally remove tokens from Omnipool after position removal (automatically sets tradability to 0).
    """
    click.echo(f"🚀 Captain's log: Engaging warp drive to remove positions for asset IDs: {list(asset_ids)}")
    click.echo(f"🔧 Engineering report: Dilithium crystals configured to check farms: {check_farms}")
    if remove_token:
        click.echo(f"🗑️  Protocol: Token removal from Omnipool is enabled (tradability will be set to 0)")
    click.echo("📡 Communications: Hailing frequencies open, preparing photon torpedo removal calls...")
    
    try:
        client = initialize_network_client(network=network, custom_rpc=custom_rpc)
        click.echo(f"✅ Helm: Successfully docked with starbase {client.api.chain}")
    except (SubstrateRequestException, RuntimeError, Exception) as e:
        click.echo("🚨 RED ALERT! 🚨")
        click.echo("💥 Engineering to Bridge: Warp core breach detected!")
        click.echo("🔴 Commander Data: Unable to establish subspace communication link with the starbase.")
        click.echo("🛸 Geordi La Forge: The dilithium matrix is showing anomalous readings, Captain.")
        click.echo("⚠️  Captain Picard: It appears the RPC connection has been severed by unknown forces.")
        click.echo("🖖 Mr. Spock: Logic dictates we cannot proceed without a stable quantum entanglement channel.")
        click.echo("💫 Status: Mission aborted. The final frontier will have to wait another day.")
        click.echo(f"🔧 Technical details for Chief O'Brien: {str(e)}")
        return
    omnipool = Omnipool(client)
    uniques = Uniques(client)
    utility = Utility(client)
    omnipool_wlm = OmnipoolWLM(client)
    omnipool_lm = OmnipoolLM(client)
    scheduler = Scheduler(client)
    circuit_breaker = CircuitBreaker(client)
    asset_registry = AssetRegistry(client)

    dispatch_as_calls = []
    future_omni_pos_owners = {}

    split_size = 20

    # Store original existential deposits for restoration later
    original_deposits = {}
    click.echo("� Archive: Storing existential deposits")
    for asset_id in asset_ids:
        asset_details = asset_registry.get_asset_details(asset_id)
        if asset_details and 'existential_deposit' in asset_details:
            original_deposits[asset_id] = asset_details['existential_deposit']
        else:
            click.echo(f"⚠️  Warning: Could not retrieve existential deposit for asset {asset_id}")

    # First step: Set circuit breaker remove liquidity limit to None AND set existential deposits to 0 (immediate execution)
    initial_calls = []
    click.echo("🔧 Circuit Breaker: Disabling remove liquidity limits for all specified assets...")
    for asset_id in asset_ids:
        cb_call = circuit_breaker.set_remove_liquidity_limit_call(asset_id, None)
        initial_calls.append(cb_call)
    
    click.echo("💰 Asset Registry: Setting existential deposits to 0 temporarily...")
    for asset_id in asset_ids:
        ed_call = asset_registry.update_call(asset_id, existential_deposit=0)
        initial_calls.append(ed_call)
    
    # Create schedule calls list (initial calls execute immediately, not scheduled)
    schedule_calls = []

    if check_farms:
        # Process positions for provided asset IDs
        for asset_id in asset_ids:
            deposit_positions = omnipool_wlm.get_deposit_positions(asset_id)
            click.echo(f"🔍 Sensors: Long-range scanners detect {len(deposit_positions)} Klingon LM deposit positions on asset {asset_id}")

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
        for i, sublist in enumerate(sublists):
            force_batch_call = utility.create_force_batch(sublist)
            block_delay = i + 1  # 1,2,3...
            schedule_call = scheduler.create_schedule_after_call(block_delay, force_batch_call)
            schedule_calls.append(schedule_call)

    click.echo("🔄 Science Officer: Analyzing quantum flux in OMNIPOOL nebula for all assets...")
    positions = omnipool.retrieve_positions()
    l = []
    for key, value in positions.items():
        if value.asset_id in asset_ids:
            l.append((key, value.shares))

    click.echo(f"📊 Data: Computing... {len(l)} hostile LP positions identified matching your tactical parameters")

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

    start_delay = len(sublists)
    for i, subremoval in enumerate(subremovals):
        force_batch_call = utility.create_force_batch(subremoval)
        block_delay = start_delay + (i + 1)
        schedule_call = scheduler.create_schedule_after_call(block_delay, force_batch_call)
        schedule_calls.append(schedule_call)

    click.echo("\n🎉 Mission accomplished! The Borg have been defeated. Here's your encoded subspace transmission:")
    click.echo("" + "="*50)
    
    # Add tradability, token removal, and existential deposit restoration if specified
    final_calls = []
    
    if remove_token:
        click.echo(f"🔧 Engineering: Setting tradability state to 0 for assets: {list(asset_ids)}")
        for asset_id in asset_ids:
            tradability_call = omnipool.set_asset_tradable_state_call(asset_id, 0)
            final_calls.append(tradability_call)
            
        click.echo(f"🗑️  Cleanup Protocol: Removing tokens from Omnipool for assets: {list(asset_ids)}")
        for asset_id in asset_ids:
            remove_token_call = omnipool.remove_token_call(asset_id)
            final_calls.append(remove_token_call)
    
    # Restore original existential deposits
    if original_deposits:
        click.echo("💰 Asset Registry: Restoring original existential deposit values...")
        for asset_id, original_deposit in original_deposits.items():
            click.echo(f"🔄 Restoration: Setting existential deposit back to {original_deposit} for asset {asset_id}")
            restore_ed_call = asset_registry.update_call(asset_id, existential_deposit=original_deposit)
            final_calls.append(restore_ed_call)
    
    # Add any final calls to the schedule calls list
    if final_calls:
        final_delay = start_delay + len(subremovals) + 1
        final_batch_call = utility.create_force_batch(final_calls)
        final_schedule_call = scheduler.create_schedule_after_call(final_delay, final_batch_call)
        schedule_calls.append(final_schedule_call)
    
    # Combine initial calls (circuit breaker + existential deposit = 0) + scheduled calls
    all_calls = []
    if initial_calls:
        initial_batch_call = utility.create_force_batch(initial_calls)
        all_calls.append(initial_batch_call)
    all_calls.extend(schedule_calls)
    
    # Batch all calls in one force_batch call
    final_batch_call = utility.create_force_batch(all_calls)
    click.echo(final_batch_call.encode())
    click.echo("" + "="*50)
    click.echo("✨ Captain, all systems are nominal. Permission to engage and transmit to the network, sir!")
    client.api.close()

