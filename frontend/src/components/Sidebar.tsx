import React from 'react';
import {
  LayoutDashboard,
  PackageSearch,
  ShieldAlert,
  MessageSquare,
  BarChart3,
  Sliders,
  History,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab }) => {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'orders', label: 'Orders & Queue', icon: PackageSearch },
    { id: 'risk-analysis', label: 'Risk Analysis', icon: ShieldAlert },
    { id: 'whatsapp-simulator', label: 'WhatsApp Simulator', icon: MessageSquare },
    { id: 'analytics', label: 'Analytics & Trends', icon: BarChart3 },
    { id: 'configuration', label: 'Configuration', icon: Sliders },
    { id: 'decision-logs', label: 'Decision Logs', icon: History },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-logo">
          <Sparkles size={18} />
        </div>
        <div className="brand-text">
          <h1>COD Intelligence</h1>
          <span>Bliss Bloomly D2C • v1.0</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#34C78A' }}></span>
          <span>Decision Engine: Active</span>
        </div>
        <div>Model: rto-pipeline-v1.0</div>
        <div>Env: Production Demo</div>
      </div>
    </aside>
  );
};
