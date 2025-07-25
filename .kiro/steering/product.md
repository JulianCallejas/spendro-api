# Product Overview

**Spendro** is a collaborative expense tracking API built with FastAPI that enables multi-user budget management with real-time synchronization capabilities.

## Core Features
- Multi-user collaborative budgets with role-based access control (Admin, Editor, Viewer)
- Multiple authentication methods: email/password, Google OAuth, biometric
- Real-time synchronization with offline-first design and conflict resolution
- Advanced transaction management supporting income, expenses, and investments
- Recurring transaction automation
- Audio transcription for expense entry via Whisper AI
- Rate limiting and caching for performance optimization

## Target Use Cases
- Personal expense tracking
- Shared household budgets
- Team expense management
- Small business expense tracking
- Multi-currency budget management

## Key Business Logic
- Transactions are categorized and can have custom metadata
- Budgets support multiple currencies
- Conflict resolution handles concurrent edits across users
- Role-based permissions control budget access levels
- Offline-first architecture ensures data availability