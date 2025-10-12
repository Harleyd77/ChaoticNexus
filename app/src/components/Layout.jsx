import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'
import { Button } from './Button'
import { Sun, Moon, Home, Briefcase, Users, Palette, Package, ShoppingCart, FileText } from 'lucide-react'

const Layout = ({ children }) => {
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Jobs', href: '/jobs', icon: Briefcase },
    { name: 'Customers', href: '/customers', icon: Users },
    { name: 'Powders', href: '/powders', icon: Palette },
    { name: 'Inventory', href: '/inventory', icon: Package },
    { name: 'Reorder List', href: '/reorder', icon: ShoppingCart },
    { name: 'Intake', href: '/intake', icon: FileText },
  ]

  const isActive = (href) => location.pathname === href

  return (
    <div className="min-h-screen bg-bg text-text">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-panel border-r border-border min-h-screen">
          <div className="p-6 border-b border-border">
            <h1 className="text-xl font-bold">PowderApp</h1>
            <span className="text-sm text-muted">React Frontend</span>
          </div>
          
          <nav className="p-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                        isActive(item.href)
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted hover:text-text hover:bg-accent'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <header className="sticky top-0 z-50 border-b border-border bg-panel/80 backdrop-blur-sm">
            <div className="flex h-16 items-center justify-between px-6">
              <div className="flex items-center gap-4">
                <h2 className="text-lg font-semibold">
                  {navigation.find(item => isActive(item.href))?.name || 'Dashboard'}
                </h2>
              </div>
              
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleTheme}
                  className="h-9 w-9 p-0"
                >
                  {theme === 'dark' ? (
                    <Sun className="h-4 w-4" />
                  ) : (
                    <Moon className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-border bg-panel/50">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted">
            PowderApp React Frontend - Built with ReactBits
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Layout
