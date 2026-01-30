# WaqediAI Web Console

Enterprise Admin Console for WaqediAI Platform.

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query
- Axios

## Structure

```
web-console/
├── app/
│   ├── (auth)/login/
│   └── (protected)/
│       ├── dashboard/
│       ├── documents/
│       ├── knowledge/
│       ├── users/
│       └── audit/
├── core/
│   ├── api-client.ts
│   └── permissions.ts
├── services/
│   ├── auth.ts
│   ├── knowledge.ts
│   └── documents.ts
├── hooks/
│   ├── useAuth.ts
│   └── useRBAC.ts
└── middleware.ts
```

## Running

```bash
npm install
npm run dev
```

## Features

- JWT RS256 authentication
- Multi-tenant support
- RBAC enforcement
- Document management
- RAG knowledge search
