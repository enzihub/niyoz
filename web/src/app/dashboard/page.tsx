'use client';
import { VideoPlayer } from '@/shared/components/VideoPlayer';
import { useUser } from '@clerk/nextjs';
import { useState } from 'react';
import { sendNewsletterAction } from '../(newsletter)/_actions/newsletter';

export default function Dashboard() {
  const { user } = useUser();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    status: string;
    subject?: string;
    preview?: string;
  } | null>(null);
  //const supabase = createClient();
  // TODO: Implement user object using clerk user object

  /**
   if (!user) {
    return (
      <div className='flex items-center justify-center min-h-screen'>
        <div className='animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500'></div>
      </div>
    );
  }
 */

  //   if (!user) return null;
  /** 
   * TODO: Implement getDisplayName function using clerk user object
  const getDisplayName = () => {
    if (user.user_metadata.full_name) {
      return user.user_metadata.full_name;
    }
    if (user.email) {
      return user.email.split('@')[0];
    }
    return 'there';
  };
*/

  const getDisplayName = () => user?.firstName || 'there';

  /**
   * TODO: Implement sendNiyoz function using supabase client
   */
  const handleDopamineClick = async () => {
    try {
      setLoading(true);
      const response = await sendNewsletterAction(
        user?.primaryEmailAddress?.emailAddress!,
      );
      if (response.preview) {
        // Demo mode: the core API built the email locally, show a link to it
        setResult(response);
      } else {
        alert(response.status ?? response.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to send dopamine hit. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='w-full items-center md:px-32'>
      {/* Header */}
      <div className='mb-4 flex items-center gap-2'>
        <h1 className='text-2xl font-bold'>Hey {getDisplayName()}</h1>
        <span role='img' aria-label='wave' className='text-2xl'>
          👋
        </span>
      </div>

      {process.env.NEXT_PUBLIC_ONBOARDING_VIDEO_URL && (
        <VideoPlayer src={process.env.NEXT_PUBLIC_ONBOARDING_VIDEO_URL} />
      )}

      {/* Confirmation Message */}
      <p className='mb-8 text-xl'>
        Thanks for signing up, your account is activated!
      </p>

      {/* Email Info */}
      <p className='mb-8 text-lg'>
        You will receive an email tomorrow morning at 8am with the summaries of
        your YouTube homepage recommendations. If you can&apos;t wait until
        then, press the Dopamine Hit button below and check your email for an
        early one ;)
      </p>

      {/* Dopamine Button */}
      <button
        onClick={handleDopamineClick}
        disabled={loading}
        className='gap-2.5 rounded-[32px] border border-solid border-blue-600 bg-blue-600 px-6 py-2 text-white shadow-[2px_3px_0px_rgba(0,0,0,1)] hover:text-black disabled:bg-blue-300 max-md:px-5'
      >
        {loading ? 'Sending...' : 'Dopamine Hit'}
      </button>

      {result?.preview && (
        <div className='mt-6 max-w-2xl rounded-2xl border border-blue-100 bg-white p-5 shadow-sm'>
          <p className='text-sm font-medium text-blue-600'>{result.status}</p>
          <p className='mt-1 text-lg font-semibold'>{result.subject}</p>
          <a
            href={result.preview}
            className='mt-3 inline-block font-medium text-blue-600 underline underline-offset-4'
          >
            Open the email
          </a>
        </div>
      )}

      {/* Contact Info */}
      <div className='my-8 flex items-center gap-2'>
        <p className='text-lg'>
          Any questions? Have ideas?{' '}
          {process.env.NEXT_PUBLIC_SUPPORT_EMAIL
            ? `Just email ${process.env.NEXT_PUBLIC_SUPPORT_EMAIL}`
            : 'Open an issue on GitHub'}
        </p>
        <span role='img' aria-label='heart' className='text-xl'>
          ❤️
        </span>
      </div>
    </div>
  );
}
