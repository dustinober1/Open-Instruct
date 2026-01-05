# @open-instruct/dashboard

React dashboard for Open-Instruct educational content generation powered by Bloom's Taxonomy and AI.

## Features

- 🎓 **Course Generation**: Create AI-powered learning objectives aligned with Bloom's Taxonomy
- 📝 **Quiz Management**: Generate quiz questions from learning objectives
- 📊 **Analytics Dashboard**: Track usage statistics and performance metrics
- 🎨 **Modern UI**: Built with Ant Design for a professional look
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🔗 **API Integration**: Connects seamlessly with the Open-Instruct backend

## Installation

```bash
npm install @open-instruct/dashboard
# or
yarn add @open-instruct/dashboard
# or
pnpm add @open-instruct/dashboard
```

## Usage

### Standalone App

```tsx
import React from 'react';
import { App } from '@open-instruct/dashboard';
import '@open-instruct/dashboard/dist/index.css';

const RootApp: React.FC = () => {
  return <App />;
};

export default RootApp;
```

### Individual Components

```tsx
import React from 'react';
import { CourseGeneratorForm, ObjectivesDisplay, QuizGenerator } from '@open-instruct/dashboard';

const MyComponent: React.FC = () => {
  const handleGenerate = async (request) => {
    // Call your API
    const response = await fetch('/api/v1/generate/objectives', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    return response.json();
  };

  return (
    <div>
      <CourseGeneratorForm onGenerate={handleGenerate} />
    </div>
  );
};

export default MyComponent;
```

### Using Hooks

```tsx
import React from 'react';
import { useGenerateObjectives, useGenerateQuiz } from '@open-instruct/dashboard';

const MyComponent: React.FC = () => {
  const { data, loading, error, generate } = useGenerateObjectives();
  const { generate: generateQuiz } = useGenerateQuiz();

  const handleGenerate = async (request) => {
    await generate(request);
  };

  return (
    // ... component JSX
  );
};
```

## Environment Variables

Configure the API URL by setting environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## API Integration

The dashboard expects the following API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/generate/objectives` | POST | Generate learning objectives |
| `/api/v1/generate/quiz` | POST | Generate quiz questions |

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

## Project Structure

```
packages/dashboard/
├── src/
│   ├── components/     # React components
│   │   ├── CourseGeneratorForm.tsx
│   │   ├── ObjectivesDisplay.tsx
│   │   ├── QuizGenerator.tsx
│   │   ├── QuizPreview.tsx
│   │   ├── AnalyticsDashboard.tsx
│   │   └── Layout.tsx
│   ├── hooks/          # Custom React hooks
│   │   ├── useHealthCheck.ts
│   │   ├── useObjectives.ts
│   │   └── useQuiz.ts
│   ├── pages/          # Page components
│   │   ├── HomePage.tsx
│   │   └── AnalyticsPage.tsx
│   ├── services/       # API services
│   │   └── api.ts
│   ├── types/          # TypeScript types
│   │   └── index.ts
│   ├── utils/          # Utility functions
│   │   └── index.ts
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Dependencies

### Peer Dependencies

- React ≥ 18.0.0
- React DOM ≥ 18.0.0
- React Router DOM ≥ 6.0.0

### Main Dependencies

- Ant Design 5.x
- Axios
- Recharts
- Day.js

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Email: support@example.com
- 🐛 Issues: GitHub Issues
- 📖 Documentation: [docs/](docs/)
