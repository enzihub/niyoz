'use client';
// Demo-mode stand-in for @clerk/nextjs (see next.config.mjs).
import React from 'react';
import { DEMO_USER } from './user';

type Props = { children?: React.ReactNode; [key: string]: unknown };

export const ClerkProvider = ({ children }: Props) => <>{children}</>;
export const SignedIn = ({ children }: Props) => <>{children}</>;
export const SignedOut = (_: Props) => null;
export const SignInButton = ({ children }: Props) => <>{children}</>;
export const SignUpButton = ({ children }: Props) => <>{children}</>;
export const SignOutButton = ({ children }: Props) => <>{children}</>;
export const UserButton = () => null;
const Panel = ({ title }: { title: string }) => (
  <div className='mx-auto mt-8 max-w-md rounded-2xl bg-white p-8 text-center shadow-sm'>
    <h1 className='text-2xl font-bold'>{title}</h1>
    <p className='mt-2 text-gray-600'>
      Demo mode is on, so you are already signed in as {DEMO_USER.fullName}.
    </p>
  </div>
);
export const SignIn = (_: Props) => <Panel title='Sign in' />;
export const SignUp = (_: Props) => <Panel title='Sign up' />;

export const useUser = () => ({
  user: DEMO_USER,
  isLoaded: true,
  isSignedIn: true,
});
export const useAuth = () => ({
  isLoaded: true,
  isSignedIn: true,
  userId: DEMO_USER.id,
  sessionId: 'sess_demo',
  getToken: async () => null,
});
export const useClerk = () => ({
  signOut: async () => {
    window.location.href = '/';
  },
});
