# Customer Job Portal Feature Specification

## Spec Overview

**Spec ID**: 2025-09-29-customer-job-portal
**Created**: September 29, 2025
**Priority**: High
**Effort**: 4-6 weeks
**Owner**: Development Team

## Goals & Success Criteria

### Primary Goals
1. **Customer Self-Service**: Allow customers to submit jobs and track progress independently
2. **Improved Efficiency**: Reduce phone calls and manual job intake processes
3. **Data Integrity**: Maintain accurate job records with full edit history
4. **Security**: Ensure customers only see their own jobs and data

### Success Metrics
- **Usage Rate**: 60% of customers submit jobs through portal within 3 months
- **Satisfaction**: 90%+ customer satisfaction with portal experience
- **Efficiency**: 50% reduction in job intake phone calls
- **Data Quality**: 100% of job edits tracked with full audit trail

## User Stories

### As a Customer
- **US1**: I want to create an account so I can submit and track my jobs
- **US2**: I want to submit new jobs with all required details so the shop can process them
- **US3**: I want to view all my submitted jobs so I can track their progress
- **US4**: I want to edit my job details if I need to make changes
- **US5**: I want to see the history of changes made to my jobs for transparency
- **US6**: I want a mobile-friendly interface so I can use it on my phone

### As a Shop Operator
- **US7**: I want to review customer-submitted jobs before they enter our workflow
- **US8**: I want to see edit history to understand customer requirements changes
- **US9**: I want to approve or reject customer-submitted jobs
- **US10**: I want to communicate with customers through the portal

### As a System Administrator
- **US11**: I want to manage customer accounts and permissions
- **US12**: I want to monitor portal usage and security
- **US13**: I want to export customer and job data for reporting

## Functional Requirements

### 1. Customer Authentication & Account Management
- **Account Creation**: Simple registration with email verification
- **Login System**: Secure login with password reset functionality
- **Profile Management**: Customers can update their contact information
- **Account Security**: Password strength requirements and session management

### 2. Job Submission System
- **Intake Form**: Comprehensive form matching shop's job requirements
- **File Upload**: Support for photos, drawings, and specification documents
- **Form Validation**: Client-side and server-side validation
- **Draft Saving**: Ability to save incomplete jobs as drafts
- **Form Guidance**: Clear instructions and help text for each field

### 3. Job Viewing & Tracking
- **Job Dashboard**: Overview of all customer's jobs with status indicators
- **Job Details**: Complete job information with progress updates
- **Status Tracking**: Real-time status updates from shop
- **Search & Filter**: Find specific jobs by date, type, or status
- **Mobile Responsive**: Works seamlessly on all devices

### 4. Job Editing Capabilities
- **Edit Access**: Customers can modify their submitted jobs
- **Field Restrictions**: Some fields may be locked after shop approval
- **Validation**: Same validation rules apply to edits as initial submission
- **Edit Limits**: Reasonable limits on edit frequency to prevent abuse

### 5. Edit History & Audit Trail
- **Complete Tracking**: Every field change recorded with timestamp
- **User Attribution**: Track who made each change (customer vs shop)
- **Change Details**: What was changed from/to with reason if provided
- **History View**: Chronological view of all changes
- **Export Capability**: Download edit history for records

### 6. Admin & Shop Management
- **Job Review Queue**: Shop can review and approve customer submissions
- **Communication Tools**: Internal notes and customer messaging
- **Status Management**: Update job status with customer notifications
- **Reporting**: Usage statistics and customer activity reports

## Technical Specifications

### Architecture
- **Frontend**: HTML templates with JavaScript for dynamic features
- **Backend**: Flask routes with Blueprint organization
- **Database**: Extended customer, job, and audit tables
- **Authentication**: Flask-Login with customer-specific roles
- **File Handling**: Secure file upload with validation

### Database Schema Changes
```sql
-- Customer accounts table
CREATE TABLE customer_accounts (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    company_name VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Customer sessions table
CREATE TABLE customer_sessions (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customer_accounts(id),
    session_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Job edit history table
CREATE TABLE job_edit_history (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    customer_id INTEGER REFERENCES customer_accounts(id),
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_reason TEXT,
    changed_by_customer BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add customer reference to jobs
ALTER TABLE jobs ADD COLUMN customer_account_id INTEGER REFERENCES customer_accounts(id);
ALTER TABLE jobs ADD COLUMN submitted_by_customer BOOLEAN DEFAULT FALSE;
ALTER TABLE jobs ADD COLUMN requires_approval BOOLEAN DEFAULT TRUE;
```

