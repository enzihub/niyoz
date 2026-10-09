// Invented demo user. Not a real person.
const avatar =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96"><rect width="96" height="96" rx="48" fill="#0059FF"/><text x="48" y="60" font-family="Arial, sans-serif" font-size="38" font-weight="700" fill="#fff" text-anchor="middle">MO</text></svg>`,
  );

export const DEMO_USER = {
  id: 'user_demo_maya',
  firstName: 'Maya',
  lastName: 'Okafor',
  fullName: 'Maya Okafor',
  imageUrl: avatar,
  hasVerifiedEmailAddress: true,
  createdAt: new Date('2025-02-14T09:30:00Z'),
  primaryEmailAddress: { emailAddress: 'maya.okafor@example.com' },
  emailAddresses: [{ emailAddress: 'maya.okafor@example.com' }],
};
