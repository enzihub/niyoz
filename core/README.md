# niyoz-core

The backend for Niyoz. It reads a user's YouTube homepage recommendations,
pulls each video's transcript, asks an LLM for a short summary, and emails the
result as one daily digest at the hour the user picked.

Built with FastAPI, Celery, Redis, SQLAlchemy (Postgres) and Jinja2.

## How it works

1. **Celery beat** runs `tasks.produce_messages` every hour. It calls the
   `get_scheduled_users` Postgres function to find users whose preferred hour
   falls in the next window.
2. For each user it fetches their Google OAuth token from **Clerk**, calls
   YouTube's homepage feed (`FEwhat_to_watch`) and shuffles the results.
3. `youtube-transcript-api` fetches transcripts (optionally through a
   ScrapeOps proxy). Videos without a transcript are skipped.
4. **OpenAI** writes a summary per video, a subject line and a one-line
   overview. Free users get 3 videos, subscribers get 12.
5. The email is rendered from `templates/newsletter.html` and parked in a
   **Redis** sorted set keyed by send time.
6. `tasks.consume_messages` runs every minute and sends due emails through
   **Mailtrap**.

`POST /send-newsletter` (with the `X-API-Key` header) skips the queue and
builds one digest for a user right away. The web app's "Dopamine Hit" button
calls it.

## Run it

```bash
cp .env.example .env.development     # fill in the blanks
poetry install
docker run -d --name niyoz-redis -p 6379:6379 redis:alpine
poetry run uvicorn main:app --reload --port 8000
poetry run celery -A app.core.scheduler.job_tasks worker --loglevel=info
poetry run celery -A app.core.scheduler.job_tasks beat --loglevel=info
```

Or everything at once: `docker compose up --build` (reads `.env`).

## Demo mode (no Google, OpenAI or database needed)

```bash
YOUTUBE_DEMO_MODE=true REDIS_URL=redis://127.0.0.1:6379/0 API_KEY=dev \
DEMO_THUMB_BASE_URL=http://127.0.0.1:8000/demo/thumbs \
poetry run uvicorn main:app --port 8000

curl -X POST localhost:8000/send-newsletter -H 'X-API-Key: dev' \
  -H 'content-type: application/json' -d '{"email":"you@example.com"}'
# then open http://127.0.0.1:8000/demo/outbox/latest
```

Demo mode swaps YouTube for eight invented videos from invented channels
(`app/integrations/youtube/demo_data.py`). Their thumbnails in
`../docs/demo-thumbs/` are AI-generated scenes. Without `OPENAI_API_KEY` the
summaries are canned text; with a key the real prompts run on the invented
transcripts. Emails go to a local `outbox/` folder instead of Mailtrap.

## Tests

```bash
poetry run pytest
```

## Configuration

See [`.env.example`](.env.example). The main values:

| Variable | Purpose |
| --- | --- |
| `API_KEY` | Shared secret the web app sends as `X-API-Key` |
| `DATABASE_URL` | Postgres, same database as the web app |
| `REDIS_URL`, `CELERY_*` | Message queue and Celery broker |
| `CLERK_SECRET_KEY` | Reads each user's Google OAuth token |
| `OPENAI_API_KEY` | Summaries, subject lines and overviews |
| `MAILTRAP_API_TOKEN`, `FROM_EMAIL`, `FROM_NAME` | Email delivery |
| `APP_URL`, `CONTACT_EMAIL`, `NEWSLETTER_LOGO_URL` | Links and branding in the email |
| `YOUTUBE_DEMO_MODE` | Invented videos instead of YouTube |
