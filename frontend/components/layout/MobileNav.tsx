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
    <nav className="md:hidden bg-white border-b sticky top-0 z-50">
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-2">
          <Activity className="text-indigo-600" />
          <span className="font-black text-lg">MediAI</span>
        </div>
        
        <button onClick={() => setIsOpen(!isOpen)} className="p-2 text-slate-600 focus:outline-none">
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div className="absolute top-full left-0 w-full bg-white shadow-2xl border-b p-6 flex flex-col gap-6 animate-in slide-in-from-top-2 duration-200">
           <Link href="/dashboard" onClick={() => setIsOpen(false)} className="font-bold text-slate-700 text-lg">Dashboard</Link>
           <Link href="/upload" onClick={() => setIsOpen(false)} className="font-bold text-slate-700 text-lg">Upload Report</Link>
           <Link href="/reports" onClick={() => setIsOpen(false)} className="font-bold text-slate-700 text-lg">Medical Vault</Link>
           <Link href="/chat" onClick={() => setIsOpen(false)} className="font-bold text-indigo-600 text-lg">AI Chat</Link>
           
           {/* SIGN OUT BUTTON FOR MOBILE */}
           <button 
             onClick={handleLogout}
             className="mt-4 flex items-center gap-3 text-red-500 font-bold text-lg border-t pt-6"
           >
             <LogOut size={20} />
             Sign Out
           </button>
        </div>
      )}
    </nav>
  );
}