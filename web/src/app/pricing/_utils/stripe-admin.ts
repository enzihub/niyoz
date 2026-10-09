import { getEnvVar } from '@/shared/utils/get-env-var';
import Stripe from 'stripe';

export const stripeAdmin = new Stripe(
  getEnvVar(process.env.STRIPE_SECRET_KEY, 'STRIPE_SECRET_KEY'),
  {
    // https://github.com/stripe/stripe-node#configuration
    apiVersion: '2025-02-24.acacia',
    // Register this as an official Stripe plugin.
    // https://stripe.com/docs/building-plugins#setappinfo
    appInfo: {
      name: 'Niyoz',
      version: '0.1.0',
    },
  },
);
