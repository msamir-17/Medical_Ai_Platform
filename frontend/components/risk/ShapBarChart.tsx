'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function ShapBarChart({ data }: { data: any[] }) {
  // Data format example: [{ feature: 'Glucose', contribution: 42 }, { feature: 'BMI', contribution: -10 }]
  
  return (
    <div className="w-full mt-4 md:mt-6">
      <h4 className="text-xs md:text-sm font-bold text-[--color-text-secondary] mb-3 md:mb-4 uppercase tracking-tight">
        Feature Impact (SHAP)
      </h4>
      {/* Responsive height: compact on mobile, taller on desktop */}
      <div className="h-48 md:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={data} 
            layout="vertical" 
            margin={{ left: 0, right: 8, top: 4, bottom: 4 }}
          >
            <XAxis type="number" hide />
            <YAxis 
              dataKey="feature" 
              type="category" 
              width={70}
              tick={{ fontSize: 10, fontWeight: 600, fill: 'var(--color-text-secondary)' }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip 
              contentStyle={{ 
                borderRadius: '8px', 
                border: '1px solid var(--color-border)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.contribution > 0 ? '#EF4444' : '#10B981'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}