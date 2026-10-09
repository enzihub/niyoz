import React from 'react';
import ReactMarkdown from 'react-markdown';

const markdownComponents = {
  h1: ({ children }: any) => (
    <h1 className='mb-8 text-center text-3xl font-medium tracking-tight text-gray-900 md:text-4xl'>
      {children}
    </h1>
  ),
  h2: ({ children }: any) => (
    <h2 className='mb-4 border-b border-gray-300 pb-2 text-xl font-medium tracking-tight text-gray-800 md:text-2xl'>
      {children}
    </h2>
  ),
  h3: ({ children }: any) => (
    <h3 className='mb-3 text-lg font-medium tracking-tight text-gray-700 md:text-xl'>
      {children}
    </h3>
  ),
  p: ({ children }: any) => (
    <p className='mb-6 text-sm leading-relaxed text-gray-600 md:text-base'>
      {children}
    </p>
  ),
  ul: ({ children }: any) => (
    <ul className='mb-6 ml-4 list-outside list-disc text-sm text-gray-600 md:text-base'>
      {children}
    </ul>
  ),
  ol: ({ children }: any) => (
    <ol className='mb-6 ml-4 list-outside list-decimal text-sm text-gray-600 md:text-base'>
      {children}
    </ol>
  ),
  li: ({ children }: any) => <li className='mb-2'>{children}</li>,
  hr: () => <hr className='my-8 border-gray-300' />,
};

export default function PrivacyPolicy() {
  const markdownContent = `
  # Privacy Policy for Niyoz  
  
  **Effective Date:** November 26, 2024  
  
  At Niyoz, we value your privacy and are committed to protecting your personal information. This Privacy Policy outlines how we collect, use, and share information when you use our services, including but not limited to email updates and any associated mobile or web applications.  
  
  ---
  
  ## 1. Information We Collect  
  
  ### 1.1 Information You Provide Directly  
  - **Personal Information:** When you sign up for Niyoz, we collect information such as your name and email address.  
  - **Feedback:** If you contact us or provide feedback, we collect the information you share with us.  
  
  ### 1.2 Information Collected Automatically  
  - **Usage Data:** When you interact with our website or app, we may collect non-identifiable information such as browser type, operating system, and timestamps.  
  - **Cookies:** We use cookies to improve your experience, track preferences, and analyze traffic.  
  
  ---
  
  ## 2. How We Use Your Information  
  We use the information collected for the following purposes:  
  - To deliver Niyoz email updates.  
  - To improve and personalize our services.  
  - To communicate with you about your account or service updates.  
  - To analyze trends and gather insights to enhance the user experience.  
  
  ---
  
  ## 3. How We Share Your Information  
  We do not sell your personal information. We may share your data with third parties in the following cases:  
  - **Service Providers:** To deliver emails, analyze user behavior, or manage infrastructure.  
  - **Legal Obligations:** If required by law or to protect our rights.  
  - **With Your Consent:** When you explicitly agree to share your information.  
  
  ---
  
  ## 4. Google API Services  
  Niyoz may use Google API Services to enhance our offerings. By using our services:  
  - You agree to Google’s Privacy Policy ([link to Google's Privacy Policy](https://policies.google.com/privacy)).  
  - We will only access and use Google API data in ways that are compliant with Google’s API Services User Data Policy ([link to Google API Policy](https://developers.google.com/terms)).  
  - We will not share or use your data for advertising purposes without your explicit consent.  
  
  ---
  
  ## 5. Data Retention  
  We retain your information only as long as necessary to provide our services or as required by law. You can request deletion of your data by contacting us.  
  
  ---
  
  ## 6. Your Rights  
  - **Access and Update:** You can access or update your personal information at any time.  
  - **Opt-Out:** You can unsubscribe from emails using the link provided in each message.  
  - **Data Deletion:** Contact us to request the deletion of your data.  
  
  ---
  
  ## 7. Security  
  We implement industry-standard security measures to protect your data. However, no method of transmission or storage is completely secure, and we cannot guarantee absolute security.  
  
  ---
  
  ## 8. Third-Party Links  
  Our emails or app may contain links to third-party websites or services. We are not responsible for their privacy practices or content.  
  
  ---
  
  ## 9. Changes to This Privacy Policy  
  We may update this policy from time to time. Changes will be communicated through email or our website.  
  
  ---
  
  ## 10. Contact Us  
  If you have questions or concerns about this Privacy Policy, contact us at:  
  **Email:** the support address published by the operator of this deployment  
  **Address:**  
  30 N Gould St Ste N  
  Sheridan, Wyoming 82801  
  USA  
  
  ---  
  
    `;

  return (
    <div className='w-full'>
      <div className='mx-auto max-w-3xl bg-white px-4 md:px-6'>
        <div className='mb-16 mt-16 rounded-lg'>
          <div className='scrollbar-thin scrollbar-thumb-gray-700 hover:scrollbar-thumb-gray-600 scrollbar-track-transparent overflow-y-auto px-6 py-8 md:px-8'>
            <div className='prose prose-invert max-w-none'>
              <ReactMarkdown components={markdownComponents}>
                {markdownContent}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
