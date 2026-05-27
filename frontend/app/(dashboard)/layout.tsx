import { Sidebar } from '@/components/layout/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex bg-[--color-bg-primary]">
      {/* 1. The Fixed Sidebar */}
      <Sidebar />

      {/* 2. The Main Content Area */}
      <main className="flex-1 md:ml-60 p-6 lg:p-10">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}