#!/usr/bin/python

import hashlib
import json
import os
import stat
import time

import markdown
import requests
from bs4 import BeautifulSoup


def removeEmojis(x):
    return ''.join(c for c in x if c <= '\uFFFF')


def parseMarkdownFile(path):
    f = open(path, 'r', encoding='utf-8')
    html = markdown.markdown(f.read(), extensions=['markdown.extensions.tables'])

    result = {}
    soup = BeautifulSoup(html, 'html.parser')
    for tr in soup.find_all('tr'):
        tds = [x for x in tr.find_all('td')]
        if len(tds) == 4:
            x = ''.join(tds[0].strings).strip()
            y = ''.join(tds[1].strings).strip()
            y = removeEmojis(y)
            if len(x) != 0 and len(y) != 0:
                result[x] = y

    return result


def sha1(path):
    sha1 = hashlib.sha1()
    with open(path, 'rb') as f:
        while True:
            data = f.read(64 * 1024)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


def saveTags(path, tags):
    with open(path, 'w') as f:
        json.dump(tags, f, ensure_ascii=False, indent=0)

    # Save sha1
    with open(path + ".sha1", 'w') as f:
        f.write(sha1(path))


def downloadMarkdownFiles():
    if os.system('git clone https://github.com/EhTagTranslation/Database.git --depth=1'):
        raise ValueError('Failed to git clone')


def rmtree(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            f = os.path.join(root, name)
            os.chmod(f, stat.S_IWUSR)
            os.remove(f)
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)


def removeMarkdownFiles():
    rmtree('Database')


if __name__ == "__main__":
    if os.path.exists('Database'):
        removeMarkdownFiles()
    downloadMarkdownFiles()

    tags = {}
    files = (
        ('rows.md', 'n'),
        ('artist.md', 'a'),
        ('cosplayer.md', 'cos'),
        ('character.md', 'c'),
        ('female.md', 'f'),
        ('group.md', 'g'),
        ('language.md', 'l'),
        ('male.md', 'm'),
        ('mixed.md', 'x'),
        ('other.md', 'o'),
        ('parody.md', 'p'),
        ('reclass.md', 'r')
    )
    for f, p in files:
        tags[p] = parseMarkdownFile(os.path.join('Database', 'database', f))
    saveTags('tag-translations/tag-translations-zh-rCN.json', tags)

    removeMarkdownFiles()

    tags = {}
    groups = (
        ('reclass', 'r'),
        ('language', 'l'),
        ('parody', 'p'),
        ('character', 'c'),
        ('group', 'g'),
        ('artist', 'a'),
        ('male', 'm'),
        ('female', 'f'),
        ('mixed', 'x'),
        ('cosplayer', 'cos'),
        ('other', 'o')
    )
    url = 'https://repo.e-hentai.org/tools.php?act=taggroup&show='
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'cookie': os.environ['COOKIE']
    }
    for index, (group, prefix) in enumerate(groups, start=1):
        r = requests.get(url + str(index), headers=headers)
        r.raise_for_status()  # TODO: Handle it
        soup = BeautifulSoup(r.content, 'html.parser')
        tags[prefix] = [a.text.removeprefix(group + ':') for a in soup.select('body > table a')]
        time.sleep(1)
    saveTags('tag-translations/tags.json', tags)
