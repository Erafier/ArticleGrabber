import os
import pytest
import requests

from grabber import ArticleGrabber

TEST_CONFIG = {
    "GRABBER": {
        "wrap": 80,
        "words_count": 20,
        "scip_paragraphs": 3,
        "output_dir": "tests/articles",
    }
}

TEST_URLS = [
    "https://lenta.ru/news/2020/09/04/bogat/",
    "https://www.gazeta.ru/politics/2020/09/04_a_13236446.shtml",
    "https://vc.ru/tech/156713-amazon-apple-google-i-drugie-anonsirovali-edinyy-standart-dlya-ustroystv-umnogo-doma-v-2021-godu",
    "https://www.rbc.ru/politics/07/09/2020/5f55dda39a79472a56d81e24?utm_source=yxnews&utm_medium=desktop",
    "https://tass.ru/mezhdunarodnaya-panorama/9388223",
    "https://www.spb.kp.ru/daily/217178.5/4282326/",
    "https://meduza.io/news/2020/09/07/kurs-evro-prevysil-90-rubley-vpervye-s-fevralya-2016-goda",
    "https://www.kommersant.ru/doc/4482578",
    "https://rg.ru/2020/09/07/bmw-posmeialas-nad-novym-mercedes-s-class-no-sdelala-eto-s-uvazheniem.html",
    "https://news.rambler.ru/community/44791552-urnu-nadenu-na-bashku-darmoedy-i-nischebrody-uchitelnitsa-v-rossiyskoy-shkole-otchitala-uchenikov-za-bardak-v-klasse/",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_valid_urls():
    for url in TEST_URLS:
        grabber = ArticleGrabber(url, config=TEST_CONFIG)
        grabber.download_text()
    out_dir_1 = os.path.join(
        BASE_DIR, "articles\\lenta.ru\\news\\2020\\09\\04\\bogat.txt"
    )
    out_dir_2 = os.path.join(
        BASE_DIR, "articles\\www.spb.kp.ru\\daily\\217178.5\\4282326.txt"
    )
    out_dir_3 = os.path.join(
        BASE_DIR,
        "articles\\news.rambler.ru\\community\\"
        "44791552-urnu-nadenu-na-bashku-darmoedy-i-nischebrody-uchitelnitsa-v-rossiyskoy-shkole-otchitala-uchenikov-za-bardak-v-klasse.txt",
    )
    assert os.path.exists(out_dir_1)
    assert os.path.exists(out_dir_2)
    assert os.path.exists(out_dir_3)


def test_invalid_url():
    with pytest.raises(requests.exceptions.RequestException):
        grabber = ArticleGrabber("https://ssss123")


def test_text_file_lines_width():
    width = TEST_CONFIG["GRABBER"]["wrap"]
    with open(
        "tests\\articles\\lenta.ru\\news\\2020\\09\\04\\bogat.txt", "r", encoding="utf8"
    ) as f:
        for line in f:
            assert len(line.strip()) <= width
