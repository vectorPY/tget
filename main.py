import requests
import argparse
from typing import Optional
from pathlib import Path
from bs4 import BeautifulSoup
import shutil
import exceptions

# TODO: Implement limit


class Scraper: 
    def __init__(self, url: str, path: Path, limit: Optional[int]):
        """
        :param url: url of the thread (like this: https://boards.4chan.org/<board>/thread/<id>)
        :param path: path where the folder for the media should be created
        :param limit: media limit (only the given amount of data will be saved)
        """
        self.url = url
        self.limit = limit        
        self.path = path        
        self.req = requests.get(self.url)
        self.r = self.req.content
        self.soup = BeautifulSoup(self.r, "html.parser")

    def verify_url(self) -> bool:
        """
        checks if the url fits the normal pattern
        :return: depending on the result
        """
        if self.req.status_code != 200:
            raise exceptions.InvalidUrlException(f"{self.req.status_code} Error")
        s = self.url.split("/")
        if len(s) != 6 or s[4] != "thread" or not s[-1].isnumeric():
            return False
        return True        

    def get_link_list(self) -> list[str]:
        """
        :return: all links of images/videos etc.
        """
        if self.verify_url():
            self.get_thread_name()
            return ["https:" + a["href"] for a in self.soup.find_all("a", href=True) if "i.4cdn.org" in a["href"]]
        else:
            raise exceptions.InvalidUrlException("Please provide a valid 4chan url")
    
    def get_thread_name(self) -> str:
        title = str(self.soup.find("title")).split("-")[1].strip()
        return title.replace(" ", "_")

    def save(self):
        """
        saves the images in the given folder
        """
        links = self.get_link_list()
        p = Path(self.path / self.get_thread_name())
        p.mkdir(parents=True, exist_ok=True)
        for link in links:
            print(f"Saving {link}...")

            r = requests.get(link, stream=True)
            filename = link.split("/")[-1]            

            with open(self.path / p / filename, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            del r
        
        print(f"Finished! Files saved at {self.path / p}")


def main():
    parser = argparse.ArgumentParser(description='Download 4chan Threads')
    parser.add_argument("--link", "-l", dest="link", type=str, help="The Link of the Thread")    
    parser.add_argument("--limit", dest="limit", type=int, help="Media limiMedia limitt")    
    parser.add_argument(
        "--output", "-o", 
        dest="path", 
        type=Path, 
        default=Path(__file__).absolute().parent,
        help="Path to save"
    )    

    args = parser.parse_args()
    s = Scraper(args.link, Path(args.path), args.limit)
    s.save()    


if __name__ == '__main__':
    main()
