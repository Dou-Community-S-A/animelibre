import requests
import re
class AnimeFLV(object):

    def search(self, query):
        http = requests.get(f"https://m.animeflv.net/browse?q={query}").text
        matches=re.findall(r"a href=['\"]\/anime\/(.*?)['\"]",http)
        return matches

    def anime_info(self, anime_id):
        http= requests.get(f"https://m.animeflv.net/anime/{anime_id}").text

        try:
            self.title=re.findall(r"h1 class=\"Title\"[>](.*?)[<]",http)[0]
        except:
            self.title=anime_id
        try:
            self.status=re.findall(r'<p><strong>Estado:<\/strong> <strong class="[^"]*">(.*?)<\/strong>',http)[0]
        except:
            self.status="404 Not Found"
        try:
            self.summary=re.findall(r"<p><strong>Sinopsis:<\/strong>([\s\S]*?)<",http)[0]
        except:
            self.summary="404 Not Found"
        try:
            self.cover = re.findall(r'https:\/\/animeflv.net\/uploads\/animes\/covers\/.*?(?=\")',http)[0]
        except:
            self.cover = None
        self.episodes=re.findall(r'href="/ver/([^"]+)"',http)

    def get_links(self,episode_to_watch):
        episode = self.episodes[episode_to_watch-1]
        http_fragment = requests.get(f"https://m.animeflv.net/ver/{episode}").text

        url_pattern = r"https:\\\/\\\/ok.ru\\\/videoembed\\\/.*?\"|https:\\\/\\\/www.yourupload.com\\\/embed\\\/.*?\"|https:\\\/\\\/streamwish.to\\\/e\\\/.*?\""

        links = re.findall(url_pattern, http_fragment)
        for i in range(len(links)):
            links[i] = links[i].replace("\\","").strip('"')
        return links
    
    def anime_title(self):
        return self.title

    def anime_status(self):
        return self.status
    
    def anime_summary(self):
        return self.summary
    
    def anime_episodes(self):
        return self.episodes
    
    def anime_cover(self):
        return self.cover

