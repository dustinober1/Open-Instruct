/**
 * ObjectivesDisplay Component
 * Displays generated learning objectives with Bloom's level color coding
 */

import React, { useState } from 'react';
import {
  Table,
  Tag,
  Button,
  Card,
  Space,
  Typography,
  Tooltip,
  Dropdown,
  Modal,
  message,
  Empty,
  Badge,
} from 'antd';
import {
  DownloadOutlined,
  ExportOutlined,
  CopyOutlined,
  CheckCircleOutlined,
  FileTextOutlined,
  EyeOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { LearningObjectiveResponse } from '../types';
import {
  getBloomLevelColor,
  getBloomLevelOrder,
  exportToJson,
  exportToCsv,
} from '../utils';

const { Title, Text, Paragraph } = Typography;

interface ObjectivesDisplayProps {
  objectives: LearningObjectiveResponse[];
  topic?: string;
  loading?: boolean;
  onQuizGenerate?: (objectiveId: string) => void;
  onExport?: (format: 'json' | 'csv') => void;
}

const ObjectivesDisplay: React.FC<ObjectivesDisplayProps> = ({
  objectives,
  topic,
  loading = false,
  onQuizGenerate,
  onExport,
}) => {
  const [messageApi, contextHolder] = message.useMessage();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  if (objectives.length === 0) {
    return (
      <Card bordered={false}>
        <Empty
          description="No objectives to display"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  const handleCopyAll = () => {
    const text = objectives
      .map((obj) => `${obj.id}: ${obj.verb} ${obj.content} [${obj.level}]`)
      .join('\n');
    navigator.clipboard.writeText(text);
    messageApi.success('All objectives copied to clipboard');
  };

  const handleExportJson = () => {
    const data = objectives.map((obj) => ({
      id: obj.id,
      verb: obj.verb,
      content: obj.content,
      level: obj.level,
      explanation: obj.explanation,
    }));
    exportToJson(data, topic ? `${topic.replace(/\s+/g, '_')}_objectives` : 'objectives');
    messageApi.success('Exported to JSON');
    onExport?.('json');
  };

  const handleExportCsv = () => {
    const data = objectives.map((obj) => ({
      ID: obj.id,
      Verb: obj.verb,
      Content: obj.content,
      BloomLevel: obj.level,
      Explanation: obj.explanation || '',
    }));
    exportToCsv(data, topic ? `${topic.replace(/\s+/g, '_')}_objectives` : 'objectives');
    messageApi.success('Exported to CSV');
    onExport?.('csv');
  };

  const handleRowExport = (record: LearningObjectiveResponse) => ({
    onClick: () => {
      exportToJson([record], `objective_${record.id}`);
      messageApi.success(`Exported objective ${record.id}`);
    },
  });

  const columns: ColumnsType<LearningObjectiveResponse> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: (a, b) => a.id.localeCompare(b.id),
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 120,
      sorter: (a, b) => getBloomLevelOrder(a.level as any) - getBloomLevelOrder(b.level as any),
      render: (level: string) => {
        const color = getBloomLevelColor(level as any);
        return (
          <Tag color={color} style={{ fontWeight: 500 }}>
            {level}
          </Tag>
        );
      },
    },
    {
      title: 'Verb',
      dataIndex: 'verb',
      key: 'verb',
      width: 120,
      sorter: (a, b) => a.verb.localeCompare(b.verb),
    },
    {
      title: 'Learning Objective',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Tooltip title="Generate Quiz">
            <Button
              type="text"
              icon={<FileTextOutlined />}
              onClick={() => onQuizGenerate?.(record.id)}
            />
          </Tooltip>
          <Dropdown
            menu={{
              items: [
                {
                  key: 'copy',
                  icon: <CopyOutlined />,
                  label: 'Copy',
                  onClick: () => {
                    navigator.clipboard.writeText(
                      `${record.verb} ${record.content} [${record.level}]`
                    );
                    messageApi.success('Copied to clipboard');
                  },
                },
                {
                  key: 'export',
                  icon: <DownloadOutlined />,
                  label: 'Export JSON',
                  onClick: handleRowExport(record).onClick,
                },
              ],
            }}
            trigger={['click']}
          >
            <Button type="text" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      ),
    },
  ];

  const rowSelection = {
    selectedRowKeys,
    onChange: (keys: React.Key[]) => setSelectedRowKeys(keys),
  };

  const exportMenuItems = [
    {
      key: 'json',
      icon: <DownloadOutlined />,
      label: 'Export as JSON',
      onClick: handleExportJson,
    },
    {
      key: 'csv',
      icon: <DownloadOutlined />,
      label: 'Export as CSV',
      onClick: handleExportCsv,
    },
  ];

  return (
    <>
      {contextHolder}
      <Card
        className="objectives-display"
        bordered={false}
        loading={loading}
      >
        <div className="card-header">
          <div>
            <Title level={5} style={{ margin: 0 }}>
              <CheckCircleOutlined style={{ marginRight: 8, color: '#52c41a' }} />
              Generated Learning Objectives
            </Title>
            {topic && (
              <Text type="secondary" style={{ marginTop: 4, display: 'block' }}>
                Topic: <Text strong>{topic}</Text>
              </Text>
            )}
          </div>
          <Space wrap>
            <Button icon={<CopyOutlined />} onClick={handleCopyAll}>
              Copy All
            </Button>
            <Dropdown menu={{ items: exportMenuItems }}>
              <Button icon={<ExportOutlined />}>Export</Button>
            </Dropdown>
          </Space>
        </div>

        <div style={{ marginTop: 16 }}>
          <Badge count={objectives.length} showZero color="#52c41a">
            <Text strong>Total Objectives</Text>
          </Badge>
        </div>

        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={objectives.map((obj, index) => ({ ...obj, key: obj.id || index }))}
          pagination={false}
          scroll={{ x: 800 }}
          size="middle"
          rowClassName={(record) =>
            selectedRowKeys.includes(record.id) ? 'selected-row' : ''
          }
        />

        <style>{`
          .objectives-display {
            background: #fff;
            border-radius: 8px;
            margin-top: 16px;
          }
          .objectives-display .card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 16px;
          }
          .objectives-display .selected-row {
            background-color: #e6f7ff;
          }
          .objectives-display .ant-table-thead > tr > th {
            background-color: #fafafa;
            font-weight: 600;
          }
        `}</style>
      </Card>
    </>
  );
};

export default ObjectivesDisplay;
