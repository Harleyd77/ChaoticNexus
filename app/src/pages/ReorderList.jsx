import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { ShoppingCart, AlertTriangle, Package, Download, Printer, CheckCircle, Edit, History, ArrowLeft } from 'lucide-react'

const ReorderList = () => {
  const [reorderItems, setReorderItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [orderNotes, setOrderNotes] = useState('')

  useEffect(() => {
    fetchReorderData()
    loadSavedNotes()
  }, [])

  const fetchReorderData = async () => {
    try {
      const response = await fetch('/inventory/api/reorder')
      if (response.ok) {
        const data = await response.json()
        setReorderItems(data)
      }
    } catch (error) {
      console.error('Error fetching reorder data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSavedNotes = () => {
    const savedNotes = localStorage.getItem('reorderNotes')
    if (savedNotes) {
      setOrderNotes(savedNotes)
    }
  }

  const saveNotes = () => {
    localStorage.setItem('reorderNotes', orderNotes)
    alert('Notes saved!')
  }

  const exportToCSV = () => {
    const csvContent = [
      ['Powder Color', 'Manufacturer', 'Product Code', 'Color Family', 'Current Stock (kg)', 'Box Weight (kg)', 'Price per kg ($)'],
      ...reorderItems.map(item => [
        item.powder_color,
        item.manufacturer || '',
        item.product_code || '',
        item.color_family || '',
        item.on_hand_kg || item.in_stock || 0,
        item.weight_box_kg || '',
        item.price_per_kg || ''
      ])
    ].map(row => row.map(cell => `"${cell}"`).join(',')).join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `reorder_list_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const printList = () => {
    const printContent = document.querySelector('.reorder-content').innerHTML
    const printWindow = window.open('', '', 'height=600,width=800')
    printWindow.document.write(`
      <html>
        <head>
          <title>Reorder List - ${new Date().toLocaleDateString()}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .bg-white { background: white !important; }
            .text-gray-900 { color: black !important; }
            .text-gray-600 { color: #666 !important; }
            .border { border: 1px solid #ddd !important; }
            .rounded-lg { border-radius: 4px !important; }
            .shadow-sm { box-shadow: none !important; }
            .mb-8 { margin-bottom: 20px !important; }
            .mb-6 { margin-bottom: 15px !important; }
            .mb-4 { margin-bottom: 10px !important; }
            .p-6 { padding: 15px !important; }
            .space-y-4 > * + * { margin-top: 15px !important; }
            .grid { display: block !important; }
            .grid > * { margin-bottom: 10px !important; }
            .flex { display: block !important; }
            .hidden { display: none !important; }
            .priority-out { border-left: 4px solid #dc2626; padding-left: 15px; }
            .priority-low { border-left: 4px solid #d97706; padding-left: 15px; }
          </style>
        </head>
        <body>
          ${printContent}
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }

  const markAsOrdered = (item) => {
    const quantity = prompt(`Enter quantity ordered for ${item.powder_color} (kg):`, '')
    const supplier = prompt(`Enter supplier for ${item.powder_color}:`, '')
    
    if (quantity !== null && !isNaN(quantity)) {
      // Here you would typically send this to your backend
      alert(`Marked ${item.powder_color} as ordered: ${quantity} kg from ${supplier}`)
      // Remove from reorder list or mark as ordered
      setReorderItems(prev => prev.filter(i => i.id !== item.id))
    }
  }

  const getPriorityClass = (item) => {
    const stock = item.on_hand_kg || item.in_stock || 0
    return stock <= 0 ? 'priority-out' : 'priority-low'
  }

  const getPriorityBadge = (item) => {
    const stock = item.on_hand_kg || item.in_stock || 0
    if (stock <= 0) {
      return { label: 'OUT OF STOCK', color: 'bg-red-100 text-red-800' }
    } else {
      return { label: 'LOW STOCK', color: 'bg-orange-100 text-orange-800' }
    }
  }

  const getStats = () => {
    const outOfStock = reorderItems.filter(item => (item.on_hand_kg || item.in_stock || 0) <= 0).length
    const lowStock = reorderItems.length - outOfStock
    return { total: reorderItems.length, outOfStock, lowStock }
  }

  const stats = getStats()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading reorder list...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="reorder-content space-y-6">
      {/* Top Navigation Bar */}
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div className="flex gap-2 flex-wrap items-center">
          <Button variant="outline" onClick={() => window.location.href = '/powders'}>
            <ArrowLeft className="h-4 w-4" />
            Back to Powders
          </Button>
          <Button variant="outline" onClick={() => window.location.href = '/inventory'}>
            <Package className="h-4 w-4" />
            Inventory Management
          </Button>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={printList} className="gap-2">
            <Printer className="h-4 w-4" />
            Print List
          </Button>
          <Button variant="outline" onClick={exportToCSV} className="gap-2">
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Main Header */}
      <div className="bg-panel border border-border rounded-lg p-6">
        <div>
          <h1 className="text-3xl font-bold text-text mb-2">Reorder List</h1>
          <p className="text-muted">Powders that need to be reordered</p>
        </div>
      </div>

      {/* Summary */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
              <div className="text-sm text-gray-600">Total Items to Reorder</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{stats.outOfStock}</div>
              <div className="text-sm text-gray-600">Out of Stock</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{stats.lowStock}</div>
              <div className="text-sm text-gray-600">Low Stock</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reorder Items */}
      {reorderItems.length > 0 ? (
        <div className="space-y-4">
          {reorderItems.map((item) => {
            const stock = item.on_hand_kg || item.in_stock || 0
            const priority = getPriorityBadge(item)
            
            return (
              <Card key={item.id} className={`${getPriorityClass(item)} hover:shadow-lg transition-shadow`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{item.powder_color}</h3>
                        <span className={`text-xs font-medium px-2.5 py-0.5 rounded ${priority.color}`}>
                          {priority.label}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="font-medium text-gray-700">Manufacturer:</span>
                          <span className="text-gray-900 ml-2">{item.manufacturer || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Product Code:</span>
                          <span className="text-gray-900 ml-2">{item.product_code || 'N/A'}</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Color Family:</span>
                          <span className="text-gray-900 ml-2">{item.color_family || 'N/A'}</span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mt-3">
                        <div>
                          <span className="font-medium text-gray-700">Current Stock:</span>
                          <span className="text-gray-900 ml-2">{stock} kg</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Box Weight:</span>
                          <span className="text-gray-900 ml-2">{item.weight_box_kg || 'N/A'} kg</span>
                        </div>
                        <div>
                          <span className="font-medium text-gray-700">Price per kg:</span>
                          <span className="text-gray-900 ml-2">${item.price_per_kg || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="ml-6 flex flex-col space-y-2">
                      <Button 
                        size="sm" 
                        onClick={() => markAsOrdered(item)}
                        className="bg-green-500 hover:bg-green-600 text-white"
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Mark as Ordered
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => window.open(`/powders/${item.id}/edit`, '_blank')}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Edit Powder
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => window.open(`/inventory/history/${item.id}`, '_blank')}
                      >
                        <History className="h-4 w-4 mr-1" />
                        History
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">All stocked up!</h3>
            <p className="text-gray-600">No powders need to be reordered at this time.</p>
          </CardContent>
        </Card>
      )}

      {/* Order Notes Section */}
      {reorderItems.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Order Notes</CardTitle>
            <CardDescription>Add notes for your powder order</CardDescription>
          </CardHeader>
          <CardContent>
            <textarea
              value={orderNotes}
              onChange={(e) => setOrderNotes(e.target.value)}
              rows={4}
              placeholder="Add notes for your powder order..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <div className="mt-4 flex justify-end">
              <Button onClick={saveNotes} className="gap-2">
                <CheckCircle className="h-4 w-4" />
                Save Notes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ReorderList
