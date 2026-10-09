// Demo-mode stand-in for the Drizzle client: a tiny in-memory store with
// invented rows. Filters are ignored because there is only one demo user.
import { getTableName } from 'drizzle-orm';
import { DEMO_USER } from './user';

const now = new Date();
const userId = '7d1f4c2a-5b8e-4f3a-9c61-2e0b9a7d4f10';

const rows: Record<string, any[]> = {
  users: [
    {
      id: userId,
      clerkId: DEMO_USER.id,
      fullName: DEMO_USER.fullName,
      email: DEMO_USER.primaryEmailAddress.emailAddress,
      avatarUrl: null,
      createdAt: DEMO_USER.createdAt,
      updatedAt: now,
    },
  ],
  customers: [],
  subscriptions: [
    {
      id: 'sub_demo',
      userId,
      email: DEMO_USER.primaryEmailAddress.emailAddress,
      status: 'active',
      priceId: 'demo-monthly',
      quantity: 1,
      createdAt: now,
      updatedAt: now,
    },
  ],
  user_prefs: [
    {
      userId,
      email: DEMO_USER.primaryEmailAddress.emailAddress,
      description: null,
      timezone: 'Europe/Lisbon',
      phone: null,
      prefTime: '07:00',
      isSubscribed: true,
      createdAt: DEMO_USER.createdAt,
      updatedAt: now,
    },
  ],
};

const chain = (resolve: () => any[]) => {
  const q: any = {
    from: () => q,
    where: () => q,
    limit: () => q,
    orderBy: () => q,
    returning: () => q,
    then: (ok: any, fail: any) => Promise.resolve(resolve()).then(ok, fail),
  };
  return q;
};

export const db: any = {
  select: () => {
    let table = '';
    const q = chain(() => rows[table] ?? []);
    q.from = (t: any) => {
      table = getTableName(t);
      return q;
    };
    return q;
  },
  insert: (t: any) => ({
    values: (v: any) => {
      const table = getTableName(t);
      (rows[table] ??= []).push(v);
      return chain(() => [v]);
    },
  }),
  update: (t: any) => ({
    set: (v: any) => {
      const table = getTableName(t);
      const list = (rows[table] ??= []);
      if (list[0]) Object.assign(list[0], v);
      return chain(() => list.slice(0, 1));
    },
  }),
  delete: () => chain(() => []),
};
