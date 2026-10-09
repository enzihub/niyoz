export default function AuthCodeErrorPage() {
  return (
    <div className='flex h-screen flex-col items-center justify-center'>
      <h1 className='text-3xl font-bold text-red-600'>Authentication Error</h1>
      <p className='mt-4 text-gray-700'>
        Something went wrong during authentication.
      </p>
      <a
        href='/signup'
        className='mt-6 rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600'
      >
        Go Back to Sign Up
      </a>
    </div>
  );
}
