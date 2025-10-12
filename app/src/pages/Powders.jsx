import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { Palette, Plus, Package } from 'lucide-react'

const Powders = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Powder Inventory</h1>
          <p className="text-muted">Manage powder colors and specifications</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2" onClick={() => window.location.href = '/inventory'}>
            <Package className="h-4 w-4" />
            Manage Inventory
          </Button>
          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            New Powder
          </Button>
        </div>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="text-center py-12">
            <Palette className="h-12 w-12 text-muted mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Powder Inventory</h3>
            <p className="text-muted mb-4">This page will integrate with your existing powder management system.</p>
            <Button variant="outline">Coming Soon</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Powders
