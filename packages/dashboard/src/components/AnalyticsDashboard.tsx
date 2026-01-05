/**
 * AnalyticsDashboard Component
 * Displays usage statistics, performance metrics, and charts
 */

import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Space,
  Progress,
  Spin,
  Empty,
  Table,
  Tag,
} from 'antd';
import {
  BookOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  FallOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts';
import type {
  UsageStats,
  PerformanceStats,
  PopularTopic,
  BloomLevelDistribution,
} from '../types';
import { getBloomLevelColor, formatDuration } from '../utils';

const { Title, Text, Paragraph } = Typography;

interface AnalyticsDashboardProps {
  usageStats?: UsageStats | null;
  performanceStats?: PerformanceStats | null;
  popularTopics?: PopularTopic[] | null;
  bloomDistribution?: BloomLevelDistribution[] | null;
  loading?: boolean;
}

const COLORS = ['#8B5CF6', '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#EC4899'];

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  usageStats,
  performanceStats,
  popularTopics,
  bloomDistribution,
  loading = false,
}) => {
  if (loading) {
    return (
      <Card bordered={false}>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>Loading analytics...</Paragraph>
        </div>
      </Card>
    );
  }

  const hasData = usageStats || performanceStats || popularTopics || bloomDistribution;

  if (!hasData) {
    return (
      <Card bordered={false}>
        <Empty
          description="No analytics data available"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  const topicColumns = [
    {
      title: 'Topic',
      dataIndex: 'topic',
      key: 'topic',
      ellipsis: true,
    },
    {
      title: 'Generations',
      dataIndex: 'count',
      key: 'count',
      width: 120,
      sorter: (a: PopularTopic, b: PopularTopic) => b.count - a.count,
    },
  ];

  return (
    <div className="analytics-dashboard">
      <Row gutter={[16, 16]}>
        {/* Usage Stats */}
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="Courses Generated"
              value={usageStats?.totalCoursesGenerated || 0}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#3B82F6' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="Quizzes Created"
              value={usageStats?.totalQuizzesGenerated || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#10B981' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="Avg. Generation Time"
              value={formatDuration(usageStats?.averageGenerationTimeMs || 0)}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#F59E0B' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="Success Rate"
              value={usageStats?.successRate ? (usageStats.successRate * 100).toFixed(1) : 0}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{
                color: (usageStats?.successRate || 0) >= 0.9 ? '#10B981' : '#F59E0B',
              }}
            />
          </Card>
        </Col>

        {/* Performance Stats */}
        <Col xs={24} sm={8}>
          <Card bordered={false} className="stat-card">
            <Statistic
              title="Avg Response Time"
              value={formatDuration(performanceStats?.averageResponseTimeMs || 0)}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card bordered={false} className="stat-card">
            <div className="stat-with-progress">
              <Text type="secondary">Error Rate</Text>
              <Title level={4} style={{ margin: '4px 0' }}>
                {performanceStats?.errorRate ? `${(performanceStats.errorRate * 100).toFixed(1)}%` : '0%'}
              </Title>
              <Progress
                percent={(performanceStats?.errorRate || 0) * 100}
                showInfo={false}
                status="exception"
                size="small"
              />
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card bordered={false} className="stat-card">
            <div className="stat-with-progress">
              <Text type="secondary">Cache Hit Rate</Text>
              <Title level={4} style={{ margin: '4px 0' }}>
                {performanceStats?.cacheHitRate ? `${(performanceStats.cacheHitRate * 100).toFixed(1)}%` : '0%'}
              </Title>
              <Progress
                percent={(performanceStats?.cacheHitRate || 0) * 100}
                showInfo={false}
                status="active"
                size="small"
              />
            </div>
          </Card>
        </Col>

        {/* Bloom's Level Distribution */}
        <Col xs={24} lg={12}>
          <Card bordered={false} title="Bloom's Level Distribution" className="chart-card">
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={bloomDistribution || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="level" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3B82F6">
                    {bloomDistribution?.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={getBloomLevelColor(entry.level as any)}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>

        {/* Popular Topics */}
        <Col xs={24} lg={12}>
          <Card bordered={false} title="Popular Topics" className="chart-card">
            <Table
              columns={topicColumns}
              dataSource={popularTopics || []}
              pagination={false}
              size="small"
              rowKey="topic"
            />
          </Card>
        </Col>

        {/* Level Pie Chart */}
        <Col xs={24}>
          <Card bordered={false} title="Objectives by Cognitive Level" className="chart-card">
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={bloomDistribution || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ level, percentage }) => `${level}: ${percentage}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                    nameKey="level"
                  >
                    {bloomDistribution?.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={getBloomLevelColor(entry.level as any)}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>

      <style>{`
        .analytics-dashboard .stat-card {
          border-radius: 8px;
          background: #fff;
        }
        .analytics-dashboard .chart-card {
          border-radius: 8px;
          background: #fff;
        }
        .analytics-dashboard .stat-with-progress {
          text-align: left;
        }
      `}</style>
    </div>
  );
};

export default AnalyticsDashboard;
