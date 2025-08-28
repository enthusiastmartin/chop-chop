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
uv run chopchop --help
```

### Available Commands

#### `remove-positions`

Remove positions for specified asset IDs with optional farm checking.

```bash
uv run chopchop remove-positions [ASSET_IDS]... [OPTIONS]
```

**Arguments:**
- `ASSET_IDS`: One or more asset IDs (integers >= 1) to process

**Options:**
- `--check-farms / --no-check-farms`: Flag to indicate if farms should be checked (default: True)
- `--help`: Show command help

**Examples:**

```bash
# Remove positions for single asset
uv run chopchop remove-positions 123

# Remove positions for multiple assets
uv run chopchop remove-positions 123 456 789

# Remove positions without checking farms
uv run chopchop remove-positions 123 --no-check-farms
```

## Development

The project structure:

- `chopchop/cli.py` - Main CLI interface using Click
- `chopchop/client.py` - Network client initialization
- `chopchop/pallets/` - Blockchain pallet interactions
- `chopchop/types.py` - Type definitions

To run in development mode:

```bash
uv run chopchop
```

## Dependencies

- `click` - Command line interface creation
- `substrate-interface` - Blockchain network interaction