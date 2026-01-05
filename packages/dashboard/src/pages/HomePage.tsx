/**
 * HomePage Component
 * Main dashboard page with course generation and quiz features
 */

import React, { useState } from 'react';
import { Row, Col, Card, Typography, Space, Tabs, Alert, Divider } from 'antd';
import {
  RocketOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';
import { CourseGeneratorForm, ObjectivesDisplay, QuizGenerator, QuizPreview } from '../components';
import { useGenerateObjectives, useGenerateQuiz, useHealthCheck } from '../hooks';
import type { GenerateObjectivesRequest, GenerateQuizRequest, LearningObjectiveResponse, QuizQuestionResponse } from '../types';

const { Title, Paragraph, Text } = Typography;

const HomePage: React.FC = () => {
  const [objectives, setObjectives] = useState<LearningObjectiveResponse[]>([]);
  const [currentTopic, setCurrentTopic] = useState<string>('');
  const [quiz, setQuiz] = useState<QuizQuestionResponse | null>(null);

  const { data: healthData, loading: healthLoading } = useHealthCheck();
  const {
    data: courseData,
    loading: objectivesLoading,
    error: objectivesError,
    progress,
    generate: generateObjectives,
  } = useGenerateObjectives();

  const {
    data: quizData,
    loading: quizLoading,
    error: quizError,
    generate: generateQuiz,
  } = useGenerateQuiz();

  // Update objectives when course data is generated
  React.useEffect(() => {
    if (courseData) {
      setObjectives(courseData.objectives);
      setCurrentTopic(courseData.topic);
    }
  }, [courseData]);

  // Update quiz when quiz data is generated
  React.useEffect(() => {
    if (quizData) {
      setQuiz(quizData);
    }
  }, [quizData]);

  const handleGenerateObjectives = async (request: GenerateObjectivesRequest) => {
    await generateObjectives(request);
  };

  const handleGenerateQuiz = async (request: GenerateQuizRequest) => {
    await generateQuiz(request);
  };

  const handleQuizFromObjective = (objectiveId: string) => {
    const objective = objectives.find((obj) => obj.id === objectiveId);
    if (objective) {
      generateQuiz({
        objectiveId: objective.id,
        difficulty: 'medium',
      });
    }
  };

  return (
    <div className="home-page">
      {/* Health Status Alert */}
      {healthData && healthData.status !== 'healthy' && (
        <Alert
          message="API Status: Degraded"
          description={
            healthData.ollamaConnected
              ? 'The API is running but some services may be slow.'
              : 'Cannot connect to Ollama. Please ensure Ollama is running.'
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
          closable
        />
      )}

      <Row gutter={[24, 24]}>
        {/* Left Column - Generation Forms */}
        <Col xs={24} lg={12}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* Course Generator */}
            <CourseGeneratorForm
              onGenerate={handleGenerateObjectives}
              loading={objectivesLoading}
              progress={progress}
              error={objectivesError?.message}
            />

            {/* Quiz Generator */}
            <QuizGenerator
              objectives={objectives}
              onGenerate={handleGenerateQuiz}
              loading={quizLoading}
              error={quizError?.message}
            />
          </Space>
        </Col>

        {/* Right Column - Results */}
        <Col xs={24} lg={12}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* Quiz Preview */}
            <QuizPreview
              quiz={quiz}
              loading={quizLoading}
              onRetry={() => quiz && generateQuiz({ objectiveId: quiz.objectiveId, difficulty: quiz.difficulty })}
            />

            {/* Objectives Display */}
            <ObjectivesDisplay
              objectives={objectives}
              topic={currentTopic}
              loading={objectivesLoading}
              onQuizGenerate={handleQuizFromObjective}
            />
          </Space>
        </Col>
      </Row>

      <style>{`
        .home-page {
          width: 100%;
        }
        .home-page .ant-card {
          border-radius: 8px;
        }
      `}</style>
    </div>
  );
};

export default HomePage;
