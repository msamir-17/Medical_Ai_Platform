"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useMe } from '@/features/auth/useAuth';
import { LayoutDashboard, Upload, MessageSquare, FileText, HeartPulse } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { LogOut, User as UserIcon } from 'lucide-react';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Upload Report', href: '/upload', icon: Upload },
  { name: 'My Reports', href: '/reports', icon: FileText },
  { name: 'AI Chat', href: '/chat', icon: MessageSquare },
];

export function Sidebar() {
  const { data: user } = useMe(); // Fetch real user data
  const logout = useAuthStore((state) => state.logout);
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 border-r border-slate-200/80 bg-white p-4 hidden md:flex flex-col z-40">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-2 mb-8">
        <div className="w-8 h-8 rounded-lg bg-[#0F52BA] flex items-center justify-center shadow-sm">
          <HeartPulse size={18} className="text-white" />
        </div>
        <span className="text-xl font-heading font-extrabold tracking-tight text-slate-900">
          Medi<span className="text-[#0F52BA]">AI</span>
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg min-h-11 relative",
                "font-medium transition-all duration-150",
                "focus-visible:ring-2 focus-visible:ring-[#0F52BA]/20 focus-visible:outline-none",
                isActive
                  ? "bg-[#0F52BA]/[0.07] text-[#0F52BA] font-semibold before:absolute before:left-0 before:top-1/2 before:-translate-y-1/2 before:w-[3px] before:h-5 before:bg-[#0F52BA] before:rounded-r-full"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <item.icon size={20} className="shrink-0" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="pt-4 border-t border-slate-200 mt-auto">
        <div className="flex items-center gap-3 px-3 py-4">
          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 shrink-0">
            <UserIcon size={16} />
          </div>
          <div className="flex-1 overflow-hidden min-w-0">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Active Account</p>
            <p className="text-xs font-bold text-slate-700 truncate">{user?.email || "Loading..."}</p>
          </div>
        </div>
        
        <button 
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl min-h-11 text-red-500 hover:bg-red-50 transition-all font-bold text-xs focus-visible:ring-2 focus-visible:ring-red-500/20 focus-visible:outline-none"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}