// Demo-mode stand-in for @clerk/nextjs/server (see next.config.mjs).
import { DEMO_USER } from './user';

export type WebhookEvent = any;

export const auth = async () => ({ userId: DEMO_USER.id });
export const currentUser = async () => DEMO_USER;

export const createRouteMatcher = (patterns: string[]) => {
  const regexes = patterns.map((p) => new RegExp(`^${p}$`));
  return (req: { nextUrl: { pathname: string } }) =>
    regexes.some((r) => r.test(req.nextUrl.pathname));
};

export const clerkMiddleware =
  (handler: (authFn: typeof auth, req: any) => any) => (req: any) =>
    handler(auth, req);
