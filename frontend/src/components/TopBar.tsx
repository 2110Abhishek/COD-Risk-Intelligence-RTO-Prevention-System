import React from 'react';
import { Calendar, RefreshCw, Zap } from 'lucide-react';

interface TopBarProps {
  title: string;
  subtitle?: string;
  dateFilter: string;
  setDateFilter: (val: string) => void;
  onRefresh: () => void;
  isLoading?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({
  title,
  subtitle,
  dateFilter,
  setDateFilter,
  onRefresh,
  isLoading,
}) => {
  return (
    <header className="top-bar">
      <div className="top-bar-title">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span>{title}</span>
            <span className="badge badge-low" style={{ fontSize: 11, padding: '2px 8px' }}>
              <Zap size={12} /> ML Active
            </span>
          </div>
          {subtitle && (
            <div style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 400 }}>
              {subtitle}
            </div>
          )}
        </div>
      </div>

      <div className="top-bar-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Calendar size={16} color="var(--color-muted)" />
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="select-input"
            style={{ padding: '6px 10px', fontSize: 12.5 }}
          >
            <option value="yesterday">Yesterday (Baseline Reporting)</option>
            <option value="today">Today</option>
            <option value="last_7_days">Last 7 Days</option>
            <option value="last_30_days">Last 30 Days</option>
            <option value="all">All Time History</option>
          </select>
        </div>

        <button
          onClick={onRefresh}
          className="btn btn-secondary btn-sm"
          disabled={isLoading}
          title="Refresh Data"
        >
          <RefreshCw size={14} className={isLoading ? 'spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
};
