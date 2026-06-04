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
  const { token, _hasHydrated } = useAuthStore(); // Get both token and hydration status
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    // SIRF tab redirect karo jab store load ho chuka ho AUR token missing ho
    if (_hasHydrated && !token) {
      router.push('/login');
    }
  }, [_hasHydrated, token, router]);

    // Jab tak hydration complete nahi hoti, tab tak loader dikhao
  if (!isClient || !_hasHydrated) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-white">
        <Loader2 className="animate-spin text-indigo-600" size={40} />
      </div>
    );
  }

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