import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { 
  Users, 
  Briefcase, 
  Palette, 
  FileText, 
  BarChart3,
  Clock,
  CheckCircle
} from 'lucide-react'

const Dashboard = () => {
  const stats = [
    {
      title: 'Active Jobs',
      value: '24',
      description: 'Jobs in progress',
      icon: Briefcase,
      color: 'text-blue-600'
    },
    {
      title: 'Customers',
      value: '156',
      description: 'Total customers',
      icon: Users,
      color: 'text-green-600'
    },
    {
      title: 'Powder Colors',
      value: '89',
      description: 'Available colors',
      icon: Palette,
      color: 'text-purple-600'
    },
    {
      title: 'Completed Today',
      value: '7',
      description: 'Jobs finished',
      icon: CheckCircle,
      color: 'text-emerald-600'
    }
  ]

  const quickActions = [
    {
      title: 'New Job Intake',
      description: 'Create a new production job',
      href: '/intake',
      icon: FileText,
      variant: 'primary'
    },
    {
      title: 'View Jobs',
      description: 'Manage active jobs',
      href: '/jobs',
      icon: Briefcase,
      variant: 'default'
    },
    {
      title: 'Customer List',
      description: 'Manage customers',
      href: '/customers',
      icon: Users,
      variant: 'default'
    },
    {
      title: 'Powder Inventory',
      description: 'Manage powder colors',
      href: '/powders',
      icon: Palette,
      variant: 'default'
    }
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">Welcome to PowderApp React Frontend</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.title}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{stat.description}</p>
                  </div>
                  <Icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <Icon className="h-6 w-6 text-blue-600" />
                    <CardTitle className="text-lg">{action.title}</CardTitle>
                  </div>
                  <CardDescription>{action.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    variant={action.variant} 
                    className="w-full"
                    onClick={() => window.location.href = action.href}
                  >
                    Open
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div>
        <h2 className="text-2xl font-bold mb-6">Recent Activity</h2>
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                <span className="text-sm">Job #47 completed - Acme Railings</span>
                <span className="text-xs text-gray-600 dark:text-gray-400 ml-auto">2 hours ago</span>
              </div>
              <div className="flex items-center gap-3">
                <FileText className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                <span className="text-sm">New job intake - Island Fabricators</span>
                <span className="text-xs text-gray-600 dark:text-gray-400 ml-auto">4 hours ago</span>
              </div>
              <div className="flex items-center gap-3">
                <Palette className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                <span className="text-sm">Added new powder color - RAL 9005</span>
                <span className="text-xs text-gray-600 dark:text-gray-400 ml-auto">6 hours ago</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
