/**
 * Main App Component
 * Application entry point with routing and providers
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { MainLayout } from './components';
import { HomePage, AnalyticsPage, SettingsPage } from './pages';
import { useHealthCheck } from './hooks';

const App: React.FC = () => {
  const { data: healthData } = useHealthCheck();

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#3B82F6',
          borderRadius: 8,
        },
        components: {
          Card: {
            headerBg: 'transparent',
          },
        },
      }}
    >
      <BrowserRouter>
        <MainLayout healthStatus={healthData}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<HomePage />} />
            <Route path="/courses" element={<HomePage />} />
            <Route path="/quiz" element={<HomePage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </ConfigProvider>
  );
};

export default App;
