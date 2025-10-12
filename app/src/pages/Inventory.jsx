import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/Card'
import { Button } from '../components/Button'
import { Package, AlertTriangle, CheckCircle, XCircle, Search, Filter, Plus, ShoppingCart, ArrowLeft, Download, Upload } from 'lucide-react'

const Inventory = () => {
  const [powders, setPowders] = useState([])
  const [filteredPowders, setFilteredPowders] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filter, setFilter] = useState('all')
  const [lowStockThreshold, setLowStockThreshold] = useState(5.0)

  useEffect(() => {
    fetchInventoryData()
  }, [])

  useEffect(() => {
    filterPowders()
  }, [powders, searchTerm, filter, lowStockThreshold])

  const fetchInventoryData = async () => {
    try {
      const response = await fetch('/inventory/api/powders')
      if (response.ok) {
        const data = await response.json()
        setPowders(data)
      }
    } catch (error) {
      console.error('Error fetching inventory data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterPowders = () => {
    let filtered = powders

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(powder =>
        powder.powder_color.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (powder.manufacturer && powder.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // Apply status filter
    const stockKg = (powder) => powder.on_hand_kg || powder.in_stock || 0
    
    switch (filter) {
      case 'out':
        filtered = filtered.filter(powder => stockKg(powder) <= 0)
        break
      case 'low':
        filtered = filtered.filter(powder => {
          const stock = stockKg(powder)
          return stock > 0 && stock <= lowStockThreshold
        })
        break
      case 'good':
        filtered = filtered.filter(powder => stockKg(powder) > lowStockThreshold)
        break
      default:
        // 'all' - no additional filtering
        break
    }

    setFilteredPowders(filtered)
  }

  const getStockStatus = (powder) => {
    const stock = powder.on_hand_kg || powder.in_stock || 0
    if (stock <= 0) return { status: 'out', label: 'Out of Stock', color: 'text-red-600 bg-red-100' }
    if (stock <= lowStockThreshold) return { status: 'low', label: 'Low Stock', color: 'text-orange-600 bg-orange-100' }
    return { status: 'good', label: 'In Stock', color: 'text-green-600 bg-green-100' }
  }

  const getInventoryStats = () => {
    const outOfStock = powders.filter(p => (p.on_hand_kg || p.in_stock || 0) <= 0).length
    const lowStock = powders.filter(p => {
      const stock = p.on_hand_kg || p.in_stock || 0
      return stock > 0 && stock <= lowStockThreshold
    }).length
    const inStock = powders.filter(p => (p.on_hand_kg || p.in_stock || 0) > lowStockThreshold).length

    return { total: powders.length, outOfStock, lowStock, inStock }
  }

  const updateStock = async (powderId, newStock, notes = '') => {
    try {
      const response = await fetch('/inventory/api/update', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          powder_id: powderId,
          on_hand_kg: newStock,
          notes: notes
        })
      })

      if (response.ok) {
        await fetchInventoryData()
        return true
      }
      return false
    } catch (error) {
      console.error('Error updating stock:', error)
      return false
    }
  }

  const stats = getInventoryStats()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Package className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading inventory...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Top Navigation Bar */}
      <div className="flex justify-between items-center flex-wrap gap-3">
        <div className="flex gap-2 flex-wrap items-center">
          <Button variant="outline" onClick={() => window.location.href = '/powders'}>
            <ArrowLeft className="h-4 w-4" />
            Back to Powders
          </Button>
          <Button variant="outline" onClick={() => window.location.href = '/reorder'}>
            <ShoppingCart className="h-4 w-4" />
            Reorder List
          </Button>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      {/* Main Header */}
      <div className="bg-panel border border-border rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-text mb-2">Inventory Management</h1>
            <p className="text-muted">Track and manage powder stock levels</p>
            <div className="flex items-center gap-4 mt-3">
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
                <Package className="h-4 w-4" />
                {stats.total} Total Powders
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm font-medium">
                <CheckCircle className="h-4 w-4" />
                {stats.inStock} In Stock
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-orange-500/10 text-orange-500 rounded-full text-sm font-medium">
                <AlertTriangle className="h-4 w-4" />
                {stats.lowStock} Low Stock
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1 bg-red-500/10 text-red-500 rounded-full text-sm font-medium">
                <XCircle className="h-4 w-4" />
                {stats.outOfStock} Out of Stock
              </span>
            </div>
          </div>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted" />
              <input
                type="text"
                placeholder="Search powders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-input border border-border rounded-lg text-text placeholder-muted focus:ring-2 focus:ring-primary focus:border-primary"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-text">Low stock threshold:</label>
            <input
              type="number"
              value={lowStockThreshold}
              onChange={(e) => setLowStockThreshold(parseFloat(e.target.value))}
              step="0.1"
              min="0"
              className="w-20 px-2 py-1 bg-input border border-border rounded text-sm text-text"
            />
            <span className="text-sm text-muted">kg</span>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="border-b border-border mt-6">
          <nav className="flex space-x-8">
            <button
              onClick={() => setFilter('all')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === 'all'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted hover:text-text'
              }`}
            >
              All Powders
            </button>
            <button
              onClick={() => setFilter('out')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === 'out'
                  ? 'border-red-500 text-red-500'
                  : 'border-transparent text-muted hover:text-text'
              }`}
            >
              Out of Stock ({stats.outOfStock})
            </button>
            <button
              onClick={() => setFilter('low')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === 'low'
                  ? 'border-orange-500 text-orange-500'
                  : 'border-transparent text-muted hover:text-text'
              }`}
            >
              Low Stock ({stats.lowStock})
            </button>
            <button
              onClick={() => setFilter('good')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === 'good'
                  ? 'border-green-500 text-green-500'
                  : 'border-transparent text-muted hover:text-text'
              }`}
            >
              In Stock ({stats.inStock})
            </button>
          </nav>
        </div>
      </div>

      {/* Inventory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPowders.map((powder) => {
          const stock = powder.on_hand_kg || powder.in_stock || 0
          const status = getStockStatus(powder)
          
          return (
            <div 
              key={powder.id} 
              className="bg-panel border border-border rounded-lg p-6 hover:shadow-lg transition-all duration-200 cursor-pointer hover:border-primary/30"
              style={{
                background: 'linear-gradient(180deg, color-mix(in oklab, var(--panel), var(--primary) 4%), color-mix(in oklab, var(--panel-2), var(--primary) 2%))',
                borderColor: 'color-mix(in oklab, var(--border), var(--primary) 15%)',
                boxShadow: '0 2px 0 rgba(0,0,0,.05), 0 8px 16px rgba(0,0,0,.1)'
              }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-text mb-1">{powder.powder_color}</h3>
                  {powder.manufacturer && (
                    <p className="text-sm text-muted mb-1">{powder.manufacturer}</p>
                  )}
                  {powder.product_code && (
                    <p className="text-xs text-muted">{powder.product_code}</p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  status.status === 'out' ? 'bg-red-500/20 text-red-400' :
                  status.status === 'low' ? 'bg-orange-500/20 text-orange-400' :
                  'bg-green-500/20 text-green-400'
                }`}>
                  {status.label}
                </span>
              </div>

              <div className="space-y-2 text-sm mb-4">
                <div className="flex justify-between">
                  <span className="text-muted">Current Stock:</span>
                  <span className="font-medium text-text">{stock} kg</span>
                </div>
                
                {powder.weight_box_kg && (
                  <div className="flex justify-between">
                    <span className="text-muted">Box Weight:</span>
                    <span className="text-text">{powder.weight_box_kg} kg</span>
                  </div>
                )}

                {powder.last_weighed_at && (
                  <div className="flex justify-between">
                    <span className="text-muted">Last Weighed:</span>
                    <span className="text-text">{powder.last_weighed_at.substring(0, 10)}</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Button 
                  size="sm" 
                  className="flex-1"
                  onClick={() => {
                    const newStock = prompt(`Enter new stock level for ${powder.powder_color} (kg):`, stock)
                    if (newStock !== null && !isNaN(newStock)) {
                      updateStock(powder.id, parseFloat(newStock))
                    }
                  }}
                >
                  Update
                </Button>
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => {
                    const adjustment = prompt(`Enter adjustment amount for ${powder.powder_color} (kg):`, '')
                    if (adjustment !== null && !isNaN(adjustment)) {
                      const newStock = stock + parseFloat(adjustment)
                      updateStock(powder.id, Math.max(0, newStock))
                    }
                  }}
                >
                  Adjust
                </Button>
              </div>
            </div>
          )
        })}
      </div>

      {filteredPowders.length === 0 && (
        <div className="text-center py-12">
          <Package className="h-12 w-12 text-muted mx-auto mb-4" />
          <h3 className="text-lg font-medium text-text mb-2">No powders found</h3>
          <p className="text-muted">
            {searchTerm ? 'Try adjusting your search terms.' : 'No powders match the current filter.'}
          </p>
        </div>
      )}
    </div>
  )
}

export default Inventory
