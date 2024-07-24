from podgen import Podcast, Episode, Media
from lxml import etree
import datetime


class Scraper:
    def __init__(self, *, logger, http_session, episode_cache):
        self.logger = logger
        self.http_session = http_session
        self.episode_cache = episode_cache
        self.base_url = "https://psapi.nrk.no"

    def _get_podcast_url(self, slug):
        return f"{self.base_url}/radio/catalog/podcast/{slug}"

    async def _get(self, url):
        response = await self.http_session.get(url)
        response.raise_for_status()
        data = await response.json()
        return data

    async def _scrape_episode(self, data):
        id = data["episodeId"]

        # Check cache first
        cached_xml = await self.episode_cache.get(id)
        if cached_xml:
            return cached_xml

        # Not in cache, build the Episode object
        episode = Episode()
        episode.id = id
        episode.title = data.get("titles", {}).get("title", "missing title")
        episode.summary = data.get("titles", {}).get("subtitle")
        images = data.get("squareImage", [])
        if images:
            images.sort(key=lambda x: x.get("width", 1))
            episode.image = images[-1].get("url") + ".jpeg"
        episode.publication_date = datetime.datetime.fromisoformat(data["date"])

        playbackUrl = f"{self.base_url}{data['_links']['playback']['href']}"
        playback_data = await self._get(playbackUrl)

        playableUrl = f"{self.base_url}{playback_data['playable']['resolve']}"
        playable_data = await self._get(playableUrl)
        media = Media.create_from_server_response(playable_data["playable"]["assets"][0]["url"],
                                                  duration=datetime.timedelta(seconds=data["durationInSeconds"]))
        episode.media = media
        self.logger.info(f"Found new episode {id}")

        # Turn into an XML string
        xmlString = etree.tostring(episode.rss_entry(), encoding="UTF-8").decode("UTF-8")

        # Put it in the cache
        await self.episode_cache.set(id, xmlString)

        return xmlString

    async def scrape(self, slug):
        url = self._get_podcast_url(slug)
        self.logger.debug(f"Scraping {slug} from {url}")

        response = await self.http_session.get(url)
        response.raise_for_status()
        podcast_data = await response.json()

        podcast = Podcast()
        podcast.name = podcast_data.get("series", {}).get("titles", {}).get("title", slug)
        podcast.description = podcast_data.get("series", {}).get("titles", {}).get("subtitle", podcast.name)
        podcast.website = podcast_data.get("_links", {}).get("share", {}).get("href", f"https://nrk-podcast.onrender.com/podcast/{slug}")
        podcast.explicit = False
        images = podcast_data.get("series", {}).get("squareImage", [])
        if images:
            images.sort(key=lambda x: x.get("width", 1))
            podcast.image = images[-1].get("url") + ".jpeg"

        # Find episodes
        url = f"{self.base_url}{podcast_data["_links"]["episodes"]["href"]}"
        xmlStringEpisodes = []
        while True:
            response = await self.http_session.get(url)
            response.raise_for_status()
            page_data = await response.json()
            episodes_data = page_data.get("_embedded", {}).get("episodes", [])
            nextPath = page_data.get("_links", {}).get("next", {}).get("href")

            for episode_data in episodes_data:
                xmlStringEpisodes.append(await self._scrape_episode(episode_data))

            if not episodes_data:
                break
            if not nextPath:
                break
            url = f"{self.base_url}{nextPath}"

        # Add episodes to podcast
        xmlPodcast = podcast._create_rss()

        channelNode = xmlPodcast.find("channel")
        for xmlStringEpisode in xmlStringEpisodes:
            channelNode.append(etree.fromstring(xmlStringEpisode))

        body = etree.tostring(xmlPodcast,
                              encoding="UTF-8",
                              xml_declaration=True,
                              pretty_print=True).decode("UTF-8")

        return body
