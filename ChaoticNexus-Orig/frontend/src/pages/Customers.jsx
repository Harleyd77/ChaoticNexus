import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { Users, Plus, Search } from 'lucide-react'

const Customers = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Customers</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage customer information and contacts</p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          New Customer
        </Button>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="text-center py-12">
            <Users className="h-12 w-12 text-gray-600 dark:text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Customers Page</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">This page will integrate with your existing customer management system.</p>
            <Button variant="outline">Coming Soon</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Customers
