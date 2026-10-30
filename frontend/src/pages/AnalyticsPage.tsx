import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
import { api } from '../services/apiClient';

export const AnalyticsPage: React.FC = () => {
  const [trends, setTrends] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const data = await api.getTrends();
        setTrends(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  if (loading) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-muted)' }}>Loading analytics...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Longitudinal Order Trends & Payment Modes</h2>
        <div style={{ fontSize: 13, color: 'var(--color-muted)' }}>
          Historical delivery performance tracking COD vs Prepaid cohorts over time.
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Daily Volume Chart */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>
            Daily Order Volume (COD vs Prepaid)
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="date" stroke="var(--color-muted)" fontSize={11} tickFormatter={(d) => d.slice(5)} />
                <YAxis stroke="var(--color-muted)" fontSize={11} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#26344A', borderRadius: 8, color: '#F4F7FB' }}
                  itemStyle={{ color: '#F4F7FB' }}
                  labelStyle={{ color: '#FFFFFF', fontWeight: 600, marginBottom: 4 }}
                />
                <Legend />
                <Bar dataKey="cod_orders" name="COD Orders" fill="#7C9CFF" stackId="a" />
                <Bar dataKey="prepaid_orders" name="Prepaid Orders" fill="#34C78A" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Daily RTO Rate Trend */}
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>
            Daily COD RTO Rate (%)
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <XAxis dataKey="date" stroke="var(--color-muted)" fontSize={11} tickFormatter={(d) => d.slice(5)} />
                <YAxis
                  stroke="var(--color-muted)"
                  fontSize={11}
                  tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                />
                <Tooltip
                  formatter={(val: any) => [`${(Number(val) * 100).toFixed(1)}%`, 'COD RTO Rate']}
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#F4B860', borderRadius: 8, color: '#F4F7FB' }}
                  itemStyle={{ color: '#F4B860', fontWeight: 700 }}
                  labelStyle={{ color: '#FFFFFF', fontWeight: 600, marginBottom: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="rto_rate"
                  name="COD RTO Rate"
                  stroke="#F4B860"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
