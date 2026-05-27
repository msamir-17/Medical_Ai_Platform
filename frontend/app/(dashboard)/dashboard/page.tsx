export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-[--color-text-primary]">Health Overview</h1>
        <p className="text-[--color-text-secondary]">Welcome back! Here is your medical summary.</p>
      </header>

      {/* Placeholder for future cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="h-32 rounded-xl border border-[--color-border] bg-[--color-bg-secondary] animate-pulse p-4">
          <div className="h-4 w-24 bg-[--color-border] rounded mb-2"></div>
          <div className="h-8 w-16 bg-[--color-border] rounded"></div>
        </div>
        <div className="h-32 rounded-xl border border-[--color-border] bg-[--color-bg-secondary] animate-pulse p-4"></div>
        <div className="h-32 rounded-xl border border-[--color-border] bg-[--color-bg-secondary] animate-pulse p-4"></div>
      </div>
    </div>
  );
}