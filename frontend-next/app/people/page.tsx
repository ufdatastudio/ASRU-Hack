'use client';

import Link from 'next/link';

export default function People() {
  const teamMembers = [
    {
      name: 'Dr. Sarah Johnson',
      role: 'Chief Medical Officer',
      specialty: 'General Medicine',
      bio: 'With over 15 years of experience in healthcare, Dr. Johnson leads our medical team with expertise in preventive care and patient wellness.',
      image: '/mother.jpeg', // Using the same image for now, you can replace with team photos
    },
    {
      name: 'Dr. Michael Chen',
      role: 'Cardiologist',
      specialty: 'Cardiology',
      bio: 'Specializing in heart health and cardiovascular diseases, Dr. Chen brings advanced treatment options to our patients.',
      image: '/mother.jpeg',
    },
    {
      name: 'Dr. Emily Rodriguez',
      role: 'Pediatrician',
      specialty: 'Pediatrics',
      bio: 'Dedicated to children\'s health, Dr. Rodriguez provides compassionate care for young patients and their families.',
      image: '/mother.jpeg',
    },
    {
      name: 'Dr. James Wilson',
      role: 'Dermatologist',
      specialty: 'Dermatology',
      bio: 'Expert in skin health and dermatological conditions, Dr. Wilson helps patients achieve healthy, radiant skin.',
      image: '/mother.jpeg',
    },
    {
      name: 'Dr. Aisha Okafor',
      role: 'Public Health Specialist',
      specialty: 'Public Health',
      bio: 'Focused on community health and wellness initiatives across African communities.',
      image: '/mother.jpeg',
    },
    {
      name: 'Dr. Kwame Mensah',
      role: 'Mental Health Counselor',
      specialty: 'Mental Health',
      bio: 'Providing compassionate mental health support and therapy services.',
      image: '/mother.jpeg',
    },
  ];

  return (
    <div className="min-h-screen bg-dark-950">
      <div className="container mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
            Our People
          </h1>
          <p className="text-xl text-gray-400 max-w-3xl mx-auto">
            Meet the dedicated healthcare professionals and team members who make African health studio possible
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {teamMembers.map((member, index) => (
            <div
              key={index}
              className="bg-dark-900 rounded-xl p-6 border border-dark-800 hover:border-primary-600/50 transition-colors"
            >
              <div className="flex flex-col items-center text-center mb-4">
                <div className="relative w-32 h-32 rounded-full overflow-hidden border-4 border-primary-600/30 mb-4">
                  <img
                    src={member.image}
                    alt={member.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-semibold text-white mb-1">{member.name}</h3>
                <p className="text-primary-400 font-medium mb-1">{member.role}</p>
                <p className="text-sm text-gray-500 mb-3">{member.specialty}</p>
              </div>
              <p className="text-gray-400 text-sm leading-relaxed">{member.bio}</p>
            </div>
          ))}
        </div>

        {/* Join Us Section */}
        <div className="mt-16 bg-gradient-to-r from-primary-600/20 to-primary-800/20 rounded-2xl p-12 text-center border border-primary-600/30">
          <h2 className="text-3xl font-bold mb-4">Join Our Team</h2>
          <p className="text-gray-300 mb-8 max-w-2xl mx-auto">
            Are you a healthcare professional passionate about improving access to quality healthcare? 
            We're always looking for dedicated individuals to join our mission.
          </p>
          <Link
            href="/contact"
            className="inline-block px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-lg transition-colors shadow-lg"
          >
            Get in Touch
          </Link>
        </div>
      </div>
    </div>
  );
}

