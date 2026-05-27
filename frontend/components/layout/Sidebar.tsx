import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, Upload, MessageSquare, FileText, Settings } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

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

      <div className="pt-4 border-t border-[--color-border]">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-[--color-text-secondary] hover:bg-[--color-bg-tertiary] hover:text-[--color-text-primary]"
        >
          <Settings size={20} />
          <span className="font-medium">Settings</span>
        </Link>
      </div>
    </aside>
  );
}