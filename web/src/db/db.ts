import { drizzle } from 'drizzle-orm/neon-http';
import { db as demoDb } from '@/demo/db';

export const db =
  process.env.NEXT_PUBLIC_DEMO_MODE === 'true'
    ? demoDb
    : drizzle(process.env.DATABASE_URL!);
