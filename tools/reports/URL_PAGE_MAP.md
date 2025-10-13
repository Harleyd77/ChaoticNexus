# Routing Compatibility Matrix (Legacy → Canonical)

Legend: Prefer 308 for same-method redirects. “Keep” indicates legacy URL must remain functional during parity.

| Legacy Path | Method | Params | Canonical Target | Expected Status/Redirect | Keep |
| --- | --- | --- | --- | --- | --- |
| / | GET | - | /dashboard/ | 302 → /dashboard/ | Y |
| /nav | GET | - | /dashboard/ | 308 → /dashboard/ | Y |
| /favicon.ico | GET | - | /favicon.ico | 200 | Y |
| /uploads/<path:name> | GET | name | /uploads/<path:name> | 200/404 | Y |

Auth
| /login | GET, POST | - | /login | 200 | Y |
| /logout | GET | - | /logout | 302 → / | Y |
| /logout/customer | POST | - | /logout/customer | 302 → / | Y |

Customer Portal
| /customer/dashboard | GET | - | /customer/ | 200 | Y |
| /customer/jobs | GET | - | /customer/jobs | 200 | Y |
| /customer/jobs/<int:job_id> | GET | job_id | /customer/jobs/<int:job_id> | 200/404 | Y |
| /customer/jobs/<int:job_id>/edit | GET, POST | job_id | /customer/jobs/<int:job_id>/edit | 200/302 | Y |
| /customer/jobs/submit | GET, POST | - | /customer/jobs/submit | 200/302 | Y |
| /customer/register | GET, POST | - | /customer/register | 200/302 | Y |
| /customer/forgot-password | GET, POST | - | /customer/forgot-password | 200/302 | Y |
| /customer/logout | GET | - | /customer/logout | 302 → / | Y |

Customers
| /customers | GET | - | /customers | 200 | Y |
| /customers/<int:cust_id> | GET | cust_id | /customers/<int:cust_id> | 200/404 | Y |
| /customers/search.json | GET | q | /customers/search.json | 200 | Y |
| /customers/save | POST | form fields | /customers/save | 302 | Y |
| /customers/<int:cust_id>/delete | POST | cust_id | /customers/<int:cust_id>/delete | 302 | Y |
| /customers/<int:cust_id>/contacts.json | GET | cust_id | /customers/<int:cust_id>/contacts.json | 200 | Y |
| /customers/<int:cust_id>/contacts/add | POST | cust_id | /customers/<int:cust_id>/contacts/add | 302 | Y |
| /customers/<int:cust_id>/contacts/<int:ct_id>/save | POST | cust_id, ct_id | /customers/<int:cust_id>/contacts/<int:ct_id>/save | 302 | Y |
| /customers/<int:cust_id>/contacts/<int:ct_id>/delete | POST | cust_id, ct_id | /customers/<int:cust_id>/contacts/<int:ct_id>/delete | 302 | Y |
| /api/customers | GET | filters | /api/customers | 200 | Y |
| /api/customers/<int:customer_id>/dashboard | GET | customer_id | /api/customers/<int:customer_id>/dashboard | 200 | Y |
| /api/customers/<int:customer_id> | PATCH | customer_id | /api/customers/<int:customer_id> | 200 | Y |

Admin Customer Accounts
| /admin/customer-accounts | GET | - | /admin/customer-accounts | 200 | Y |
| /api/admin/customer-accounts | GET | - | /api/admin/customer-accounts | 200 | Y |
| /admin/customer-accounts/<int:account_id> | GET | account_id | /admin/customer-accounts/<int:account_id> | 200/404 | Y |
| /api/admin/customer-accounts/<int:account_id> | PATCH | account_id | /api/admin/customer-accounts/<int:account_id> | 200 | Y |
| /api/admin/customer-accounts/<int:account_id>/password | POST | account_id | /api/admin/customer-accounts/<int:account_id>/password | 200/302 | Y |
| /api/admin/customer-accounts/<int:account_id>/toggle-active | POST | account_id | /api/admin/customer-accounts/<int:account_id>/toggle-active | 200/302 | Y |
| /api/admin/customer-accounts/<int:account_id> | DELETE | account_id | /api/admin/customer-accounts/<int:account_id> | 200 | Y |

Jobs
| /jobs | GET | - | /jobs | 200 | Y |
| /jobs/kanban | GET | - | /jobs/kanban | 200 | Y |
| /jobs/<int:job_id> | GET | job_id | /jobs/<int:job_id> | 200/404 | Y |
| /jobs/<int:job_id>/edit | GET, POST | job_id | /jobs/<int:job_id>/edit | 200/302 | Y |
| /jobs/<int:job_id>/photos.json | GET | job_id | /jobs/<int:job_id>/photos.json | 200 | Y |
| /jobs/<int:job_id>/photos/upload | POST | job_id | /jobs/<int:job_id>/photos/upload | 302/200 | Y |
| /jobs/<int:job_id>/photos/<int:photo_id>/delete | POST | job_id, photo_id | /jobs/<int:job_id>/photos/<int:photo_id>/delete | 302 | Y |
| /jobs/reorder | POST | payload | /jobs/reorder | 200 | Y |
| /jobs/screen | GET | - | /jobs/screen | 200 | Y |
| /jobs/<int:job_id>/screen/add | POST | job_id | /jobs/<int:job_id>/screen/add | 302 | Y |
| /jobs/<int:job_id>/screen/remove | POST | job_id | /jobs/<int:job_id>/screen/remove | 302 | Y |
| /jobs/screen/reorder | POST | payload | /jobs/screen/reorder | 200 | Y |
| /jobs.csv | GET | filters | /jobs.csv | 200 | Y |
| /jobs/completed | GET | - | /jobs/completed | 200 | Y |
| /jobs/<int:job_id>/worksheet | GET | job_id | /jobs/<int:job_id>/worksheet | 200 | Y |
| /jobs/<int:job_id>/worksheet/save | POST | job_id | /jobs/<int:job_id>/worksheet/save | 302 | Y |
| /jobs/<int:job_id>/archive | POST | job_id | /jobs/<int:job_id>/archive | 302 | Y |
| /jobs/<int:job_id>/unarchive | POST | job_id | /jobs/<int:job_id>/unarchive | 302 | Y |
| /jobs/<int:job_id>/complete | POST | job_id | /jobs/<int:job_id>/complete | 302 | Y |
| /jobs/<int:job_id>/reopen | POST | job_id | /jobs/<int:job_id>/reopen | 302 | Y |
| /jobs/<int:job_id>/delete | POST | job_id | /jobs/<int:job_id>/delete | 302 | Y |

