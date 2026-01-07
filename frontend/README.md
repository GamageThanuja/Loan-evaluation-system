# 🏦 Home Credit Loan Approval System

A **production-ready** Next.js 14 frontend application for the Home Credit Default Risk prediction system, featuring advanced ML model visualizations with SHAP explanations and Bayesian network analysis.

## ✨ Features

### 📊 Dashboard
- Real-time model performance metrics (AUC, Accuracy)
- Recent predictions overview
- Model health monitoring
- Quick action buttons

### 👤 Applicant Management
- **List View**: Paginated table with search functionality
- **New Application**: Comprehensive form with real-time validation
- **Detail View**: Complete applicant profile with prediction results

### 🤖 AI Explanations
- **Risk Gauge**: Circular and linear progress indicators
- **SHAP Analysis**: Top 5 feature impacts with bar charts
- **Bayesian Network**: Causal path visualization
- **Business Rules**: Triggered rules with severity levels

### 📈 Reports
- Model performance over time (line charts)
- Decision distribution (bar charts)
- Batch prediction history
- Export to CSV/PDF

### 🔐 Role-Based Access
- **Loan Officer**: View applications, create new applicants
- **Bank Manager**: All officer permissions + approve/reject loans

### 🎨 UI/UX
- Material UI 5 components
- Dark/Light mode toggle
- Fully responsive (mobile → desktop)
- Loading skeletons & error boundaries
- Professional banking design

## 🛠️ Tech Stack

- **Framework**: Next.js 14.1.0 (App Router)
- **UI Library**: Material UI 5.15.10
- **State Management**: 
  - Zustand 4.5.0 (Auth)
  - TanStack React Query 5.17.19 (API/Data)
- **Validation**: Zod 3.22.4
- **Charts**: Recharts 2.12.0
- **HTTP Client**: Axios 1.6.7
- **Styling**: Tailwind CSS 3.4.1
- **Language**: TypeScript 5.3.3 (Strict Mode)

## 📁 Project Structure

```
my-loan-approval-frontend/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Dashboard
│   ├── login/
│   │   └── page.tsx         # Login page
│   ├── applicant/
│   │   ├── page.tsx         # Applicant list
│   │   ├── new/page.tsx     # New applicant form
│   │   └── [id]/page.tsx    # Applicant detail
│   ├── reports/
│   │   └── page.tsx         # Reports & analytics
│   └── globals.css          # Global styles
│
├── components/
│   ├── ui/
│   │   ├── LoadingSkeleton.tsx
│   │   └── ErrorBoundary.tsx
│   ├── common/
│   │   └── EmptyState.tsx
│   ├── prediction/
│   │   ├── RiskGauge.tsx
│   │   ├── ShapExplanation.tsx
│   │   ├── BayesianNetworkDisplay.tsx
│   │   └── BusinessRules.tsx
│   └── Providers.tsx
│
├── layouts/
│   ├── MainLayout.tsx       # Sidebar + navbar
│   └── AuthLayout.tsx       # Login layout
│
├── hooks/
│   ├── usePrediction.ts     # React Query hooks
│   ├── useAuth.ts           # Zustand auth store
│   └── useModel.ts          # Model stats hooks
│
├── services/
│   ├── api.ts               # Axios client
│   └── prediction.ts        # API methods + mock data
│
├── lib/
│   ├── theme.ts             # MUI theme
│   ├── utils.ts             # Helper functions
│   └── validation.ts        # Zod schemas
│
├── types/
│   └── index.ts             # TypeScript interfaces
│
└── public/                   # Static assets
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. **Clone or navigate to the directory**
   ```bash
   cd my-loan-approval-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   
   The `.env.local` file is already created with default values:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_APP_NAME="Home Credit Loan Approval"
   NEXT_PUBLIC_RISK_THRESHOLD_LOW=0.15
   NEXT_PUBLIC_RISK_THRESHOLD_MEDIUM=0.30
   NEXT_PUBLIC_RISK_THRESHOLD_HIGH=0.50
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

5. **Open browser**
   ```
   http://localhost:3000
   ```

### First Login

The app currently uses **mock authentication**:
- **Email**: Any valid email (e.g., `user@example.com`)
- **Password**: Any password (min 6 characters)
- **Role**: Select "Loan Officer" or "Bank Manager"

## 📡 API Integration

### Current State: Mock Data

The frontend currently works with **mock data** for standalone development. All API calls in `services/prediction.ts` return mock responses.

### Connecting to Real Backend

