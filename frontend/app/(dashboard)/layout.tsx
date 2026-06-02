'use client';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { MobileNav } from '@/components/layout/MobileNav';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) 
{
  const token = useAuthStore((state) => state.token);
  const router = useRouter();

  useEffect(() => {
    // If no token, kick them back to login!
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);

  if (!token) return null; // Prevent flickering while redirecting

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[--color-bg-primary]">
      {/* 1. The Fixed Sidebar */}
      <MobileNav />
      <Sidebar />

      {/* 2. The Main Content Area */}
      <main className="flex-1 md:pl-60 p-6 lg:p-10 transition-all">
        <div className="max-w-5xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}