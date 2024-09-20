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


@main.command(help="Test cache expiry")
@click.argument("url")
async def test_cache(url):
    async with (
        factory.produce("http_session") as http_session
    ):
        response = await http_session.get(url)
        response.raise_for_status()
        print(await response.text())


if __name__ == "__main__":
    main(_anyio_backend="asyncio")
