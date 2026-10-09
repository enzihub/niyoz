'use client';

import React from 'react';
import { SignInButton, SignUpButton } from '@clerk/nextjs';
import { getUserTimezone } from '@/shared/services/timezone';

export const AuthButton = ({
  loading,
  isSignup,
}: {
  loading?: boolean;
  isSignup?: boolean;
}) => {
  const ButtonComponent = isSignup ? SignUpButton : SignInButton;
  const timezone = getUserTimezone();

  return (
    <div className='mx-auto flex justify-center'>
      <ButtonComponent
        mode='modal'
        forceRedirectUrl={`auth/callback?timezone=${encodeURIComponent(timezone)}`}
      >
        <button
          disabled={loading}
          className='w-full rounded-2xl bg-[#0059FF] px-3 py-3 text-lg font-medium text-[#FCFCFA] hover:bg-blue-700 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 md:text-xl'
        >
          {isSignup ? 'Sign up' : 'Sign in'}
        </button>
      </ButtonComponent>
    </div>
  );
};