### Security Requirements
- **Authentication**: Secure password hashing with bcrypt
- **Authorization**: Customer can only access their own jobs
- **Session Security**: Secure session management with timeouts
- **Input Validation**: Comprehensive validation on all user inputs
- **File Security**: Virus scanning and type validation for uploads
- **Rate Limiting**: Prevent brute force attacks and spam submissions

### API Endpoints
```
# Authentication
POST /customer/register
POST /customer/login
POST /customer/logout
POST /customer/forgot-password
POST /customer/reset-password

# Job Management
GET  /customer/dashboard
POST /customer/jobs/submit
GET  /customer/jobs
GET  /customer/jobs/{id}
PUT  /customer/jobs/{id}
GET  /customer/jobs/{id}/history

# Profile Management
GET  /customer/profile
PUT  /customer/profile

# Admin (Shop) Endpoints
GET  /admin/customer-jobs/pending
POST /admin/customer-jobs/{id}/approve
POST /admin/customer-jobs/{id}/reject
GET  /admin/customers
```

## Implementation Plan

### Phase 1: Foundation (Week 1-2)
1. **Database Schema**: Implement new tables and relationships
2. **Customer Authentication**: Registration, login, password reset
3. **Basic Dashboard**: Simple job listing and status view
4. **Security Setup**: Authentication middleware and validation

### Phase 2: Core Features (Week 3-4)
1. **Job Submission**: Complete intake form with file uploads
2. **Job Viewing**: Detailed job view with status tracking
3. **Job Editing**: Customer edit capabilities with validation
4. **Edit History**: Complete audit trail implementation

### Phase 3: Enhancement & Polish (Week 5-6)
1. **Mobile Responsiveness**: Optimize for mobile devices
2. **Admin Interface**: Shop review and approval system
3. **Notification System**: Email updates for status changes
4. **Performance Optimization**: Caching and query optimization

## Dependencies

### Technical Dependencies
- Flask-Login for authentication
- Flask-WTF for form handling
- Bcrypt for password hashing
- SQLAlchemy for database operations
- Existing job and customer models

### Business Dependencies
- Customer email verification process
- Shop approval workflow for submitted jobs
- File storage and backup systems
- Email service for notifications

## Risk Assessment

### Technical Risks
- **Database Performance**: Complex queries with audit trails could impact performance
- **File Upload Security**: Ensuring uploaded files are safe and virus-free
- **Authentication Security**: Protecting customer accounts and sessions

### Business Risks
- **Customer Adoption**: Customers may prefer phone submission over digital forms
- **Data Quality**: Customer-submitted data may have quality issues
- **Support Overhead**: Additional support requests for portal usage

### Mitigation Strategies
- Performance testing and optimization before launch
- Comprehensive security review and penetration testing
- User training and clear documentation
- Phased rollout with feedback collection
- Quality checks on submitted jobs before processing

## Testing Strategy

### Unit Tests
- Authentication functions (register, login, password reset)
- Form validation and submission
- Database query methods
- Edit history tracking

### Integration Tests
- Complete job submission workflow
- Customer authentication flow
- Edit history generation
- Admin approval process

### User Acceptance Testing
- Test with actual customers for usability
- Mobile device compatibility testing
- Accessibility compliance verification
- Performance testing with large datasets

## Rollout Plan

### Pre-Launch
1. Complete development and testing
2. Train shop staff on new workflow
3. Prepare customer communication materials
4. Set up monitoring and analytics

### Launch
1. Soft launch with select customers
2. Monitor for issues and gather feedback
3. Full rollout with promotional materials
4. Collect usage metrics and customer feedback

### Post-Launch
1. Weekly monitoring of usage and issues
2. Monthly feedback collection and improvements
3. Quarterly feature updates based on usage patterns
4. Annual review and major enhancements

This specification provides a comprehensive roadmap for implementing the customer job portal, balancing technical requirements with business needs and user experience considerations.