Powders
| /powders | GET | - | /powders | 200 | Y |
| /powders/<int:pow_id>/edit | GET | pow_id | /powders/<int:pow_id>/edit | 200/404 | Y |
| /powders/new | GET | - | /powders/new | 200 | Y |
| /powders/save | POST | form | /powders/save | 302 | Y |
| /powders/<int:pow_id>/delete | POST | pow_id | /powders/<int:pow_id>/delete | 302 | Y |
| /powders.csv | GET | filters | /powders.csv | 200 | Y |
| /powders/import | POST | file | /powders/import | 302/200 | Y |
| /powders/families.json | GET | - | /powders/families.json | 200 | Y |
| /powders/colors_full.json | GET | - | /powders/colors_full.json | 200 | Y |
| /powders/by_color.json | GET | color | /powders/by_color.json | 200 | Y |

Inventory
| /inventory | GET | - | /inventory | 200 | Y |
| /inventory/reorder | GET | - | /inventory/reorder | 200 | Y |
| /inventory/<int:powder_id>/update | POST | powder_id | /inventory/<int:powder_id>/update | 302/200 | Y |
| /inventory/<int:powder_id>/adjust | POST | powder_id | /inventory/<int:powder_id>/adjust | 302/200 | Y |
| /inventory/history/<int:powder_id> | GET | powder_id | /inventory/history/<int:powder_id> | 200 | Y |
| /inventory/api/powders | GET | filters | /inventory/api/powders | 200 | Y |
| /inventory/api/update | POST | payload | /inventory/api/update | 200 | Y |
| /inventory/api/reorder | GET | - | /inventory/api/reorder | 200 | Y |

Intake
| /intake_form | GET | - | /intake/form | 200 | Y |
| /railing_intake | GET | - | /intake/railing | 200 | Y |
| /submit | POST | form | /intake/submit | 302/200 | Y |

Admin & Config
| /admin | GET | - | /admin | 200 | Y |
| /admin/dbinfo | GET | - | /admin/dbinfo | 200 | Y |
| /admin/logos/list | GET | - | /admin/logos/list | 200 | Y |
| /admin/branding/select_logo | POST | file | /admin/branding/select_logo | 302/200 | Y |
| /admin/branding/favicon | POST | file | /admin/branding/favicon | 302/200 | Y |
| /admin/branding/favicon/clear | POST | - | /admin/branding/favicon/clear | 302 | Y |
| /admin/branding/page_logo | POST | file | /admin/branding/page_logo | 302/200 | Y |
| /admin/branding/page_logo/clear | POST | - | /admin/branding/page_logo/clear | 302 | Y |
| /admin/branding/login_bg | POST | file | /admin/branding/login_bg | 302/200 | Y |
| /admin/branding/login_bg/clear | POST | - | /admin/branding/login_bg/clear | 302 | Y |
| /admin/branding/login_title | POST | text | /admin/branding/login_title | 302/200 | Y |
| /config/intake.json | GET | - | /config/intake.json | 200 | Y |
| /config/intake | POST | json | /config/intake | 200 | Y |
| /config/railing.json | GET | - | /config/railing.json | 200 | Y |
| /config/railing | POST | json | /config/railing | 200 | Y |
| /admin/print-templates | GET | - | /admin/print-templates | 200 | Y |
| /admin/users | GET | - | /admin/users | 200 | Y |
| /admin/users/add | POST | form | /admin/users/add | 302 | Y |
| /admin/users/<int:user_id>/delete | POST | user_id | /admin/users/<int:user_id>/delete | 302 | Y |
| /admin/users/<int:user_id>/toggle_admin | POST | user_id | /admin/users/<int:user_id>/toggle_admin | 302 | Y |
| /admin/users/<int:user_id>/set_password | POST | user_id | /admin/users/<int:user_id>/set_password | 302 | Y |
| /admin/users/<int:user_id>/perms | POST | user_id | /admin/users/<int:user_id>/perms | 302 | Y |
| /admin/ui | POST | json | /admin/ui | 200 | Y |

Print Templates
| /api/print-templates/<template_type> | GET | template_type | /api/print-templates/<template_type> | 200 | Y |
| /api/print-templates/<template_type>/all | GET | template_type | /api/print-templates/<template_type>/all | 200 | Y |
| /api/print-templates | POST | json | /api/print-templates | 201/200 | Y |
| /api/print-templates/<int:template_id> | DELETE | template_id | /api/print-templates/<int:template_id> | 200/204 | Y |
| /api/print-templates/<int:template_id>/set-default | POST | template_id | /api/print-templates/<int:template_id>/set-default | 200 | Y |

Legacy Dev/React/Migrate (not required to keep)
| /react/* | GET | - | n/a | 410/404 | N |
| /dev/* | GET | - | n/a | 410/404 | N |
| /admin/migrate/add-charge-columns | GET | - | n/a | 410/404 (migrated to Alembic) | N |


