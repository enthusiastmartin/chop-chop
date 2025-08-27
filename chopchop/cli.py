import click


@click.group()
def cli():
    """Chop-chop CLI utility."""
    pass


@cli.command()
@click.argument('position', type=click.IntRange(min=1))
@click.option('--has-farms/--no-has-farms', default=False, help='Flag to indicate if farms are present')
def remove_positions(position, has_farms):
    """Remove positions command with a mandatory positive number and optional has_farms flag."""
    click.echo(f"-- remove_positions executed with position={position}, has_farms={has_farms}")
