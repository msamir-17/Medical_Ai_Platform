'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function ShapBarChart({ data }: { data: any[] }) {
  // Data format example: [{ feature: 'Glucose', contribution: 42 }, { feature: 'BMI', contribution: -10 }]
  
  return (
    <div className="h-64 w-full mt-6">
      <h4 className="text-sm font-bold text-slate-700 mb-4 uppercase tracking-tighter">Feature Impact (SHAP)</h4>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <XAxis type="number" hide />
          <YAxis dataKey="feature" type="category" width={80} style={{ fontSize: '10px', fontWeight: 'bold' }} />
          <Tooltip />
          <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.contribution > 0 ? '#EF4444' : '#10B981'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}