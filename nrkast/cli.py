import asyncclick as click
from . import factory


@click.group()
async def main():
    pass


@main.command(help="Generate RSS feed")
@click.argument("slug")
async def rss(slug):
    async with (
        factory.produce("scraper") as scraper
    ):
        print(await scraper.scrape(slug))


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
