# Demo mode

`NEXT_PUBLIC_DEMO_MODE=true` lets the web app run on your machine with no
Clerk, Stripe or Postgres account:

- `clerk.tsx` / `clerk-server.ts` replace `@clerk/nextjs` (wired in
  `next.config.mjs`) with one signed-in, invented user.
- `db.ts` is a tiny in-memory stand-in for the Drizzle client with invented rows.
- `/api/pricing` returns the plans from `stripe_fixtures.json` instead of
  calling Stripe.

Everything in this folder is fictional demo data. It is only used when demo
mode is on.
