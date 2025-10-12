# PowderApp React Frontend

This is the React frontend for PowderApp, built with ReactBits components and integrated with the existing Flask backend.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm run dev
```
This will start the Vite dev server on http://localhost:3000

### Production Build
```bash
npm run build
```
This will build the React app and output to `../src/powder_app/static/dist/`

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable React components
│   ├── pages/         # Page components
│   ├── contexts/      # React contexts (theme, etc.)
│   ├── utils/         # Utility functions
│   ├── App.jsx        # Main app component
│   └── main.jsx       # Entry point
├── public/            # Static assets
├── package.json       # Dependencies
├── vite.config.js     # Vite configuration
├── tailwind.config.js # Tailwind CSS config
└── build.sh          # Build script
```

## 🎨 Components

### Button
A versatile button component with multiple variants:
- `default`, `primary`, `secondary`, `success`, `warning`, `danger`, `outline`, `ghost`
- Sizes: `sm`, `default`, `lg`, `xl`

### Card
Card components for content organization:
- `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`

## 🎯 Integration with Flask

The React app is served through Flask at `/react` and integrates with your existing:
- Theme system (dark/light mode)
- Authentication
- API endpoints
- Static file serving

## 🔧 Customization

### Theme
The app uses your existing CSS variables and theme system. Colors and styling match your current design.

### Adding New Components
1. Create component in `src/components/`
2. Export from appropriate index files
3. Use in pages or other components

### API Integration
The app is configured to proxy API calls to your Flask backend at `http://localhost:5000/api`

## 📱 Features

- ✅ Responsive design
- ✅ Dark/light theme support
- ✅ ReactBits component library
- ✅ Tailwind CSS styling
- ✅ TypeScript support (optional)
- ✅ Hot reload in development
- ✅ Production build optimization

## 🚀 Deployment

1. Run `npm run build` to create production build
2. The built files will be in `../src/powder_app/static/dist/`
3. Flask will serve the React app at `/react`

## 🔗 Links

- [ReactBits Documentation](https://reactbits.dev)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
