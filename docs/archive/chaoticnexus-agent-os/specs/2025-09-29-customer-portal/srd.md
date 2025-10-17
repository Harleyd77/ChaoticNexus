# Customer Portal Feature Specification

## Spec Overview

**Spec ID**: 2025-09-29-customer-portal
**Created**: September 29, 2025
**Priority**: Medium
**Effort**: 2-3 weeks
**Owner**: Development Team

## Goals & Success Criteria

### Primary Goals
1. **Customer Self-Service**: Allow customers to check job status without calling the shop
2. **Improved Communication**: Reduce phone inquiries about job progress
3. **Professional Image**: Provide modern, professional customer experience
4. **Operational Efficiency**: Free up staff time for shop operations

### Success Metrics
- **Usage Rate**: 40% of customers actively use the portal within 3 months
- **Satisfaction**: 85%+ customer satisfaction with portal experience
- **Efficiency**: 30% reduction in status-related phone calls
- **Performance**: <2 second page load times for status checks

## User Stories

### As a Customer
- **US1**: I want to check my job status online so I don't need to call the shop
- **US2**: I want to see estimated completion dates so I can plan accordingly
- **US3**: I want to view job details and specifications so I know what's being worked on
- **US4**: I want to see my job history so I can reference past projects
- **US5**: I want a simple, mobile-friendly interface so I can check on my phone

### As a Shop Operator
- **US6**: I want to provide job updates that customers can see immediately
- **US7**: I want to reduce time spent answering status calls
- **US8**: I want customers to have access to their project information 24/7

## Functional Requirements

### Core Features
1. **Customer & Admin Authentication**
   - Unified login screen that offers both admin and customer authentication
   - Customers authenticate with email/password; admins with username/password
   - Session management with automatic logout and cross-role awareness

2. **Job Status Dashboard**
   - List of customer's active jobs with current status
   - Visual status indicators (Not Started, In Progress, Quality Check, Ready for Pickup, Completed)
   - Estimated completion dates
   - Basic job details (description, quantity, special instructions)

3. **Job Details View**
   - Complete job specifications and requirements
   - Progress updates and notes from shop
   - Photo uploads of work in progress (if enabled)
   - Contact information for shop communication

4. **Job History**
   - Archive of completed jobs
   - Search and filter capabilities
   - Download invoices/receipts (future feature)

5. **Mobile-Responsive Design**
   - Works well on phones and tablets
   - Touch-friendly interface
   - Fast loading on mobile networks

### Technical Requirements
- **Security**: No customer data exposed, secure authentication
- **Performance**: Pages load in under 2 seconds
- **Accessibility**: WCAG 2.1 AA compliance
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge)
- **Mobile**: Responsive design for all screen sizes

## Non-Functional Requirements

### Security
- Secure authentication system
- No sensitive data in URLs
- Session timeout after inactivity
- Input validation and sanitization
- HTTPS encryption for all communications

### Performance
- Page load time: <2 seconds on 3G
- Database query optimization
- Efficient caching of job data
- Minimal JavaScript bundle size

### Usability
- Intuitive navigation
- Clear status indicators
- Helpful error messages
- Loading states for all actions

## Technical Specifications

### Architecture
- **Frontend**: HTML templates with minimal JavaScript
- **Backend**: Flask routes with Blueprint organization
- **Database**: Extended customer and job tables
- **Authentication**: Custom session-based auth
- **Styling**: Bootstrap-based responsive design

### Database Changes
```sql
-- Add customer portal access fields
ALTER TABLE customers ADD COLUMN portal_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE customers ADD COLUMN portal_login_token VARCHAR(255);
ALTER TABLE customers ADD COLUMN portal_last_login TIMESTAMP;

-- Add job progress tracking
ALTER TABLE jobs ADD COLUMN customer_notes TEXT;
ALTER TABLE jobs ADD COLUMN shop_notes TEXT;
ALTER TABLE jobs ADD COLUMN progress_percentage INTEGER DEFAULT 0;

-- Add job status history
CREATE TABLE job_status_history (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    updated_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints
- `GET /login` - Unified login page for admins and customers
- `POST /login` - Authenticate admin or customer based on selection
- `GET /customer/dashboard` - Customer job dashboard
- `GET /customer/job/<job_id>` - Individual job details
- `GET /customer/history` - Job history page
- `POST /customer/logout` - Customer logout

### Security Considerations
- Rate limiting on authentication attempts
- CAPTCHA for repeated failed logins
- Secure token generation for authentication
- Audit logging of customer access
- Input validation on all customer inputs

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. **Database Schema**: Extend customer and job tables
2. **Authentication System**: Implement customer login/logout
3. **Basic Dashboard**: Simple job status display
4. **Security Setup**: Authentication and rate limiting

### Phase 2: Core Features (Week 2)
1. **Job Details Page**: Complete job information display
2. **Mobile Responsive**: Ensure mobile-friendly design
3. **Status Updates**: Allow shop to add progress notes
4. **History Page**: Past jobs viewing

### Phase 3: Polish & Testing (Week 3)
1. **UI/UX Improvements**: Enhance design and usability
2. **Performance Optimization**: Caching and query optimization
3. **Testing**: Unit and integration tests
4. **Documentation**: Update user guides

## Dependencies

### Technical Dependencies
- Flask-Login or custom authentication
- Bootstrap for responsive design
- SQLAlchemy for database operations
- Existing customer and job models

### Business Dependencies
- Customer email addresses must be collected
- Job numbering system for easy reference
- Shop staff training on updating job progress

## Risk Assessment

### Technical Risks
- **Performance**: Complex queries could slow down customer portal
- **Security**: Customer authentication system could be vulnerable
- **Mobile Experience**: Responsive design might not work on all devices

### Business Risks
- **Adoption**: Customers may not use the portal if not promoted
- **Support**: Increased support requests during initial rollout
- **Data Quality**: Inaccurate job status information could frustrate customers

### Mitigation Strategies
- Performance testing before launch
- Security review and penetration testing
- User acceptance testing with real customers
- Staff training on portal usage and updates
- Clear communication about portal benefits

## Future Enhancements

### Phase 2 Features (Post-Launch)
- Photo uploads of work in progress
- Real-time notifications via email/SMS
- Online quote request system
- Digital proof approval workflow

### Advanced Features (Future)
- Customer account management
- Payment processing integration
- Appointment scheduling
- Feedback and rating system

## Testing Strategy

### Unit Tests
- Authentication functions
- Database query methods
- Template rendering
- Form validation

### Integration Tests
- Customer login/logout flow
- Job status retrieval
- Mobile responsiveness
- Error handling

### User Acceptance Testing
- Test with actual customers
- Mobile device testing
- Accessibility compliance
- Performance on slow connections

## Rollout Plan

### Pre-Launch
1. Complete development and testing
2. Train shop staff on portal usage
3. Prepare customer communication materials
4. Set up monitoring and analytics

### Launch
1. Soft launch with select customers
2. Monitor for issues and feedback
3. Full rollout with email notifications
4. Collect usage metrics and feedback

### Post-Launch
1. Weekly monitoring of usage and issues
2. Monthly feedback collection
3. Quarterly feature updates based on usage
4. Annual review and major updates

This specification provides a comprehensive roadmap for implementing the customer portal feature, balancing technical requirements with business needs and user experience considerations.
