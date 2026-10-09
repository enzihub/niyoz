'use client';

import { useState } from 'react';
import { Share, Copy, Check } from 'lucide-react';

export default function SharePage() {
  const [copied, setCopied] = useState(false);
  const shareUrl =
    process.env.NEXT_PUBLIC_SITE_URL || 'http://127.0.0.1:3000';

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <section className='w-full'>
      <div className='mx-auto max-w-2xl px-4 py-16'>
        <div className='mb-12 space-y-6 text-center'>
          <div className='inline-flex h-12 w-12 items-center justify-center rounded-full bg-blue-50'>
            <Share className='h-6 w-6 text-blue-600' />
          </div>
          <h1 className='text-3xl font-bold tracking-tight text-gray-900'>
            Share with friends
          </h1>
          <p className='text-gray-500'>
            Copy the link below or click a button and share it with your network
          </p>
        </div>

        <div className='space-y-6'>
          <div className='relative'>
            <input
              type='text'
              readOnly
              value={shareUrl}
              className='w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500'
            />
            <button
              onClick={handleCopy}
              className='absolute right-2 top-1/2 -translate-y-1/2 rounded-md p-2 transition-colors hover:bg-gray-100'
            >
              {copied ? (
                <Check className='h-5 w-5 text-green-600' />
              ) : (
                <Copy className='h-5 w-5 text-gray-400' />
              )}
            </button>
          </div>

          <div className='flex flex-col gap-3'>
            <button
              onClick={() =>
                window.open(
                  `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}`,
                  '_blank',
                )
              }
              className='w-full rounded-lg bg-[#1DA1F2] px-4 py-3 font-medium text-white transition hover:bg-[#1a8cd8]'
            >
              Share on Twitter
            </button>

            <button
              onClick={() =>
                window.open(
                  `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
                  '_blank',
                )
              }
              className='w-full rounded-lg bg-[#0A66C2] px-4 py-3 font-medium text-white transition hover:bg-[#094d92]'
            >
              Share on LinkedIn
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
