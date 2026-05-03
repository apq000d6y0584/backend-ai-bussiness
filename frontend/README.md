# BI-AI Engine Frontend

This is a Next.js frontend application for the BI-AI Engine project. It features a stock chart visualization component and is built with TypeScript, Tailwind CSS, and modern React patterns.

## Project Structure

```
frontend/
├── app/                  # Next.js App Router pages and layouts
│   ├── globals.css       # Global Tailwind CSS styles
│   ├── layout.tsx        # Root layout component
│   └── page.tsx          # Home page component
├── components/           # Reusable React components
│   └── StockChart.tsx    # Interactive stock chart visualization
├── types/                # TypeScript type definitions
│   └── api.ts            # API response types (e.g., for stock data)
├── next.config.mjs       # Next.js configuration
├── package.json          # Dependencies and scripts
├── postcss.config.mjs    # PostCSS config for Tailwind
├── tailwind.config.ts    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
└── README.md             # This file
```

## Key Features

- **Stock Chart Visualization**: `components/StockChart.tsx` renders interactive charts for stock data, likely using libraries like Chart.js, Recharts, or D3 (check implementation details).
- **Type-Safe API Integration**: Types defined in `types/api.ts` for handling backend API responses.
- **Responsive Design**: Powered by Tailwind CSS for mobile-first, responsive UI.
- **Next.js 13+ App Router**: Server-side rendering, static generation, and modern routing.

## Local Setup & Usage

### Prerequisites
- Node.js (v18+ recommended)
- npm or yarn

### Installation
1. Clone or navigate to the project directory:
   ```
   cd c:/Users/USER/OneDrive/Dokumen/anaconda_projects/bi-ai-engine/frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```
   or
   ```
   yarn install
   ```

### Development Server
Run the app in development mode:
```
npm run dev
```
or
```
yarn dev
```

- Open [http://localhost:3000](http://localhost:3000) in your browser.
- The home page (`app/page.tsx`) will load, featuring the StockChart component.

### Build for Production
```
npm run build
```
Then start the production server:
```
npm run start
```

### Available Scripts (from package.json)
- `dev`: Start dev server
- `build`: Build for production
- `start`: Run production server
- `lint`: Run ESLint

### Backend Integration
- This frontend likely connects to a backend API (e.g., for stock data).
- Configure API endpoints in components (e.g., StockChart fetches from `/api/stocks`).
- Update `types/api.ts` if API contracts change.
- Ensure the backend (possibly in a sibling directory) is running on the expected port.

### Customization
- **Add Components**: Place in `components/`.
- **Styles**: Extend `globals.css` or Tailwind config.
- **Pages**: Add routes in `app/`.
- **Types**: Update `types/api.ts` for new endpoints.

## Troubleshooting
- **Port Conflict**: Use `npm run dev -- -p 3001`.
- **Type Errors**: Run `npm run type-check`.
- **Tailwind Issues**: Ensure `tailwind.config.ts` includes all source paths.
- **Dependencies**: Delete `node_modules` and `package-lock.json`, then reinstall.

## Tech Stack
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- React 18+

For issues, check console logs or open an issue.

Happy coding! 🚀

