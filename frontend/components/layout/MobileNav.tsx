'use client';
import { Menu, X, HeartPulse, LogOut } from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/upload', label: 'Upload Report' },
    { href: '/reports', label: 'Medical Vault' },
    { href: '/chat', label: 'AI Chat' },
  ];

  return (
    <>
      <nav className="md:hidden bg-white border-b sticky top-0 z-50">
        <div className="flex items-center justify-between p-4 h-14">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-[#0F52BA] flex items-center justify-center">
              <HeartPulse size={15} className="text-white" />
            </div>
            <span className="font-heading font-extrabold text-lg text-slate-900">
              Medi<span className="text-[#0F52BA]">AI</span>
            </span>
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
          {navLinks.map((link) => {
            const isActive = pathname === link.href || pathname.startsWith(link.href + '/');
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsOpen(false)}
                className={`font-bold text-lg py-3 px-3 rounded-lg min-h-[44px] flex items-center transition-colors ${
                  isActive
                    ? 'text-[#0F52BA] bg-[#0F52BA]/[0.07]'
                    : 'text-slate-700 hover:bg-slate-50'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
           
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