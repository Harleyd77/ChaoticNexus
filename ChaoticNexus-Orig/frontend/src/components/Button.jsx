import React from 'react'
import { cn } from '../utils/cn'

const Button = React.forwardRef(({ 
  className, 
  variant = 'default', 
  size = 'default', 
  children, 
  ...props 
}, ref) => {
  const variants = {
    default: 'bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400',
    primary: 'bg-blue-600 dark:bg-blue-700 text-white border-blue-600 dark:border-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600',
    secondary: 'bg-gray-100/80 dark:bg-gray-700/80 text-gray-600 dark:text-gray-300 border-gray-300/60 dark:border-gray-600/60 hover:bg-gray-100 dark:hover:bg-gray-700',
    success: 'bg-green-600 text-white border-green-600 hover:bg-green-700',
    warning: 'bg-yellow-600 text-white border-yellow-600 hover:bg-yellow-700',
    danger: 'bg-red-600 text-white border-red-600 hover:bg-red-700',
    outline: 'bg-transparent text-blue-600 dark:text-blue-400 border-blue-600 dark:border-blue-400 hover:bg-blue-600 dark:hover:bg-blue-700 hover:text-white',
    ghost: 'bg-transparent text-gray-600 dark:text-gray-400 border-transparent hover:bg-gray-100 dark:hover:bg-gray-800'
  }

  const sizes = {
    sm: 'h-8 px-3 text-xs',
    default: 'h-10 px-4 py-2 text-sm',
    lg: 'h-12 px-6 text-base',
    xl: 'h-14 px-8 text-lg'
  }

  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-lg border font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/20 disabled:pointer-events-none disabled:opacity-50',
        variants[variant],
        sizes[size],
        className
      )}
      ref={ref}
      {...props}
    >
      {children}
    </button>
  )
})

Button.displayName = 'Button'

export { Button }
