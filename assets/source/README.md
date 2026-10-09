# Art sources

The README and social images are plain HTML rendered with headless Chromium
(Playwright) at 2x. They use the real app screenshots in `docs/img/` and the
self-hosted fonts in `docs/fonts/`.

```bash
cd assets/source && node render.js   # needs the `playwright` package
```

`docs/demo-thumbs/` holds AI-generated scenes used as thumbnails for the
invented demo videos (ChatGPT image generation). No real creator's image is
used anywhere.
