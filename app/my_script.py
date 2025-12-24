import click
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@click.group()
def cli():
    """News Aggregator Management CLI"""
    pass

@click.command()
@click.option('--port', default=8000, help='Port to run the API on')
def runserver(port):
    """Run the FastAPI development server"""
    import uvicorn
    click.echo(f"Starting API server on port {port}...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)

@click.command()
def worker():
    """Run the Celery worker"""
    click.echo("Starting Celery worker...")
    subprocess.run(["celery", "-A", "app.tasks", "worker", "--loglevel=info", "-P", "solo"])

@click.command()
def beat():
    """Run the Celery beat scheduler"""
    click.echo("Starting Celery beat...")
    subprocess.run(["celery", "-A", "app.tasks", "beat", "--loglevel=info"])

@click.command()
def fetch():
    """Manually trigger news ingestion"""
    import asyncio
    from app.tasks.fetch_articles import _fetch_all_sources_async
    click.echo("Manually fetching news articles...")
    results = asyncio.run(_fetch_all_sources_async())
    click.echo(f"Sync complete: {results}")

cli.add_command(runserver)
cli.add_command(worker)
cli.add_command(beat)
cli.add_command(fetch)

if __name__ == '__main__':
    cli()
