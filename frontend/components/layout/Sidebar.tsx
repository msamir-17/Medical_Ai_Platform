"use client";

import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, Upload, MessageSquare, FileText, Settings } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';
import { LogOut, User as UserIcon } from 'lucide-react';
// Helper for clean tailwind classes
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
    const logout = useAuthStore((state) => state.logout);
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };
  return (
    <aside className="fixed left-0 top-0 h-screen w-60 border-r border-[--color-border] bg-[--color-bg-secondary] p-4 hidden md:flex flex-col">
      <div className="flex items-center gap-2 px-2 mb-8">
        <div className="h-8 w-8 rounded-lg bg-[--color-primary-500] flex items-center justify-center">
          <span className="text-white font-bold">M</span>
        </div>
        <span className="text-xl font-bold tracking-tight">MediAI</span>
      </div>


      <nav className="flex-1 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-lg text-[--color-text-secondary] transition-colors",
              "hover:bg-[--color-bg-tertiary] hover:text-[--color-text-primary]"
            )}
          >
            <item.icon size={20} />
            <span className="font-medium">{item.name}</span>
          </Link>
        ))}
      </nav>


       <div className="pt-4 border-t border-slate-200 mt-auto">
        <div className="flex items-center gap-3 px-3 py-4">
          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
            <UserIcon size={16} />
          </div>
          <div className="flex-1 overflow-hidden">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Active Account</p>
            <p className="text-xs font-bold text-slate-700 truncate">Patient User</p> 
            {/* Later we can fetch real email here */}
          </div>
        </div>
        
        <button 
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-red-500 hover:bg-red-50 transition-all font-bold text-xs"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>

    </aside>
  );
}