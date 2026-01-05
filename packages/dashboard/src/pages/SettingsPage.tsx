/**
 * SettingsPage Component
 * Configure API endpoint, API key, and Ollama settings
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Switch,
  Space,
  Typography,
  Divider,
  Alert,
  Result,
  message,
  Collapse,
  Tag,
  Tooltip,
  Spin,
} from 'antd';
import {
  SettingOutlined,
  ApiOutlined,
  KeyOutlined,
  RobotOutlined,
  SaveOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InfoCircleOutlined,
  GlobalOutlined,
  CloudDownloadOutlined,
} from '@ant-design/icons';
import { healthCheck } from '../services/api';

const { Title, Paragraph, Text } = Typography;
const { Panel } = Collapse;

interface Settings {
  apiUrl: string;
  apiKey: string;
  useOllama: boolean;
  ollamaBaseUrl: string;
  ollamaModel: string;
}

const defaultSettings: Settings = {
  apiUrl: 'http://localhost:8000',
  apiKey: '',
  useOllama: true,
  ollamaBaseUrl: 'http://localhost:11434',
  ollamaModel: 'llama2:7b',
};

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [pullingModel, setPullingModel] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [connectionMessage, setConnectionMessage] = useState('');
  const [savedSettings, setSavedSettings] = useState<Settings>(defaultSettings);

  // Load settings from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('open-instruct-settings');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setSavedSettings({ ...defaultSettings, ...parsed });
        form.setFieldsValue(parsed);
      } catch {
        form.setFieldsValue(defaultSettings);
      }
    } else {
      form.setFieldsValue(defaultSettings);
    }
  }, [form]);

  // Save settings to localStorage
  const saveSettings = async (values: Settings) => {
    setLoading(true);
    try {
      localStorage.setItem('open-instruct-settings', JSON.stringify(values));
      setSavedSettings(values);
      message.success('Settings saved successfully!');
    } catch {
      message.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  // Test API connection
  const testConnection = async () => {
    setTesting(true);
    setConnectionStatus('idle');

    try {
      const values = form.getFieldsValue();
      const testUrl = values.apiUrl || savedSettings.apiUrl;

      const response = await fetch(`${testUrl}/health`);
      const data = await response.json();

      if (response.ok) {
        setConnectionStatus('success');
        setConnectionMessage(`Connected successfully! API Status: ${data.status}`);
      } else {
        setConnectionStatus('error');
        setConnectionMessage(`Connection failed: ${data.message || 'Unknown error'}`);
      }
    } catch (error) {
      setConnectionStatus('error');
      setConnectionMessage(`Connection failed: ${error instanceof Error ? error.message : 'Network error'}`);
    } finally {
      setTesting(false);
    }
  };

  // Pull/download Ollama model
  const pullModel = async () => {
    const values = form.getFieldsValue();
    const ollamaUrl = values.ollamaBaseUrl || savedSettings.ollamaBaseUrl;
    const modelName = values.ollamaModel || savedSettings.ollamaModel;

    if (!modelName) {
      message.error('Please enter a model name');
      return;
    }

    setPullingModel(true);
    message.loading(`Pulling model ${modelName}... This may take a while.`, 0);

    try {
      const response = await fetch(`${ollamaUrl}/api/pull`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: modelName }),
      });

      if (response.ok) {
        message.success(`Model ${modelName} pulled successfully!`);
      } else {
        const errorData = await response.json();
        message.error(`Failed to pull model: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      message.error(`Connection failed: ${error instanceof Error ? error.message : 'Network error'}`);
    } finally {
      setPullingModel(false);
      message.destroy();
    }
  };

  // Check which models are installed
  const listModels = async () => {
    const values = form.getFieldsValue();
    const ollamaUrl = values.ollamaBaseUrl || savedSettings.ollamaBaseUrl;

    try {
      const response = await fetch(`${ollamaUrl}/api/tags`);
      const data = await response.json();
      
      if (data.models) {
        const modelNames = data.models.map((m: { name: string }) => m.name).join(', ');
        message.info(`Installed models: ${modelNames || 'None'}`);
      }
    } catch (error) {
      message.error(`Failed to list models: ${error instanceof Error ? error.message : 'Network error'}`);
    }
  };

  const resetToDefaults = () => {
    form.setFieldsValue(defaultSettings);
    message.info('Reset to default settings');
  };

  return (
    <div className="settings-page">
      <Title level={3}>
        <SettingOutlined style={{ marginRight: 8 }} />
        Settings
      </Title>
      <Paragraph type="secondary">
        Configure your API connection, authentication, and Ollama settings.
      </Paragraph>

      <Divider />

      <Form
        form={form}
        layout="vertical"
        onFinish={saveSettings}
        initialValues={savedSettings}
      >
        <Collapse defaultActiveKey={['api']} bordered={false}>
          {/* API Configuration */}
          <Panel
            header={
              <Space>
                <ApiOutlined />
                <Text strong>API Configuration</Text>
              </Space>
            }
            key="api"
          >
            <Form.Item
              name="apiUrl"
              label={
                <Space>
                  <GlobalOutlined />
                  <span>API Endpoint URL</span>
                </Space>
              }
              rules={[{ required: true, message: 'Please enter the API URL' }]}
              extra="The base URL of your Open-Instruct API server"
            >
              <Input
                placeholder="http://localhost:8000"
                prefix={<GlobalOutlined />}
              />
            </Form.Item>

            <Form.Item
              name="apiKey"
              label={
                <Space>
                  <KeyOutlined />
                  <span>API Key (Optional)</span>
                </Space>
              }
              extra="Your API key for authentication, if required"
            >
              <Input.Password
                placeholder="Enter your API key"
                prefix={<KeyOutlined />}
              />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  Save Settings
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={testConnection}
                  loading={testing}
                >
                  Test Connection
                </Button>
                <Button onClick={resetToDefaults}>
                  Reset to Defaults
                </Button>
              </Space>
            </Form.Item>

            {/* Connection Status */}
            {connectionStatus !== 'idle' && (
              <Alert
                type={connectionStatus === 'success' ? 'success' : 'error'}
                message={connectionStatus === 'success' ? 'Connection Successful' : 'Connection Failed'}
                description={connectionMessage}
                showIcon
                icon={connectionStatus === 'success' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                style={{ marginTop: 16 }}
              />
            )}
          </Panel>

          {/* Ollama Configuration */}
          <Panel
            header={
              <Space>
                <RobotOutlined />
                <Text strong>Ollama Configuration</Text>
                <Tag color="purple">Local LLM</Tag>
              </Space>
            }
            key="ollama"
          >
            <Form.Item
              name="useOllama"
              label="Use Local Ollama"
              valuePropName="checked"
              extra="Enable to use a local Ollama instance instead of remote API"
            >
              <Switch checkedChildren="Enabled" unCheckedChildren="Disabled" />
            </Form.Item>

            <Collapse>
              <Panel
                header="Ollama Settings"
                key="ollama-settings"
              >
                <Form.Item
                  name="ollamaBaseUrl"
                  label="Ollama Base URL"
                  extra="The URL where your Ollama instance is running"
                >
                  <Input
                    placeholder="http://localhost:11434"
                    prefix={<GlobalOutlined />}
                  />
                </Form.Item>

                <Form.Item
                  name="ollamaModel"
                  label="Model Name"
                  extra="The Ollama model to use (e.g., llama2:7b, codellama:7b, mistral)"
                >
                  <Input
                    placeholder="llama2:7b"
                    prefix={<RobotOutlined />}
                  />
                </Form.Item>

                {/* Model Management Buttons */}
                <Space direction="vertical" style={{ width: '100%' }} size="small">
                  <Button
                    type="primary"
                    icon={<CloudDownloadOutlined />}
                    onClick={pullModel}
                    loading={pullingModel}
                    block
                  >
                    Pull/Download Model
                  </Button>
                  
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={listModels}
                    block
                  >
                    List Installed Models
                  </Button>
                </Space>

                <Alert
                  message="Ollama Required"
                  description={
                    <div>
                      <p>Make sure Ollama is running locally with <code>ollama serve</code>.</p>
                      <p>Popular models: <code>llama2:7b</code>, <code>codellama:7b</code>, <code>mistral</code>, <code>orca-2</code></p>
                      <p>To download a model manually: <code>ollama pull llama2:7b</code></p>
                    </div>
                  }
                  type="info"
                  showIcon
                  icon={<InfoCircleOutlined />}
                  style={{ marginTop: 16 }}
                />
              </Panel>
            </Collapse>
          </Panel>
        </Collapse>
      </Form>

      <Divider />

      {/* Current Configuration Display */}
      <Card size="small" title="Current Configuration">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>API URL: </Text>
            <Text code>{savedSettings.apiUrl}</Text>
          </div>
          <div>
            <Text strong>API Key: </Text>
            <Text code>{savedSettings.apiKey ? '••••••••' : 'Not set'}</Text>
          </div>
          <div>
            <Text strong>Use Ollama: </Text>
            <Tag color={savedSettings.useOllama ? 'green' : 'red'}>
              {savedSettings.useOllama ? 'Enabled' : 'Disabled'}
            </Tag>
          </div>
          {savedSettings.useOllama && (
            <>
              <div>
                <Text strong>Ollama URL: </Text>
                <Text code>{savedSettings.ollamaBaseUrl}</Text>
              </div>
              <div>
                <Text strong>Model: </Text>
                <Tag color="purple">{savedSettings.ollamaModel}</Tag>
              </div>
            </>
          )}
        </Space>
      </Card>

      <style>{`
        .settings-page {
          max-width: 800px;
          margin: 0 auto;
        }
        .settings-page .ant-collapse {
          background: transparent;
        }
        .settings-page .ant-collapse-item {
          background: #fff;
          border-radius: 8px !important;
          margin-bottom: 16px;
          padding: 8px 16px;
        }
      `}</style>
    </div>
  );
};

export default SettingsPage;
