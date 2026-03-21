# 7-Minute Code Walkthrough Script - LoanWise Project

**Total Duration:** ~7 minutes  
**Style:** Conversational, flowing narrative  
**Target:** Non-technical and technical audience

---

## 🎬 COMPLETE SCRIPT (Read as continuous paragraphs)

Hi everyone! Today I'll walk you through the LoanWise project - a loan evaluation system powered by AI. This is a full-stack application with a React frontend, FastAPI backend, and a hybrid machine learning model that predicts loan eligibility with 98.71% accuracy. The entire project is organized into four main folders: backend, frontend, ml-model, and database. Let's dive in and see how everything works together.

Let me show you the overall architecture. We have a clean 4-layer design. First, the frontend - built with Next.js and React - this is what users see and interact with. Second, the backend API - built with FastAPI in Python - handles all the business logic, authentication, and data validation. Third, the ML model layer - this is where our hybrid Bayesian model lives, combining a Bayesian Neural Network with Gradient Boosting. And fourth, the database - we're using Supabase, which is cloud-hosted PostgreSQL. Everything communicates through REST APIs. The frontend makes HTTP requests, the backend processes them, calls the ML model when needed, and stores everything in the database. Simple and scalable.

Let's start with the backend. Open the backend folder and you'll see this structure. main.py is our entry point. It creates the FastAPI app, sets up CORS, adds middleware, and registers all our routers. Think of it as the brain that coordinates everything. The routers folder is where all our API endpoints live. We have auth.py for login and registration, applicants.py for creating and managing loan applicants, predictions.py for running our AI model, dashboard.py for statistics, and status_management.py for updating application statuses. Each router is clean and focused - for example, if you open applicants.py, you'll see endpoints like POST to create an applicant, GET to retrieve them, PUT to update, DELETE to remove. Standard REST operations.

The middleware folder handles cross-cutting concerns. auth.py verifies JWT tokens on every request, logging_middleware.py logs every API call, and error_handler.py catches errors and returns clean responses. The src folder contains our business logic. Inside, you'll find the evaluation folder with prediction logic, the inference folder that loads and runs the ML model, and the models folder with data validation using Pydantic. Everything is modular - if I need to add a new feature, I just create a new router and plug it in. No spaghetti code here!

Now let's look at the frontend. This is a Next.js 14 application using the App Router. The app folder contains all our pages. page.tsx is the dashboard - shows statistics, charts, recent applications. Then we have the applicant folder for managing applicants, the eligibility folder where we check if someone is eligible for a loan, the review folder for loan officers to approve or reject applications, and login and register folders for authentication. The components folder has reusable UI pieces. Under common, we have things like Navbar, Sidebar, Toast notifications. Under loan, we have ApplicantCard, ApplicantForm, ApplicantTable. And under prediction, we have PredictionCard showing the AI result with confidence score and risk level.

The hooks folder is crucial - these are custom React hooks that fetch data. useApplicants gets the list of applicants, usePrediction calls the AI model, useAuth handles login and logout, and useDashboard fetches statistics. These hooks use TanStack Query, which gives us automatic caching, loading states, and error handling. So if you're on the dashboard and the API call fails, TanStack Query will retry automatically. The services folder has our API client functions. For example, applicants.ts has functions like createApplicant and getApplicantById - they just wrap fetch calls to our backend. Everything is TypeScript, so we get type safety. If I try to pass the wrong data type, the compiler catches it immediately.

This is the heart of the system - our machine learning model. The training folder has our model code. hybrid_model.py is our main model. It combines two approaches: a Bayesian Neural Network for uncertainty estimation and Gradient Boosting for raw accuracy. When a prediction comes in, here's what happens. We load the applicant's data - things like income, credit score, loan amount. We extract 22 features - age, debt-to-income ratio, credit utilization, and so on. We apply StandardScaler to normalize everything. We use PCA to reduce from 22 features down to 12 components. We run it through both models in parallel. We combine the results with weighted averaging - 30% from Bayesian NN, 70% from Gradient Boosting. And we get a final probability - if it's above 0.5, the person is eligible.

The Bayesian Neural Network is special because it gives us uncertainty. So if the model isn't sure, we can flag it for manual review. The models folder stores the trained models - these are pickle files. We have hybrid_model_v3.pkl, scaler.pkl, pca.pkl - everything we need to make predictions. The data folder has our training data - we used a Kaggle loan dataset with over 4,000 samples. We validated everything with 5-fold cross-validation and got consistent 98.71% accuracy across all folds. Very stable.

Quick look at the database. The schemas folder has all our SQL files. users.sql for authentication, applicants.sql for loan applicants, predictions.sql to store AI predictions, and audit_logs.sql for compliance. We're using Supabase, which gives us PostgreSQL in the cloud with built-in authentication and Row Level Security. So users can only see their own data - security baked in.

And that's it! A full-stack AI-powered loan system in 7 minutes. Frontend talks to backend via REST APIs, backend calls the ML model, everything gets stored in the database. Clean, modular, and production-ready. Thanks for watching!

---

## 📝 SPEAKING TIPS

1. **Pace:** Speak clearly at ~140-150 words per minute
2. **Screen Time:** 
   - Spend 20% on architecture diagram
   - 30% on backend code
   - 25% on frontend code
   - 20% on ML model
   - 5% on database
3. **Visual Flow:**
   - Start with folder structure
   - Zoom into specific files when mentioning them
   - Use cursor to highlight important lines
   - Show one running example (e.g., making a prediction)
4. **Key Points to Emphasize:**
   - 4-layer architecture
   - 98.71% accuracy
   - Modular design
   - Type safety (TypeScript/Pydantic)
   - Real-time predictions

---

## 🎯 TIMING BREAKDOWN

| Section | Duration | Key Points |
|---------|----------|------------|
| Intro | 0:30 | Project name, tech stack, accuracy |
| Architecture | 1:00 | 4 layers, REST APIs, data flow |
| Backend | 2:00 | FastAPI, routers, middleware, business logic |
| Frontend | 1:30 | Next.js, pages, components, hooks, services |
| ML Model | 1:30 | Hybrid approach, prediction pipeline, validation |
| Database | 0:20 | Supabase, schemas, security |
| Conclusion | 0:10 | Summary, thank you |
| **TOTAL** | **7:00** | |

---

## 💡 ALTERNATIVE: If Running Short (5-6 minutes)

Skip these sections:
- Detailed middleware explanation
- Frontend services folder
- Database schemas details
- Cross-validation specifics

## 💡 ALTERNATIVE: If Running Long (8-9 minutes)

Add these:
- Live demo of one API call in Postman
- Show actual prediction result with explanation
- Walk through one React component in detail
- Show database table structure in Supabase UI

---

**Practice this 2-3 times before recording to get timing perfect!**
