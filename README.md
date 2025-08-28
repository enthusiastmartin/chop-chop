# Chop-Chop

A CLI utility for managing blockchain positions and liquidity removal operations.

## Description

Chop-chop is a Python CLI tool that provides commands for removing positions from blockchain networks, specifically designed to work with Omnipool operations. It uses the Substrate interface to interact with blockchain networks and provides batch operations for efficient position management.

## Requirements

- Python >= 3.13
- uv (Python package installer and resolver)

## Installation

1. Install uv if you haven't already:
   ```bash
   brew install uv
   ```

   OR 


   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone this repository:
   ```bash
   git clone <repository-url>
   cd chop-chop
   ```

3. Install dependencies using uv:
   ```bash
   uv sync
   ```

## Usage

Run the CLI using uv:

```bash
uv run python -m chopchop --help
```

### Available Commands

#### `remove-positions`

Remove positions for specified asset IDs with optional farm checking.

```bash
uv run python -m chopchop remove-positions [ASSET_IDS]... [OPTIONS]
```

**Arguments:**
- `ASSET_IDS`: One or more asset IDs (integers >= 1) to process

**Options:**
- `--check-farms / --no-check-farms`: Flag to indicate if farms should be checked (default: True)

**Network Options:**
- `--lark1`: Connect to Lark1 network
- `--lark2`: Connect to Lark2 network  
- `--mainnet`: Connect to Hydra Mainnet (default)
- `--nice`: Connect to Nice network
- `--local`: Connect to local network
- `--chopsticks`: Connect to Chopsticks network
- `--rpc URL`: Connect to custom RPC URL

Other Options:
- `--help`: Show command help

**Examples:**

```bash
# Remove positions for single asset (uses Hydra Mainnet by default)
uv run python -m chopchop remove-positions 123

# Remove positions for multiple assets
uv run python -m chopchop remove-positions 123 456 789

# Remove positions without checking farms
uv run python -m chopchop remove-positions 123 --no-check-farms

# Use different networks
uv run python -m chopchop remove-positions 123 --lark1
uv run python -m chopchop remove-positions 123 --lark2
uv run python -m chopchop remove-positions 123 --nice

# Use custom RPC endpoint
uv run python -m chopchop remove-positions 123 --rpc ws://myrpc.com:443
uv run python -m chopchop remove-positions 123 --rpc https://custom.endpoint.com

# Combine network selection with other options
uv run python -m chopchop remove-positions 123 456 --lark1 --no-check-farms
```

## Development

The project structure:

- `chopchop/cli.py` - Main CLI interface using Click
- `chopchop/client.py` - Network client initialization
- `chopchop/pallets/` - Blockchain pallet interactions
- `chopchop/types.py` - Type definitions

To run in development mode:

```bash
uv run python -m chopchop
```

## Dependencies

- `click` - Command line interface creation
- `substrate-interface` - Blockchain network interaction
