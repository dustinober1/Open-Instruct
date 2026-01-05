/**
 * QuizGenerator Component
 * Form for generating quiz questions from learning objectives
 */

import React from 'react';
import {
  Form,
  Select,
  Button,
  Card,
  Space,
  Typography,
  Alert,
  Divider,
  Spin,
} from 'antd';
import {
  FileTextOutlined,
  ThunderboltOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { GenerateQuizRequest, LearningObjectiveResponse, DifficultyLevel } from '../types';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface QuizGeneratorProps {
  objectives: LearningObjectiveResponse[];
  onGenerate: (request: GenerateQuizRequest) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

const difficultyOptions = [
  { value: 'easy', label: 'Easy', description: 'Straightforward recall questions' },
  { value: 'medium', label: 'Medium', description: 'Requires understanding and application' },
  { value: 'hard', label: 'Hard', description: 'Analysis and evaluation required' },
];

const QuizGenerator: React.FC<QuizGeneratorProps> = ({
  objectives,
  onGenerate,
  loading = false,
  error,
}) => {
  const [form] = Form.useForm();

  if (objectives.length === 0) {
    return (
      <Card variant="borderless">
        <Alert
          message="No Objectives Available"
          description="Please generate learning objectives first before creating quizzes."
          type="info"
          showIcon
        />
      </Card>
    );
  }

  const handleFinish = async (values: GenerateQuizRequest) => {
    await onGenerate(values);
  };

  return (
    <Card className="quiz-generator" variant="borderless">
      <Title level={5}>
        <FileTextOutlined style={{ marginRight: 8 }} />
        Generate Quiz Question
      </Title>
      <Paragraph type="secondary">
        Select a learning objective and difficulty level to generate a quiz question.
      </Paragraph>

      <Divider />

      {error && (
        <Alert
          message="Quiz Generation Failed"
          description={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        onFinish={handleFinish}
        disabled={loading}
        initialValues={{
          difficulty: 'medium',
          numOptions: 4,
        }}
      >
        <Form.Item
          name="objectiveId"
          label="Learning Objective"
          rules={[{ required: true, message: 'Please select a learning objective' }]}
        >
          <Select
            placeholder="Select an objective"
            showSearch
            optionFilterProp="children"
            filterOption={(input, option) =>
              (option?.children as unknown as string)
                ?.toLowerCase()
                .includes(input.toLowerCase())
            }
          >
            {objectives.map((obj) => (
              <Option key={obj.id} value={obj.id}>
                <Space>
                  <span style={{ color: '#999' }}>{obj.id}:</span>
                  <span>
                    {obj.verb} {obj.content}
                  </span>
                  <span
                    style={{
                      fontSize: 12,
                      padding: '2px 8px',
                      borderRadius: 4,
                      backgroundColor: '#f0f0f0',
                    }}
                  >
                    {obj.level}
                  </span>
                </Space>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="difficulty"
          label="Difficulty Level"
          rules={[{ required: true, message: 'Please select a difficulty level' }]}
        >
          <Select placeholder="Select difficulty">
            {difficultyOptions.map((opt) => (
              <Option key={opt.value} value={opt.value}>
                <Space direction="vertical" size={0}>
                  <Text strong>{opt.label}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {opt.description}
                  </Text>
                </Space>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<ThunderboltOutlined />}
            block
          >
            {loading ? 'Generating Quiz...' : 'Generate Quiz Question'}
          </Button>
        </Form.Item>
      </Form>

      <style>{`
        .quiz-generator {
          background: #fff;
          border-radius: 8px;
        }
      `}</style>
    </Card>
  );
};

export default QuizGenerator;
