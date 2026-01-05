/**
 * QuizPreview Component
 * Displays quiz questions with answer reveal functionality
 */

import React, { useState } from 'react';
import {
  Card,
  Radio,
  Button,
  Typography,
  Space,
  Tag,
  Alert,
  Divider,
  Result,
  Spin,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined,
  ReloadOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import type { QuizQuestionResponse, DifficultyLevel } from '../types';
import { getDifficultyColor } from '../utils';

const { Title, Text, Paragraph } = Typography;

interface QuizPreviewProps {
  quiz: QuizQuestionResponse | null;
  loading?: boolean;
  onRetry?: () => void;
  onNext?: () => void;
}

interface QuizOption {
  key: string;
  label: string;
  isCorrect: boolean;
}

const QuizPreview: React.FC<QuizPreviewProps> = ({
  quiz,
  loading = false,
  onRetry,
  onNext,
}) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);

  React.useEffect(() => {
    // Reset state when quiz changes
    setSelectedAnswer(null);
    setShowAnswer(false);
  }, [quiz]);

  if (loading) {
    return (
      <Card bordered={false} className="quiz-preview">
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>Generating quiz question...</Paragraph>
        </div>
      </Card>
    );
  }

  if (!quiz) {
    return (
      <Card bordered={false} className="quiz-preview">
        <Result
          icon="🐰"
          title="No Quiz Generated"
          subTitle="Select a learning objective to generate a quiz question"
          extra={
            onNext && (
              <Button type="primary" onClick={onNext}>
                Select Objective
              </Button>
            )
          }
        />
      </Card>
    );
  }

  const options: QuizOption[] = [
    { key: 'correct', label: quiz.correctAnswer, isCorrect: true },
    ...quiz.distractors.map((d, i) => ({
      key: `distractor-${i}`,
      label: d,
      isCorrect: false,
    })),
  ];

  // Shuffle options for display
  const shuffledOptions = [...options].sort(() => Math.random() - 0.5);

  const handleAnswerSelect = (value: string) => {
    if (!showAnswer) {
      setSelectedAnswer(value);
    }
  };

  const handleRevealAnswer = () => {
    setShowAnswer(true);
  };

  const isCorrect = selectedAnswer === quiz.correctAnswer;

  const getResultStatus = () => {
    if (!showAnswer) return 'default';
    return isCorrect ? 'success' : 'error';
  };

  const handleCopyQuestion = () => {
    const text = `
Question: ${quiz.stem}
A) ${options[0].label}
B) ${options[1].label}
C) ${options[2].label}
D) ${options[3].label}
Answer: ${quiz.correctAnswer}
Explanation: ${quiz.explanation}
    `.trim();
    navigator.clipboard.writeText(text);
  };

  return (
    <Card bordered={false} className="quiz-preview">
      <div className="quiz-header">
        <Space>
          <Title level={5} style={{ margin: 0 }}>
            Quiz Question
          </Title>
          <Tag color={getDifficultyColor(quiz.difficulty as DifficultyLevel)}>
            {quiz.difficulty.toUpperCase()}
          </Tag>
        </Space>
        <Text type="secondary">ID: {quiz.quizId}</Text>
      </div>

      <Divider />

      <div className="question-section">
        <Paragraph strong className="question-stem">
          {quiz.stem}
        </Paragraph>

        <Radio.Group
          value={selectedAnswer}
          onChange={(e) => handleAnswerSelect(e.target.value)}
          disabled={showAnswer}
          className="options-group"
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            {shuffledOptions.map((option, index) => {
              const optionLabel = String.fromCharCode(65 + index); // A, B, C, D
              const isSelected = selectedAnswer === option.label;
              const showCorrect = showAnswer && option.isCorrect;
              const showIncorrect = showAnswer && isSelected && !option.isCorrect;

              return (
                <Radio.Button
                  key={option.key}
                  value={option.label}
                  className={`option-button ${
                    showCorrect
                      ? 'correct-answer'
                      : showIncorrect
                      ? 'wrong-answer'
                      : ''
                  }`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '12px 16px',
                    height: 'auto',
                    whiteSpace: 'normal',
                  }}
                >
                  <Space align="start" style={{ width: '100%' }}>
                    <Text strong style={{ minWidth: 24 }}>{optionLabel})</Text>
                    <Text>{option.label}</Text>
                    {showCorrect && (
                      <CheckCircleOutlined style={{ color: '#52c41a', marginLeft: 'auto' }} />
                    )}
                    {showIncorrect && (
                      <CloseCircleOutlined style={{ color: '#ff4d4f', marginLeft: 'auto' }} />
                    )}
                  </Space>
                </Radio.Button>
              );
            })}
          </Space>
        </Radio.Group>
      </div>

      {showAnswer && (
        <Alert
          message={isCorrect ? 'Correct!' : 'Incorrect'}
          description={
            <div>
              <Paragraph>
                <Text strong>Correct Answer: </Text>
                {quiz.correctAnswer}
              </Paragraph>
              <Divider style={{ margin: '12px 0' }} />
              <Paragraph>
                <Text strong>Explanation: </Text>
                {quiz.explanation}
              </Paragraph>
            </div>
          }
          type={isCorrect ? 'success' : 'error'}
          showIcon
          style={{ marginTop: 16 }}
        />
      )}

      <div className="quiz-actions">
        {!showAnswer ? (
          <Button
            type="primary"
            icon={<EyeOutlined />}
            onClick={handleRevealAnswer}
            disabled={!selectedAnswer}
          >
            Reveal Answer
          </Button>
        ) : (
          <Space>
            <Button icon={<CopyOutlined />} onClick={handleCopyQuestion}>
              Copy Question
            </Button>
            {onNext && (
              <Button type="primary" onClick={onNext}>
                Next Question
              </Button>
            )}
            {onRetry && (
              <Button icon={<ReloadOutlined />} onClick={onRetry}>
                Regenerate
              </Button>
            )}
          </Space>
        )}
      </div>

      <style>{`
        .quiz-preview {
          background: #fff;
          border-radius: 8px;
        }
        .quiz-preview .quiz-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 8px;
        }
        .quiz-preview .question-section {
          margin: 24px 0;
        }
        .quiz-preview .question-stem {
          font-size: 16px;
          margin-bottom: 16px;
        }
        .quiz-preview .options-group {
          width: 100%;
        }
        .quiz-preview .option-button {
          width: 100% !important;
          margin-bottom: 8px;
          border-radius: 8px !important;
        }
        .quiz-preview .correct-answer {
          background-color: #f6ffed !important;
          border-color: #52c41a !important;
        }
        .quiz-preview .wrong-answer {
          background-color: #fff2f0 !important;
          border-color: #ff4d4f !important;
        }
        .quiz-preview .quiz-actions {
          margin-top: 24px;
          text-align: center;
        }
      `}</style>
    </Card>
  );
};

export default QuizPreview;