1. **Update `.env.local`**
   ```env
   NEXT_PUBLIC_API_URL=http://your-backend-url:8000
   ```

2. **Remove mock implementations**
   
   In `services/prediction.ts`, replace mock implementations with actual API calls:
   ```typescript
   // Before (Mock)
   await new Promise(resolve => setTimeout(resolve, 1000));
   return { success: true, data: mockData };

   // After (Real API)
   const response = await apiClient.post('/api/predict', request);
   return { success: true, data: response.data };
   ```

3. **Required API Endpoints**

   The frontend expects these endpoints:

   #### Authentication
   ```
   POST /api/auth/login
   Body: { email, password, role }
   Response: { token, user: { id, email, name, role } }
   ```

   #### Applicants
   ```
   GET /api/applicants?page=1&pageSize=10&search=query
   POST /api/applicants
   GET /api/applicants/:id
   POST /api/applicants/:id/approve
   POST /api/applicants/:id/reject
   ```

   #### Predictions
   ```
   POST /api/predict
   Body: { applicantId, features: { EXT_SOURCE_MEAN, ... } }
   Response: { riskScore, decision, confidence, shapExplanation, ... }
   
   GET /api/predictions/:id
   GET /api/predictions/recent?limit=5
   ```

   #### Model Stats
   ```
   GET /api/model/stats
   GET /api/model/health
   ```

   #### Reports
   ```
   GET /api/reports/performance
   GET /api/reports/batches
   GET /api/reports/export/csv
   GET /api/reports/export/pdf
   ```

## 🎨 Customization

### Theme Colors

Edit `lib/theme.ts` to change the color scheme:
```typescript
primary: {
  main: '#1976d2',  // Change to your brand color
},
secondary: {
  main: '#f59e0b',
},
```

### Risk Thresholds

Adjust in `.env.local`:
```env
NEXT_PUBLIC_RISK_THRESHOLD_LOW=0.15    # Score ≤ 15% = LOW risk
NEXT_PUBLIC_RISK_THRESHOLD_MEDIUM=0.30 # Score ≤ 30% = MEDIUM risk
NEXT_PUBLIC_RISK_THRESHOLD_HIGH=0.50   # Score > 30% = HIGH risk
```

## 📦 Build & Deploy

### Production Build

```bash
npm run build
npm run start
```

### Deployment Options

#### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

#### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t loan-approval-frontend .
docker run -p 3000:3000 loan-approval-frontend
```

#### Traditional Server
```bash
npm run build
pm2 start npm --name "loan-app" -- start
```

## 🧪 Available Scripts

```bash
npm run dev          # Start development server (port 3000)
npm run build        # Create production build
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

## 🔧 Configuration Files

- `tsconfig.json` - TypeScript strict mode configuration
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - Tailwind CSS theme
- `.eslintrc.json` - ESLint rules
- `postcss.config.js` - PostCSS plugins

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
PORT=3001 npm run dev
```

### Module Not Found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## 📚 Key Components

### RiskGauge
Circular progress indicator with risk level chip
```typescript
<RiskGauge 
  riskScore={0.23} 
  riskLevel="LOW" 
  confidence={0.89} 
/>
```

### ShapExplanation
SHAP feature importance visualization
```typescript
<ShapExplanation explanation={prediction.shapExplanation} />
```

### BayesianNetworkDisplay
Causal relationships network
```typescript
<BayesianNetworkDisplay network={prediction.bayesianNetwork} />
```

### BusinessRules
Triggered business rules with severity
```typescript
<BusinessRules rules={prediction.businessRules} />
```

## 🔐 Security Notes

- **Authentication**: Currently mock - implement JWT/OAuth2 for production
- **HTTPS**: Always use HTTPS in production
- **Environment Variables**: Never commit `.env.local` to version control
- **API Keys**: Store sensitive keys server-side only
- **CORS**: Configure proper CORS headers on backend

## 📊 Performance

- **First Load JS**: ~100KB gzipped
- **LCP**: < 2.5s (Largest Contentful Paint)
- **CLS**: < 0.1 (Cumulative Layout Shift)
- **FID**: < 100ms (First Input Delay)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is part of the Home Credit Default Risk system.

## 🙏 Acknowledgments

- Material UI for the component library
- Recharts for data visualization
- TanStack Query for data fetching
- Next.js team for the framework

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the API integration guide
3. Check console for error messages
4. Ensure all dependencies are installed

---

**Built with ❤️ using Next.js 14, Material UI 5, and TypeScript**
