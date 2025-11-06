# Forge Frontend

Modern, sophisticated web interface for the Forge AI Compliance Assessment Platform.

## 🚀 Features

- **Beautiful UI**: Modern design with Tailwind CSS and custom components
- **Real-time Updates**: Live polling of assessment status
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Type-Safe**: Built with TypeScript for robust code
- **Fast & Efficient**: Next.js 14 with App Router for optimal performance

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (see main README)

## 🛠️ Installation

1. **Install dependencies:**

```bash
cd frontend
npm install
```

2. **Configure environment:**

```bash
cp .env.example .env.local
```

Edit `.env.local` if your backend API is on a different port:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## 🎨 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **UI Components**: Custom components based on shadcn/ui patterns

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app router pages
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page (main flow)
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── ui/              # Reusable UI components
│   │   ├── QuestionnaireForm.tsx
│   │   ├── AssessmentStatus.tsx
│   │   └── AssessmentResults.tsx
│   ├── lib/                 # Utilities
│   │   ├── api.ts           # API client
│   │   └── utils.ts         # Helper functions
│   └── types/               # TypeScript types
│       └── index.ts         # Type definitions
├── public/                  # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## 🎯 Usage Flow

1. **Questionnaire**: Fill out the AI system assessment form
2. **Processing**: Watch real-time status updates (~90 seconds)
3. **Results**: View comprehensive compliance report
4. **Export**: Download PDF report or start new assessment

## 🔧 Development

### Adding New Components

Components should be placed in `src/components/` and follow the existing patterns:

```typescript
'use client'; // For components using React hooks

import { ComponentProps } from './types';

export default function MyComponent({ prop }: ComponentProps) {
  // Component logic
}
```

### API Integration

All API calls go through `src/lib/api.ts`:

```typescript
import { assessmentApi } from '@/lib/api';

const result = await assessmentApi.getAssessmentResult(id);
```

### Styling

Use Tailwind utility classes and the custom CSS variables defined in `globals.css`:

```tsx
<div className="bg-primary text-primary-foreground rounded-lg p-4">
  Content
</div>
```

## 🐛 Troubleshooting

### API Connection Issues

If you see "Failed to connect to API":

1. Ensure the backend is running: `python app.py`
2. Check the API URL in `.env.local`
3. Verify CORS is configured in the backend

### Build Errors

Clear Next.js cache:

```bash
rm -rf .next
npm run dev
```

### Type Errors

Regenerate TypeScript definitions:

```bash
npm run build
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

Same as main project - see LICENSE in root directory
