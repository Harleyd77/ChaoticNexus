import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { Toaster } from "@/components/ui/toaster"
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import Customers from './pages/Customers'
import Powders from './pages/Powders'
import Inventory from './pages/Inventory'
import ReorderList from './pages/ReorderList'
import IntakeForm from './pages/IntakeForm'
import ShadcnShowcase from './pages/ShadcnShowcase'
import Login from './pages/Login'

function App() {
  return (
    <ThemeProvider>
      <Router basename="/react">
        <Routes>
          {/* Login page without Layout */}
          <Route path="/login" element={<Login />} />
          
          {/* Dashboard route */}
          <Route path="/dashboard" element={
            <Layout>
              <Dashboard />
            </Layout>
          } />
          
          {/* All other routes with Layout */}
          <Route path="/" element={
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route path="/customers" element={<Customers />} />
                <Route path="/powders" element={<Powders />} />
                <Route path="/inventory" element={<Inventory />} />
                <Route path="/reorder" element={<ReorderList />} />
                <Route path="/intake" element={<IntakeForm />} />
                <Route path="/shadcn" element={<ShadcnShowcase />} />
              </Routes>
            </Layout>
          } />
        </Routes>
        <Toaster />
      </Router>
    </ThemeProvider>
  )
}

export default App
