import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { OverviewPage } from './pages/OverviewPage';
import { OrdersPage } from './pages/OrdersPage';
import { OrderDetailModal } from './pages/OrderDetailModal';
import { WhatsAppSimulatorPage } from './pages/WhatsAppSimulatorPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ConfigurationPage } from './pages/ConfigurationPage';
import { DecisionLogsPage } from './pages/DecisionLogsPage';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [dateFilter, setDateFilter] = useState<string>('yesterday');
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const getPageTitle = () => {
    switch (currentTab) {
      case 'overview':
        return { title: 'Founder Operations Overview', subtitle: 'COD Risk Intelligence & Financial Impact Console' };
      case 'orders':
        return { title: 'Orders & Risk Queue', subtitle: 'Search, filter, and inspect incoming order decisions' };
      case 'risk-analysis':
        return { title: 'ML Model & Geographic Risk Analysis', subtitle: 'Out-of-time evaluation metrics, calibration, and state trends' };
      case 'whatsapp-simulator':
        return { title: 'WhatsApp & Payment Simulator', subtitle: 'Test confirmation workflows, timeout handling, and prepaid nudges' };
      case 'analytics':
        return { title: 'Longitudinal Delivery Analytics', subtitle: 'Historical order performance and payment method comparison' };
      case 'configuration':
        return { title: 'Operational Policy Configuration', subtitle: 'Customize risk thresholds, economics, and customer safeguards' };
      case 'decision-logs':
        return { title: 'Decision Audit History', subtitle: 'Traceable audit log of every system decision and manual override' };
      default:
        return { title: 'Dashboard', subtitle: '' };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="app-layout">
      {/* Fixed Left Navigation */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Main Content View */}
      <div className="main-wrapper">
        <TopBar
          title={title}
          subtitle={subtitle}
          dateFilter={dateFilter}
          setDateFilter={setDateFilter}
          onRefresh={() => setRefreshKey((k) => k + 1)}
        />

        <main className="page-container" key={refreshKey}>
          {currentTab === 'overview' && (
            <OverviewPage
              dateFilter={dateFilter}
              onOpenOrder={(id) => setSelectedOrderId(id)}
            />
          )}

          {currentTab === 'orders' && (
            <OrdersPage
              onOpenOrder={(id) => setSelectedOrderId(id)}
            />
          )}

          {currentTab === 'risk-analysis' && <RiskAnalysisPage />}

          {currentTab === 'whatsapp-simulator' && <WhatsAppSimulatorPage />}

          {currentTab === 'analytics' && <AnalyticsPage />}

          {currentTab === 'configuration' && <ConfigurationPage />}

          {currentTab === 'decision-logs' && (
            <DecisionLogsPage
              onOpenOrder={(id) => setSelectedOrderId(id)}
            />
          )}
        </main>
      </div>

      {/* Order Detail Modal */}
      {selectedOrderId && (
        <OrderDetailModal
          orderId={selectedOrderId}
          onClose={() => setSelectedOrderId(null)}
          onRefresh={() => setRefreshKey((k) => k + 1)}
        />
      )}
    </div>
  );
};

export default App;
