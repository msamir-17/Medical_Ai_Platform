'use client';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Sidebar } from '@/components/layout/Sidebar';
import { MobileNav } from '@/components/layout/MobileNav';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) 
{
  const { token, _hasHydrated } = useAuthStore();
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (_hasHydrated && !token) {
      router.push('/login');
    }
  }, [_hasHydrated, token, router]);

  if (!isClient || !_hasHydrated) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-white">
        <Loader2 className="animate-spin text-indigo-600" size={40} />
      </div>
    );
  }

  if (!token) return null;

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-gray-50/40">
      <MobileNav />
      <Sidebar />

      {/*
        IMPORTANT: On md+ the sidebar is `fixed w-60` (240px).
        We must NOT let shorthand `p-*` override `pl-60`.
        So we set left padding separately via ml-60 on md+,
        and use pr/pt/pb for the content breathing room.
      */}
      <main className="
        flex-1
        min-h-[calc(100vh-56px)] md:min-h-screen
        p-4
        md:ml-60 md:p-6
        lg:p-10
        transition-all duration-200
      ">
        <div className="max-w-6xl 2xl:max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}