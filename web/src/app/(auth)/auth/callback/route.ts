import { NextResponse } from 'next/server';
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const redirectTo = searchParams.get('redirect_to') ?? '/dashboard';

  return NextResponse.redirect(`${process.env.SITE_URL}${redirectTo}`);
}
