# Overview

HealthCare+ is a comprehensive full-stack preventive healthcare and awareness platform that helps users track their lifestyle, receive AI-powered health insights, and manage their wellness journey. The application combines modern web technologies with artificial intelligence and weather data to provide personalized health recommendations and alerts.

The platform features user authentication, lifestyle tracking, AI-powered health assistance, weather-based health alerts, premium subscription management with payment processing, and an interactive dashboard with data visualizations.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend uses a traditional server-rendered approach with Progressive Web App capabilities:
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **Styling Framework**: Bootstrap 5 for responsive design and UI components
- **JavaScript**: Vanilla JavaScript with modular organization (app.js, charts.js, dashboard.js)
- **Data Visualization**: Chart.js for health analytics and trend visualization
- **Icons**: Font Awesome for consistent iconography
- **Progressive Enhancement**: Base functionality works without JavaScript, enhanced with dynamic features

## Backend Architecture
The backend follows a modular Flask application structure:
- **Web Framework**: Flask with Blueprint-based route organization
- **Session Management**: Flask-Session with filesystem storage for user sessions
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **API Design**: RESTful API endpoints for all core functionality
- **Security**: CORS configuration, password hashing, and session protection

## Data Storage Solution
Currently implements an in-memory storage system for MVP deployment:
- **Storage Type**: Python dictionaries for data persistence during runtime
- **User Data**: Separate stores for users, profiles, lifestyle logs, and payments
- **Session Storage**: Filesystem-based session management
- **Scalability Design**: Architecture allows easy migration to PostgreSQL/MySQL without code changes
- **Data Models**: Abstract data access layer through model classes (User, Profile, LifestyleLog, Payment)

## Authentication and Authorization
Implements a secure session-based authentication system:
- **Registration**: Complete user profile creation with health information
- **Login/Logout**: Session-based authentication with secure password hashing
- **Route Protection**: Decorator-based authentication requirements (@require_login)
- **Password Security**: Werkzeug password hashing with salt
- **Session Management**: Secure session configuration with signing

## AI Integration Architecture
Leverages OpenAI's GPT-5 model for health recommendations:
- **Health Tips**: Personalized recommendations based on user profile and recent activity
- **Chat Assistant**: Interactive health consultation with context awareness
- **Fallback System**: Rule-based responses when API is unavailable
- **Context Processing**: Combines user data, lifestyle logs, and weather data for comprehensive analysis
- **Prompt Engineering**: Structured prompts for consistent, actionable health advice

## Weather Integration
Integrates OpenWeather API for location-based health insights:
- **Real-time Data**: Current weather conditions for user's location
- **Health Risk Assessment**: Algorithm-based risk indicators for various weather conditions
- **Alert System**: Proactive health alerts based on weather patterns
- **Mock Data Support**: Fallback weather data for development and testing

## Payment Processing Architecture
Implements Paystack payment gateway for subscription management:
- **Frontend Integration**: Paystack inline payment flow with public key
- **Backend Verification**: Server-side payment verification with secret key
- **Webhook Support**: Payment status updates through Paystack webhooks
- **Mock Payment Mode**: Development-friendly payment simulation when API keys unavailable
- **Subscription Management**: User premium status tracking and feature gating

# External Dependencies

## AI Services
- **OpenAI API**: GPT-5 model for health recommendations and chat functionality
- **Configuration**: Requires OPENAI_API_KEY environment variable
- **Fallback**: Rule-based health tips when API unavailable

## Weather Services
- **OpenWeather API**: Current weather data and forecasting
- **Configuration**: Requires OPENWEATHER_API_KEY environment variable
- **Data**: Temperature, humidity, air quality, and weather conditions

## Payment Gateway
- **Paystack**: Nigerian payment processor for subscription billing
- **Configuration**: Requires PAYSTACK_PUBLIC_KEY and PAYSTACK_SECRET_KEY
- **Features**: Payment initialization, verification, and webhook handling
- **Development Mode**: Mock payment flow for local testing

## Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design and components
- **Chart.js**: JavaScript charting library for health data visualization
- **Font Awesome**: Icon library for UI elements

## Python Packages
- **Flask**: Core web framework
- **Flask-Session**: Session management
- **Werkzeug**: Security utilities and password hashing
- **Requests**: HTTP client for external API calls

## Optional Services
- **OneSignal**: Push notification service (environment variable stubbed for future implementation)
- **Deployment**: Configured for Railway deployment with proper CORS and proxy handling