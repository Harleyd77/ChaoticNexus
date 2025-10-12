import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { FileText } from 'lucide-react'

const IntakeForm = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Production Intake Form</h1>
        <p className="text-gray-600 dark:text-gray-400">Create new production jobs and work orders</p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-gray-600 dark:text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Intake Form</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">This page will integrate with your existing intake form system.</p>
            <Button variant="outline">Coming Soon</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default IntakeForm
