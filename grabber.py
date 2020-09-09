import os
from typing import Union

import requests
import textwrap
import configparser
import bs4
from bs4 import BeautifulSoup
from urllib import parse
import argparse


class ArticleGrabber:
    """
    Article grabber class.
    Used to extract the text of an article from a news site.

    Constructor accepts article url and optional configuration argument.

    Methods:
    --------
    download_text()
        Method allows save cleaned text from article
        to a folder that repeats the structure of the article url
    """

    _base: str = os.path.dirname(os.path.abspath(__file__))
    _default_config: dict = {
        "GRABBER": {
            "wrap": 80,
            "words_count": 20,
            "scip_paragraphs": 3,
            "output_dir": ".",
        }
    }

    def __init__(self, url: str, config: Union[configparser.ConfigParser, dict] = None) -> None:
        self.url = url
        self._soup = self._get_soup()
        if not config:
            config = self._default_config
        self._wrap = int(config["GRABBER"]["wrap"])
        self._scip_paragraphs = int(config["GRABBER"]["scip_paragraphs"])
        self._words_count = int(config["GRABBER"]["words_count"])
        self._output_dir = config["GRABBER"]["output_dir"]
        self._prepare_folder_and_filename()

    def _get_soup(self) -> BeautifulSoup:
        """
        Method for creating a BeautifulSoup object based on url.
        :raise requests.exceptions.RequestException:
        If the request to the server does not return code 200
        """

        response = requests.get(self.url)
        if response.status_code != 200:
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        return soup

    def _prepare_links(self, tag: bs4.element.Tag) -> None:
        """
        Method for preparing links for better text perception.
        If the hostname is missing from the link, it is added.
        :param tag: Tag
        """

        links = tag.find_all("a")

        for link in links:
            try:
                if parse.urlparse(link["href"]).netloc == "":
                    full_link = parse.urljoin(self.url_host, link["href"])
                else:
                    full_link = link["href"]
            except KeyError:
                continue
            tag.a.replace_with(f"{link.text}[{full_link}]")

    def _prepare_folder_and_filename(self) -> None:
        """
        The method determines the file name for the record,
        the full path to the file and creates a directory to save the file.
        """

        output_dir = os.path.join(self._base, self._output_dir)
        hostname: str = parse.urlparse(self.url).hostname
        article_path: list = parse.urlparse(self.url).path.split("/")
        self.url_host = f"{parse.urlparse(self.url).scheme}://{hostname}"

        if article_path[-1] == "":
            self.output_folder_path = os.path.join(
                output_dir, hostname, *article_path[:-2]
            )
            self.filename = f"{article_path[-2]}.txt"
        else:
            self.output_folder_path = os.path.join(
                output_dir, hostname, *article_path[:-1]
            )
            self.filename = f"{article_path[-1].split('.')[0]}.txt"
        os.makedirs(self.output_folder_path, exist_ok=True)

    def _save_text_to_file(self) -> None:
        """Method for writing a file with article text"""
        text_to_write = self.text.replace(
            "\xa0", " "
        )  # replace a non-breaking space with space
        with open(
                os.path.join(self.output_folder_path, self.filename), "w", encoding="utf8"
        ) as f:
            f.write(text_to_write)

    def _extract_article_title(self) -> None:
        """Method retrieves article title"""
        try:
            article_title = self._soup.find(["h1"]).text.strip()
        except AttributeError:
            article_title = self._soup.find(["h2", "h3"]).text.strip()
        self.text = textwrap.fill(article_title, self._wrap) + "\n\n"

    def _extract_article_text(self) -> None:
        """
        Method retrieves article text from <p> tag.
        If not, calls method for extract text from div.
        """
        paragraphs = self._soup.find_all("p")
        try:
            missing_paragraphs = list(paragraphs)[
                self._scip_paragraphs
            ]  # How many paragraphs to skip
            first_paragraph_parent_attr = missing_paragraphs.parent.parent.attrs
            for p in paragraphs:
                if p.parent.parent.attrs == first_paragraph_parent_attr:
                    self._prepare_links(p)
                    self.text += textwrap.fill(p.text.strip(), self._wrap) + "\n\n"
        except IndexError:
            self._div_parser()

    @staticmethod
    def _div_filter(tag) -> bool:
        """
        Function for filtering div tags
        Filter div that contains no child divs or only contains a string
        """
        return tag.name == "div" and not tag.div or tag.string

    def _div_parser(self) -> None:
        """
        Method retrieves article text from <div> tag.
        """
        divs = self._soup.find_all(self._div_filter)

        for div in divs:
            if len(div.text.strip().split()) > self._words_count:
                self._prepare_links(div)
                self.text += textwrap.fill(div.text.strip(), self._wrap) + "\n\n"

    def download_text(self) -> None:
        """
        Method for extract data from article and saving clean text
        """
        self._extract_article_title()
        self._extract_article_text()
        self._save_text_to_file()


def main(args):
    if args.config_path:
        config = configparser.ConfigParser()
        config.read(args.config_path)
    else:
        config = None
    try:
        grabber = ArticleGrabber(args.url, config)
        grabber.download_text()
        print("Upload completed successfully")
    except requests.exceptions.RequestException:
        print("Unable to download article")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to download article text from news sites"
    )
    parser.add_argument("url", type=str, help="Link with article")
    parser.add_argument(
        "-c", "--config", dest="config_path", type=str, help="Configuration file path"
    )
    args = parser.parse_args()
    main(args)
