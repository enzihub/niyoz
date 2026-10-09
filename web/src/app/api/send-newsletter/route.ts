import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';
import { getUserIdByClerkId } from '@/app/(user)/_services/user.service';

const DEFAULT_API_URL = process.env.NIYOZ_DEV_API_URL || 'http://127.0.0.1:8000';

export async function POST(request: Request) {
  try {
    // Parse request body
    const { email } = await request.json();

    // Validate email presence
    if (!email) {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 });
    }

    // Forward request to external API
    const response = await fetch(`${DEFAULT_API_URL}/send-newsletter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(process.env.NIYOZ_DEV_API_KEY && {
          'X-Api-Key': process.env.NIYOZ_DEV_API_KEY,
        }),
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: errorText },
        { status: response.status },
      );
    }

    const data = await response.json();
    if (data.preview) data.preview = '/api/demo-email';
    return NextResponse.json(data);
  } catch (error) {
    console.error('[NEWSLETTER_API_ERROR]', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 },
    );
  }
}
