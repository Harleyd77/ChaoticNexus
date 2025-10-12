import React, { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('dark')

  useEffect(() => {
    // Get theme from cookie or localStorage
    const getTheme = () => {
      try {
        const cookieMatch = document.cookie.match(/(?:^|; )vpc_theme=([^;]+)/)
        const saved = (cookieMatch ? decodeURIComponent(cookieMatch[1]) : null) || 
                     localStorage.getItem('vpc_theme') || 'light'
        return saved
      } catch (e) {
        return 'light'
      }
    }

    const currentTheme = getTheme()
    setTheme(currentTheme)
    
    // Apply Tailwind dark mode class
    if (currentTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    
    // Apply Tailwind dark mode class
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    
    // Save to cookie and localStorage
    try {
      document.cookie = `vpc_theme=${newTheme}; path=/; max-age=31536000`
      localStorage.setItem('vpc_theme', newTheme)
    } catch (e) {
      console.warn('Could not save theme preference:', e)
    }
  }

  const value = {
    theme,
    toggleTheme,
    isDark: theme === 'dark'
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}
