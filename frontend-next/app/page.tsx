'use client';

import Link from 'next/link';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="min-h-screen bg-dark-950">
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <div className="mb-8 flex justify-center">
            <div className="relative w-48 h-48 rounded-full overflow-hidden border-4 border-primary-600/30 shadow-2xl">
              <Image
                src="/mother.jpeg"
                alt="African health studio"
                fill
                className="object-cover"
                priority
              />
            </div>
          </div>
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            Welcome to African health studio
          </h1>
          <p className="text-xl text-gray-400 mb-4">
            Dedicated mental health support for Africa - accessible, compassionate, and culturally aware
          </p>
          <p className="text-lg text-gray-500 mb-12">
            Your safe space for mental wellness, connecting you with AI-powered support and professional care
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/talk-to-ai"
              className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors shadow-lg"
            >
              Talk to AI
            </Link>
            <Link
              href="/talk-to-doctor"
              className="px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors shadow-lg"
            >
              Talk to Doctor
            </Link>
            <Link
              href="/book-appointment"
              className="px-8 py-4 bg-dark-800 hover:bg-dark-700 text-white font-semibold rounded-lg transition-colors border border-dark-700"
            >
              Book Appointment
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-dark-900 rounded-xl p-8 border border-dark-800">
            <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Talk to AI</h3>
            <p className="text-gray-400 mb-4">
              Get immediate mental health support through confidential AI conversations. Share your thoughts and feelings in a safe, judgment-free space.
            </p>
            <Link href="/talk-to-ai" className="text-primary-400 hover:text-primary-300 text-sm font-medium">
              Start AI chat →
            </Link>
          </div>

          <div className="bg-dark-900 rounded-xl p-8 border border-dark-800">
            <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Talk to Doctor</h3>
            <p className="text-gray-400 mb-4">
              Connect with licensed mental health professionals who understand African cultural contexts and provide personalized care
            </p>
            <Link href="/talk-to-doctor" className="text-primary-400 hover:text-primary-300 text-sm font-medium">
              Start consultation →
            </Link>
          </div>

          <div className="bg-dark-900 rounded-xl p-8 border border-dark-800">
            <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Easy Scheduling</h3>
            <p className="text-gray-400">
              Book mental health consultations at your convenience, whenever you need support
            </p>
          </div>

          <div className="bg-dark-900 rounded-xl p-8 border border-dark-800">
            <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Secure & Private</h3>
            <p className="text-gray-400">
              Your mental health conversations are completely confidential and protected with end-to-end encryption
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-16">
        <div className="bg-gradient-to-r from-primary-600/20 to-primary-800/20 rounded-2xl p-12 text-center border border-primary-600/30">
          <h2 className="text-3xl font-bold mb-4">Your mental health matters</h2>
          <p className="text-gray-300 mb-2">Take the first step towards better mental wellness</p>
          <p className="text-gray-400 mb-8">We're here to support you on your journey - accessible, affordable, and culturally sensitive</p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/talk-to-ai"
              className="inline-block px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors shadow-lg"
            >
              Get Support Now
            </Link>
            <Link
              href="/talk-to-doctor"
              className="inline-block px-8 py-4 bg-dark-800 hover:bg-dark-700 text-white font-semibold rounded-lg transition-colors border border-dark-700"
            >
              Book Professional Consultation
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
