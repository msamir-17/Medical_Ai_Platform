'use client';
import { Menu, X, Activity, LogOut } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <>
      <nav className="md:hidden bg-white border-b sticky top-0 z-50">
        <div className="flex items-center justify-between p-4 h-14">
          <div className="flex items-center gap-2">
            <Activity className="text-indigo-600" />
            <span className="font-black text-lg">MediAI</span>
          </div>
          
          <button 
            onClick={() => setIsOpen(!isOpen)} 
            className="p-2 min-w-[44px] min-h-[44px] flex items-center justify-center text-slate-600 focus:outline-none rounded-lg hover:bg-slate-50"
            aria-label="Toggle navigation menu"
            aria-expanded={isOpen}
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 md:hidden" 
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Menu Overlay */}
      {isOpen && (
        <div className="fixed top-14 left-0 right-0 z-50 md:hidden bg-white shadow-2xl border-b p-6 flex flex-col gap-1">
          <Link href="/dashboard" onClick={() => setIsOpen(false)} className="font-bold text-slate-700 text-lg py-3 px-3 rounded-lg hover:bg-slate-50 min-h-[44px] flex items-center">Dashboard</Link>
          <Link href="/upload" onClick={() => setIsOpen(false)} className="font-bold text-slate-700 text-lg py-3 px-3 rounded-lg hover:bg-slate-50 min-h-[44px] flex items-center">Upload Report</Link>
          <Link href="/reports" onClick={() => setIsOpen(false)} className="font-bold text-slate-700 text-lg py-3 px-3 rounded-lg hover:bg-slate-50 min-h-[44px] flex items-center">Medical Vault</Link>
          <Link href="/chat" onClick={() => setIsOpen(false)} className="font-bold text-indigo-600 text-lg py-3 px-3 rounded-lg hover:bg-indigo-50 min-h-[44px] flex items-center">AI Chat</Link>
           
          <button 
            onClick={handleLogout}
            className="mt-4 flex items-center gap-3 text-red-500 font-bold text-lg border-t pt-6 px-3 py-3 min-h-[44px]"
          >
            <LogOut size={20} />
            Sign Out
          </button>
        </div>
      )}
    </>
  );
}