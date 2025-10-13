# Print Parity Checklist

Target templates: Job Worksheet, Intake Forms (production/railing)

| Spec | Legacy | New Target | Status |
| --- | --- | --- | --- |
| Page size | Letter (8.5x11) | Letter | ⚠️ |
| Margins | 0.5in all sides | 0.5in | ⚠️ |
| Font scale | 100% | 100% | ⚠️ |
| Checkbox size | 12px | 12px | ⚠️ |
| Section order | Matches legacy | Matches | ⚠️ |
| Page breaks | Controlled per section | Same | ⚠️ |
| QR/Barcode | Top-right, 32mm | Same position/size | ❌ |

Key selectors to assert:
- .print-page
- .worksheet-header
- .worksheet-section
- .qr-code
- .page-break

