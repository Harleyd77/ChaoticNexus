# Inventory Management System

The PowderApp now includes a comprehensive inventory management system that allows you to track powder stock levels, generate reorder lists, and maintain inventory history.

## Features

### 📦 Inventory Tracking
- **Real-time Stock Levels**: Track current stock levels for all powders
- **Visual Status Indicators**: Color-coded status badges (In Stock, Low Stock, Out of Stock)
- **Configurable Thresholds**: Set custom low-stock thresholds per powder
- **Search & Filter**: Quickly find powders by name, manufacturer, or stock status

### 📊 Stock Management
- **Manual Updates**: Update stock levels with notes and timestamps
- **Stock Adjustments**: Add or subtract from current stock levels
- **Inventory History**: Complete audit trail of all stock changes
- **Bulk Operations**: Update multiple powders at once

### 🛒 Reorder Management
- **Automated Reorder Lists**: Automatically identify powders that need reordering
- **Priority Sorting**: Out-of-stock items appear first, followed by low-stock items
- **Export Options**: Print reorder lists or export to CSV
- **Order Tracking**: Mark items as ordered with supplier information

### 📈 Analytics & Reporting
- **Inventory Summary**: Overview of total powders, stock levels, and status distribution
- **Change History**: Detailed log of all inventory movements
- **Usage Patterns**: Track which powders are used most frequently
- **Cost Tracking**: Monitor powder costs and pricing changes

## Database Schema

### New Tables

#### `inventory_log`
Tracks all inventory changes with full audit trail:
- `id`: Primary key
- `powder_id`: Reference to powders table
- `change_type`: Type of change (manual_update, adjustment_add, adjustment_subtract, etc.)
- `old_value`: Previous stock level
- `new_value`: New stock level
- `notes`: Optional notes about the change
- `created_at`: Timestamp of the change
- `created_by`: User who made the change

#### `reorder_settings`
Configurable reorder settings per powder:
- `id`: Primary key
- `powder_id`: Reference to powders table
- `low_stock_threshold`: Custom threshold for low stock alerts
- `reorder_quantity`: Suggested reorder quantity
- `supplier_info`: Supplier contact information
- `notes`: Additional notes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Enhanced `powders` Table
The existing powders table already includes inventory fields:
- `on_hand_kg`: Current physical stock level
- `in_stock`: Legacy stock field (for compatibility)
- `last_weighed_kg`: Last recorded weight
- `last_weighed_at`: Timestamp of last weighing
- `weight_box_kg`: Weight per box/container

## API Endpoints

### Inventory Management
- `GET /inventory` - Main inventory management page
- `GET /inventory/api/powders` - JSON API for powder inventory data
- `POST /inventory/api/update` - Update powder stock levels
- `GET /inventory/api/reorder` - Get reorder list data

### Stock Operations
- `POST /inventory/<id>/update` - Update specific powder stock
- `POST /inventory/<id>/adjust` - Adjust stock level (add/subtract)
- `GET /inventory/history/<id>` - View inventory history for a powder

### Reorder Management
- `GET /inventory/reorder` - Reorder list page
- `POST /inventory/reorder/mark-ordered` - Mark items as ordered

## Frontend Components

### React Components
- `Inventory.jsx` - Main inventory management interface
- `ReorderList.jsx` - Reorder list and ordering interface
- Enhanced `Layout.jsx` - Added inventory navigation

### Features
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live data updates without page refresh
- **Interactive Filters**: Filter by stock status, search by name/manufacturer
- **Modal Dialogs**: Quick stock updates and adjustments
- **Export Functions**: Print and CSV export capabilities

## Usage Guide

### Setting Up Inventory

1. **Initial Stock Entry**: For existing powders, update the `on_hand_kg` field with current stock levels
2. **Configure Thresholds**: Set appropriate low-stock thresholds (default: 5kg)
3. **Set Reorder Quantities**: Define how much to order when stock runs low

### Daily Operations

1. **Check Inventory Status**: Visit `/inventory` to see current stock levels
2. **Update Stock**: Use the Update button to record new stock levels after receiving shipments
3. **Adjust Stock**: Use the Adjust button for daily usage tracking
4. **Generate Reorder Lists**: Visit `/reorder` to see what needs to be ordered

### Best Practices

1. **Regular Updates**: Update stock levels after each shipment received
2. **Usage Tracking**: Record powder usage for jobs to maintain accurate counts
3. **Supplier Management**: Keep supplier information up to date in reorder settings
4. **Audit Trail**: Always add notes when making significant stock changes

## Integration Points

### With Existing Systems
- **Jobs System**: Track powder usage per job (future enhancement)
- **Customer Portal**: Allow customers to see powder availability (future enhancement)
- **Billing System**: Integrate with pricing for accurate cost tracking (future enhancement)

### Data Migration
If you have existing inventory data:
1. Import powder data with current stock levels in the `on_hand_kg` field
2. Set appropriate low-stock thresholds based on your usage patterns
3. Configure supplier information for automatic reordering

## Security & Permissions

- **Admin Only**: Stock updates and adjustments require admin privileges
- **View Access**: Regular users can view inventory status but cannot make changes
- **Audit Trail**: All changes are logged with user information and timestamps

## Future Enhancements

- **Barcode Scanning**: Mobile app integration for quick stock updates
- **Automated Alerts**: Email notifications for low stock levels
- **Supplier Integration**: Direct ordering through supplier APIs
- **Usage Analytics**: Track powder consumption patterns
- **Cost Analysis**: Detailed cost tracking and margin analysis
- **Multi-location Support**: Track inventory across multiple locations

## Troubleshooting

### Common Issues

1. **Stock Levels Not Updating**: Check database permissions and ensure inventory_log table exists
2. **Reorder List Empty**: Verify low-stock thresholds are set correctly
3. **History Not Showing**: Ensure inventory_log table has proper indexes

### Database Maintenance

- **Archive Old History**: Consider archiving inventory_log entries older than 2 years
- **Optimize Performance**: Regular database maintenance for large inventory_log tables
- **Backup Strategy**: Include inventory data in regular database backups

## Support

For issues or questions about the inventory management system:
1. Check the application logs for error messages
2. Verify database table structure matches the schema above
3. Ensure proper user permissions are configured
4. Review the API endpoints for proper integration

The inventory management system is designed to be robust, scalable, and user-friendly while maintaining data integrity and providing comprehensive audit trails.
