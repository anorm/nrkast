import asyncio

from . import factory


async def main():
    async with (
        factory.produce("scraper") as scraper
    ):
        await scraper.scrape("radiodokumentaren")


if __name__ == "__main__":
    print("-"*50)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
