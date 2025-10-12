import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { Plus, Search, Filter, MoreHorizontal } from 'lucide-react'

const Jobs = () => {
  const jobs = [
    {
      id: 47,
      company: 'Acme Railings',
      description: 'Prep 12 balcony pickets and 3 posts. Sandblast light rust, prime TGIC, topcoat RAL 9005 matte.',
      status: 'In Progress',
      priority: 'Standard',
      dueDate: '2025-10-01',
      color: 'RAL 9005 Matte'
    },
    {
      id: 48,
      company: 'Island Fabricators',
      description: 'Gate frame 4x8 ft, heavy mill scale. Two-coat with zinc prime + RAL 7016.',
      status: 'Pending',
      priority: 'Rush',
      dueDate: '2025-09-30',
      color: 'RAL 7016'
    },
    {
      id: 49,
      company: 'Westbay Marine',
      description: 'Boat rail sections, 316 stainless scuff & clear. Mask mounting faces.',
      status: 'Completed',
      priority: 'Standard',
      dueDate: '2025-09-28',
      color: 'Clear Coat'
    }
  ]

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'text-green-600 bg-green-100'
      case 'In Progress':
        return 'text-blue-600 bg-blue-100'
      case 'Pending':
        return 'text-yellow-600 bg-yellow-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Emergency':
        return 'text-red-600 bg-red-100'
      case 'Rush':
        return 'text-orange-600 bg-orange-100'
      case 'Standard':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Jobs</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage production jobs and work orders</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          New Job
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-600 dark:text-gray-400" />
              <input
                type="text"
                placeholder="Search jobs..."
                className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-600 dark:placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 dark:focus:ring-blue-400/20"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <Filter className="h-4 w-4" />
              Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.map((job) => (
          <Card key={job.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">Job #{job.id}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(job.priority)}`}>
                      {job.priority}
                    </span>
                  </div>
                  <h4 className="text-base font-medium text-gray-900 dark:text-gray-100 mb-1">{job.company}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{job.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>Due: {job.dueDate}</span>
                    <span>Color: {job.color}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    Edit
                  </Button>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default Jobs
