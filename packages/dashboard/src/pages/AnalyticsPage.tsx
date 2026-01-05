/**
 * AnalyticsPage Component
 * Displays usage statistics and performance metrics
 */

import React from 'react';
import { Typography, Space, Alert, Row, Col } from 'antd';
import { AnalyticsDashboard } from '../components';
import type { UsageStats, PerformanceStats, PopularTopic, BloomLevelDistribution } from '../types';

const { Title, Paragraph, Text } = Typography;

const AnalyticsPage: React.FC = () => {
  // Mock data - in production, this would come from API
  const mockUsageStats: UsageStats = {
    totalCoursesGenerated: 156,
    totalQuizzesGenerated: 423,
    totalObjectivesGenerated: 892,
    averageGenerationTimeMs: 4500,
    successRate: 0.94,
  };

  const mockPerformanceStats: PerformanceStats = {
    averageResponseTimeMs: 3200,
    errorRate: 0.06,
    cacheHitRate: 0.23,
    modelVersion: 'llama2:7b',
  };

  const mockPopularTopics: PopularTopic[] = [
    { topic: 'Machine Learning Fundamentals', count: 45 },
    { topic: 'Web Development with React', count: 38 },
    { topic: 'Data Analysis with Python', count: 32 },
    { topic: 'Cloud Computing Basics', count: 28 },
    { topic: 'DevOps and CI/CD', count: 22 },
  ];

  const mockBloomDistribution: BloomLevelDistribution[] = [
    { level: 'Remember', count: 120, percentage: 13.5 },
    { level: 'Understand', count: 180, percentage: 20.2 },
    { level: 'Apply', count: 210, percentage: 23.5 },
    { level: 'Analyze', count: 175, percentage: 19.6 },
    { level: 'Evaluate', count: 130, percentage: 14.6 },
    { level: 'Create', count: 77, percentage: 8.6 },
  ];

  return (
    <div className="analytics-page">
      <Title level={3}>Analytics Dashboard</Title>
      <Paragraph type="secondary">
        View usage statistics, performance metrics, and learning objective distribution.
      </Paragraph>

      <Alert
        message="Demo Mode"
        description="This page shows sample analytics data. Connect to your API to see real metrics."
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <AnalyticsDashboard
        usageStats={mockUsageStats}
        performanceStats={mockPerformanceStats}
        popularTopics={mockPopularTopics}
        bloomDistribution={mockBloomDistribution}
        loading={false}
      />

      <style>{`
        .analytics-page {
          width: 100%;
        }
      `}</style>
    </div>
  );
};

export default AnalyticsPage;
