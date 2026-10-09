import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';
import { checkIfSubscriptionExistsForClerkId } from '@/app/pricing/_services/subscription-service';

// Define route matchers
const isProtectedRoute = createRouteMatcher([
  '/dashboard(.*)',
  '/settings(.*)',
]);
const isAuthPage = createRouteMatcher(['/login', '/signup']);
const isPublicPage = createRouteMatcher([
  '/',
  '/pricing',
  '/tos',
  '/privacy-policy',
  '/api/webhooks(.*)',
  '/api/(.*)',
]);

export default clerkMiddleware(async (auth, req) => {
  const { userId } = await auth();
  const path = req.nextUrl.pathname;

  // Allow unauthenticated access to public routes and API webhooks
  if (isPublicPage(req)) {
    // Special handling for root ('/')
    if (path === '/') {
      if (userId) {
        const hasSubscription =
          await checkIfSubscriptionExistsForClerkId(userId);
        return NextResponse.redirect(
          new URL(hasSubscription ? '/dashboard' : '/pricing', req.url),
        );
      } else {
        return NextResponse.redirect(new URL('/login', req.url));
      }
    }

    // Special handling for pricing page - redirect to dashboard if user has subscription
    if (path === '/pricing' && userId) {
      const hasSubscription = await checkIfSubscriptionExistsForClerkId(userId);
      if (hasSubscription) {
        return NextResponse.redirect(new URL('/dashboard', req.url));
      }
    }

    return NextResponse.next();
  }

  // Redirect logged-in users away from login/signup pages
  if (userId && isAuthPage(req)) {
    return NextResponse.redirect(new URL('/dashboard', req.url));
  }

  // Redirect unauthenticated users from protected routes
  if (!userId && isProtectedRoute(req)) {
    return NextResponse.redirect(new URL('/login', req.url));
  }

  // If user is logged in but lacks an active subscription, redirect to pricing
  if (userId) {
    const hasSubscription = await checkIfSubscriptionExistsForClerkId(userId);
    if (!hasSubscription && !path.startsWith('/pricing')) {
      return NextResponse.redirect(new URL('/pricing', req.url));
    }
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
