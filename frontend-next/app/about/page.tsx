'use client';

export default function About() {
  return (
    <div className="min-h-screen bg-dark-950">
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            About African health studio
          </h1>

          <div className="space-y-8 text-gray-300">
            <section className="bg-dark-900 rounded-xl p-8 border border-dark-800">
              <h2 className="text-2xl font-semibold mb-4 text-white">Our Mission</h2>
              <p className="leading-relaxed">
                African health studio is dedicated to making healthcare accessible and convenient for everyone. 
                We leverage cutting-edge AI technology to provide real-time medical consultations and 
                professional healthcare services through secure video conferencing.
              </p>
            </section>

            <section className="bg-dark-900 rounded-xl p-8 border border-dark-800">
              <h2 className="text-2xl font-semibold mb-4 text-white">Technology</h2>
              <p className="leading-relaxed mb-4">
                Our platform is powered by Audio Flamingo 3, an advanced AI system that enables 
                natural, conversational interactions with healthcare professionals. This technology 
                allows for seamless communication and ensures that your health concerns are 
                understood and addressed effectively.
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-400">
                <li>Real-time audio and video communication</li>
                <li>AI-powered conversation assistance</li>
                <li>Secure and encrypted data transmission</li>
                <li>High-quality audio/video processing</li>
              </ul>
            </section>

            <section className="bg-dark-900 rounded-xl p-8 border border-dark-800">
              <h2 className="text-2xl font-semibold mb-4 text-white">Our Team</h2>
              <p className="leading-relaxed">
                We are a team of healthcare professionals, engineers, and AI researchers working 
                together to revolutionize telemedicine. Our commitment is to provide you with 
                the best possible healthcare experience from the comfort of your home.
              </p>
            </section>

            <section className="bg-dark-900 rounded-xl p-8 border border-dark-800">
              <h2 className="text-2xl font-semibold mb-4 text-white">Privacy & Security</h2>
              <p className="leading-relaxed">
                Your privacy and security are our top priorities. All communications are encrypted, 
                and we comply with healthcare data protection regulations to ensure your medical 
                information remains confidential and secure.
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}

