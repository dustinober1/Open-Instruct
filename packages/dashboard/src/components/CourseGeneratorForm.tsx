/**
 * CourseGeneratorForm Component
 * Form for generating learning objectives based on topic and target audience
 */

import React, { useState } from 'react';
import {
  Form,
  Input,
  Slider,
  Button,
  Card,
  Select,
  Space,
  Typography,
  Alert,
  Divider,
  Tooltip,
  Progress,
} from 'antd';
import {
  RocketOutlined,
  InfoCircleOutlined,
  BookOutlined,
  UserOutlined,
  NumberOutlined,
} from '@ant-design/icons';
import type { GenerateObjectivesRequest, GenerationProgress } from '../types';
import { validateTopic, validateTargetAudience, validateNumObjectives } from '../utils';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface CourseGeneratorFormProps {
  onGenerate: (request: GenerateObjectivesRequest) => Promise<void>;
  loading?: boolean;
  progress?: GenerationProgress;
  error?: string | null;
}

const targetAudienceOptions = [
  { value: 'beginners', label: 'Beginners' },
  { value: 'intermediate', label: 'Intermediate Learners' },
  { value: 'advanced', label: 'Advanced Learners' },
  { value: 'professionals', label: 'Professionals' },
  { value: 'students', label: 'Students' },
  { value: 'teachers', label: 'Teachers/Instructors' },
  { value: 'researchers', label: 'Researchers' },
  { value: 'general', label: 'General Audience' },
];

const CourseGeneratorForm: React.FC<CourseGeneratorFormProps> = ({
  onGenerate,
  loading = false,
  progress,
  error,
}) => {
  const [form] = Form.useForm();
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const topicValue = Form.useWatch('topic', form);
  const audienceValue = Form.useWatch('targetAudience', form);
  const numObjectivesValue = Form.useWatch('numObjectives', form);

  const handleFinish = async (values: GenerateObjectivesRequest) => {
    // Validate before submitting
    const topicError = validateTopic(values.topic);
    const audienceError = validateTargetAudience(values.targetAudience);
    const numError = validateNumObjectives(values.numObjectives);

    if (topicError || audienceError || numError) {
      setFormErrors({
        topic: topicError || '',
        targetAudience: audienceError || '',
        numObjectives: numError || '',
      });
      return;
    }

    setFormErrors({});
    await onGenerate(values);
  };

  const isProgressComplete = progress?.stage === 'complete';

  return (
    <Card className="course-generator-form" bordered={false}>
      <Title level={4}>
        <RocketOutlined style={{ marginRight: 8 }} />
        Generate Learning Objectives
      </Title>
      <Paragraph type="secondary">
        Enter a topic and target audience to generate Bloom's Taxonomy-aligned learning objectives.
      </Paragraph>

      <Divider />

      {error && (
        <Alert
          message="Generation Failed"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      {progress && progress.stage !== 'idle' && (
        <Card
          size="small"
          style={{ marginBottom: 16, backgroundColor: '#f5f5f5' }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>Status: </Text>
              <Text
                style={{
                  color:
                    progress.stage === 'error'
                      ? '#ff4d4f'
                      : progress.stage === 'complete'
                      ? '#52c41a'
                      : undefined,
                }}
              >
                {progress.message}
              </Text>
            </div>
            {progress.stage !== 'error' && progress.stage !== 'complete' && (
              <Progress
                percent={progress.progress}
                status="active"
                size="small"
              />
            )}
            {progress.error && (
              <Alert
                message="Suggestion"
                description={progress.error}
                type="warning"
                showIcon
                size="small"
              />
            )}
          </Space>
        </Card>
      )}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        disabled={loading || isProgressComplete}
        initialValues={{
          numObjectives: 6,
          targetAudience: 'beginners',
        }}
      >
        <Form.Item
          name="topic"
          label={
            <Space>
              <BookOutlined />
              <span>Topic</span>
              <Tooltip title="The subject or skill you want to teach">
                <InfoCircleOutlined style={{ color: '#999' }} />
              </Tooltip>
            </Space>
          }
          validateStatus={formErrors.topic ? 'error' : ''}
          help={formErrors.topic}
          rules={[{ required: true, message: 'Please enter a topic' }]}
        >
          <TextArea
            placeholder="e.g., Machine Learning Fundamentals, Web Development with React, Data Analysis with Python"
            rows={3}
            showCount
            maxLength={200}
          />
        </Form.Item>

        <Form.Item
          name="targetAudience"
          label={
            <Space>
              <UserOutlined />
              <span>Target Audience</span>
              <Tooltip title="Who is this course designed for">
                <InfoCircleOutlined style={{ color: '#999' }} />
              </Tooltip>
            </Space>
          }
          validateStatus={formErrors.targetAudience ? 'error' : ''}
          help={formErrors.targetAudience}
          rules={[{ required: true, message: 'Please select a target audience' }]}
        >
          <Select
            placeholder="Select target audience"
            options={targetAudienceOptions}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '')
                .toLowerCase()
                .includes(input.toLowerCase())
            }
          />
        </Form.Item>

        <Form.Item
          name="numObjectives"
          label={
            <Space>
              <NumberOutlined />
              <span>Number of Objectives</span>
              <Tooltip title="How many learning objectives to generate (1-12)">
                <InfoCircleOutlined style={{ color: '#999' }} />
              </Tooltip>
            </Space>
          }
          validateStatus={formErrors.numObjectives ? 'error' : ''}
          help={formErrors.numObjectives}
          rules={[{ required: true, message: 'Please select number of objectives' }]}
        >
          <Slider
            min={1}
            max={12}
            marks={{
              1: '1',
              3: '3',
              6: '6',
              9: '9',
              12: '12',
            }}
            tooltip={{
              formatter: (value) => `${value} objectives`,
            }}
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<RocketOutlined />}
            size="large"
            block
            style={{
              background: isProgressComplete ? '#52c41a' : undefined,
            }}
          >
            {loading
              ? 'Generating...'
              : isProgressComplete
              ? 'Generated Successfully!'
              : 'Generate Objectives'}
          </Button>
        </Form.Item>
      </Form>

      <style>{`
        .course-generator-form {
          background: #fff;
          border-radius: 8px;
        }
        .course-generator-form .ant-card-body {
          padding: 24px;
        }
      `}</style>
    </Card>
  );
};

export default CourseGeneratorForm;
