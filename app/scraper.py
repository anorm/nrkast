class Scraper:
    def __init__(self, *, logger, http_session):
        self.logger = logger
        self.http_session = http_session
        self.base_url = "https://psapi.nrk.no"

    def _get_podcast_url(self, slug):
        return f"{self.base_url}/radio/catalog/podcast/{slug}"

    async def scrape(self, slug):
        self.logger.info(f"Scraping {slug}")

        url = self._get_podcast_url(slug)
        self.logger.info(f"URL: {url}")

        resp = await self.http_session.get(url)
        resp.raise_for_status()
        return await resp.json()
