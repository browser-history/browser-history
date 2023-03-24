import csv
a = """
Timestamp,URL,Title
2020-09-23 13:15:03+08:00,https://pesos.github.io/,Welcome to PES Open Source - PES Open Source
2020-10-01 16:43:35+08:00,https://www.youtube.com/,YouTube
2020-10-01 16:43:35+08:00,https://www.youtube.com/,YouTube
2020-10-01 16:44:11+08:00,https://www.reddit.com/,reddit: the front page of the internet
2020-10-01 16:44:11+08:00,https://www.reddit.com/,reddit: the front page of the internet
2020-10-01 16:44:20+08:00,https://www.wikipedia.org/,Wikipedia
2020-10-01 16:44:20+08:00,https://www.wikipedia.org/,Wikipedia
2020-10-01 17:17:37+08:00,https://www.mozilla.org/en-US/firefox/welcome/2/,"Pocket - Save news, videos, stories and more"
2020-10-01 17:17:37+08:00,https://www.mozilla.org/en-US/firefox/welcome/2/,"Pocket - Save news, videos, stories and more"
2020-10-01 17:18:21+08:00,https://www.mozilla.org/en-US/firefox/welcome/2/,"Pocket - Save news, videos, stories and more"
2020-10-01 17:18:21+08:00,https://www.mozilla.org/en-US/firefox/welcome/2/,"Pocket - Save news, videos, stories and more"
2020-10-01 17:18:24+08:00,https://www.wikipedia.org/,Wikipedia
2020-10-01 17:18:24+08:00,https://www.wikipedia.org/,Wikipedia
2020-10-01 17:18:25+08:00,https://www.youtube.com/,YouTube
2020-10-01 17:18:25+08:00,https://www.youtube.com/,YouTube
2020-10-04 19:02:14+08:00,https://www.reddit.com/,reddit: the front page of the internet
2020-10-04 19:02:14+08:00,https://www.reddit.com/,reddit: the front page of the internet
2020-10-13 17:04:51+08:00,https://www.youtube.com/,YouTube
2020-10-13 17:04:59+08:00,https://github.com/,GitHub: Where the world builds software · GitHub
2020-12-08 02:58:11+08:00,https://github.com/,GitHub: Where the world builds software · GitHub
2020-12-08 02:58:45+08:00,https://github.com/,GitHub: Where the world builds software · GitHub
2020-12-08 03:00:40+08:00,https://www.reddit.com/,reddit: the front page of the internet
2020-12-08 03:01:29+08:00,https://stackoverflow.com/,"Stack Overflow - Where Developers Learn, Share, & Build Careers"
"""

s = csv.Sniffer()
s.sniff(a)
print(s.has_header(a))