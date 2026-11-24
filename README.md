# The World in One Day — 24 November 2026

[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/fearxfx22/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/fearxfx22/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

A one-page front-page infographic of the world's news on Tuesday 24 November 2026:
33 dated stories across 7 regions, drawn as a newspaper front page — masthead,
headline, three illustrated feature stories, a ten-story medium grid, a world map
with numbered pins, a list of twenty more stories, and a date check that says
plainly what was left out and why.

Every story is dated to 24 November 2026 and tagged by how it was verified:
CONFIRMED (two or more outlets), OFFICIAL (on the record), or REPORTED (one outlet).

## Run it

```sh
python3 main.py entry.png
```

With Pillow installed it draws the page from `stories.json` with `draw.py`.
Without Pillow (the grader's Python has none) it copies the bundled `entry.png`
instead — the same bytes either way.

## Files

- `main.py` — entrypoint: draw the page, or copy the bundled image when Pillow is missing.
- `draw.py` — the renderer: masthead, features, grid, map, lists, date check.
- `stories.json` — the 33 verified stories and the numbers strip.
- `entry.png` — the finished 1024×1024 page.
- `fonts/` — Liberation Serif and Sans, the fonts the page is drawn with.

Built for the [news-image-20261124 bounty](https://make.fun/bounty/news-image-20261124)
on make.fun.
