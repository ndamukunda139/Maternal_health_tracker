# Maternal Health Tracker API

A comprehensive RESTful API for managing maternal health records, pregnancies, deliveries, and clinical visits. Designed to improve healthcare outcomes by providing healthcare providers with centralized access to patient maternal health data and basic analytics feature of recorded data.

## Problem Statement

Maternal health management requires coordination across multiple healthcare providers and visits. Existing systems often suffer from:

- **Fragmented Records**: Patient data scattered across different clinics and papers
- **Poor Accessibility**: Difficult to access complete maternal history when needed
- **Data Integrity Issues**: Inconsistent or missing medical records
- **Limited Analytics**: No real-time insights into maternal health trends
- **Compliance Challenges**: Difficulty maintaining patient privacy while sharing data

## Solution

The **Maternal Health Tracker API** provides a centralized, secure platform for:

✅ **Complete Patient Records** - Unified maternal health history accessible to authorized providers  
✅ **Pregnancy Management** - Track pregnancies from conception through delivery with risk factor monitoring  
✅ **Delivery Records** - Comprehensive delivery documentation with newborn outcomes  
✅ **Clinical Visits** - Document prenatal, postnatal, and general medical mothers' visits  
✅ **Analytics & Insights** - Generate summary reports on maternal and infant outcomes  
✅ **Role-Based Access** - Strict authorization ensuring patients only see their own data  
✅ **HIPAA-Ready** - Built with healthcare privacy and security standards in mind  

---

## Tech Stack

- **Framework**: Django 6.0 with Django REST Framework
- **Database**: SQLite (development)
- **Authentication**: Token-based & Session-based auth
- **Routing**: REST Nested Routers for hierarchical data
- **API Format**: RESTful JSON

---

## Installation

### Prerequisites
- Python 3.13
- pip/virtualenv

### Setup

1. **Clone and Navigate**
```bash
cd maternal_health
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Migrations**
```bash
python manage.py migrate
```

5. **Create Superuser** (for admin access)
```bash
python manage.py createsuperuser
```

6. **Start Development Server**
```bash
python manage.py runserver
```

The API will be available at `https://danielndamukunda.pythonanywhere.com/api/`

---

## Authentication

### Register New User
```
POST /register/
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword",
  "email": "user@example.com",
  "role": "patient"  # Can be: patient, doctor, nurse, admin
}
```
Each role as specific additional required fields.

### Login
```
POST /login/
Content-Type: application/json

{
  "username": "user",
  "password": "password"
}
```

### Logout
```
POST /logout/
```

**All subsequent requests must include authentication credentials**.

---
### Admin dashbord
```
GET /admin-dashboard/ : Only Admins can retrive all registered users
```

## API Endpoints

### 1. Patients

#### Get All Patients (clinicians/admins only)
```
GET /api/patients/
```

#### Get Specific Patient
```
GET /api/patients/{patient_id}/
```

#### Update Patient Profile
```
PATCH /api/patients/{patient_id}/
Content-Type: application/json

{
  "first_name": "Jane",
  "address": "123 Main St",
  "phone_number": "555-1234",
  ...
}
```

#### Get Patient Profile
```
GET /profile/
```

---

### 2. Pregnancies

#### Get All Pregnancies (for logged-in user or specific patient)
```
GET /api/pregnancies/                              # All pregnancies (if clinician)
GET /api/patients/{patient_id}/pregnancies/        # Patient's pregnancies
```

#### Create Pregnancy (clinicians/admins only)
```
POST /api/patients/{patient_id}/pregnancies/
Content-Type: application/json

{
  "gestational_age_weeks": 12,
  "last_menstrual_period": "2024-01-20",
  "expected_delivery_date": "2024-10-27",
  "blood_type": "O+",
  "hiv_status": false,
  "diabetes_status": false,
  "hypertension_status": false
}
```

#### Get Specific Pregnancy
```
GET /api/patients/{patient_id}/pregnancies/{pregnancy_id}/
```

#### Update Pregnancy
```
PATCH /api/patients/{patient_id}/pregnancies/{pregnancy_id}/
Content-Type: application/json
```

#### Delete Pregnancy
```
DELETE /api/patients/{patient_id}/pregnancies/{pregnancy_id}/
```

---

### 3. Deliveries

#### Get All Deliveries
```
GET /api/deliveries/                                  # All (clinicians only)
GET /api/patients/{patient_id}/deliveries/           # Patient's deliveries
```

#### Create Delivery (clinicians/admins only)
```
POST /api/patients/{patient_id}/deliveries/
Content-Type: application/json

{
  "pregnancy_id": 1,
  "delivery_date": "2024-10-27",
  "delivery_mode": "vaginal",  # Options: vaginal, cesarean, assisted
  "birth_weight_g": 3500,
  "place_of_delivery": "Hospital ABC",
  "skilled_birth_attendant": true,
  "newborn_gender": "Female",
  "apgar_score_1min": 8,
  "apgar_score_5min": 9,
  "alive": true,
  "congenital_anomalies": null,
  "neonatal_complications": null,
  "complications": null,
  "interventions": null
}
```

#### Get Specific Delivery
```
GET /api/patients/{patient_id}/deliveries/{delivery_id}/
```

#### Update Delivery
```
PATCH /api/patients/{patient_id}/deliveries/{delivery_id}/
Content-Type: application/json
```

---

### 4. Visits

#### Get All Visits
```
GET /api/visits/                                                  # All (clinicians only)
GET /api/patients/{patient_id}/visits/                           # Patient's visits
GET /api/patients/{patient_id}/pregnancies/{pregnancy_id}/visits/ # Pregnancy visits (Antinatal Visits)
GET /api/patients/{patient_id}/deliveries/{delivery_id}/visits/   # Delivery visits (Prenatal Visits)
```

#### Create Visit
```
POST /api/patients/{patient_id}/pregnancies/{pregnancy_id}/visits/ (Antinatal Visit)
Content-Type: application/json

{
  "visit_date": "2024-09-15",
  "visit_type": "prenatal",  # Options: prenatal, postnatal, general
  "weight_kg": 65.5,
  "hemoglobin_level": 12.0,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  ......
  ......
  ......
  "notes": "Routine checkup",
  "pregnancy_id": 1,
  "delivery_id": null
}
```

POST /api/patients/{patient_id}/deliveries/{delivery_id}/visits/ (Postnatal Visit)
Content-Type: application/json

{
  "visit_date": "2024-09-15",
  "visit_type": "prenatal",  # Options: prenatal, postnatal, general
  "weight_kg": 65.5,
  "hemoglobin_level": 12.0,
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "breastfeeding_status": true,
  "postpartum_complications": "None",
  "newborn_health_issues": "None",
  ......
  ......
  "notes": "Routine checkup",
  "pregnancy_id": 1,
  "delivery_id": null
}
```

#### Get Specific Visit to specific Patient
```
GET /api/patients/{patient_id}/visits/{visit_id}/
```

#### Update Visit to specific Patient
```
PATCH /api/patients/{patient_id}/visits/{visit_id}/
Content-Type: application/json
```
#### Get, Update or Delete Specific visit to specific delivery

```
GET PATCH DELETE /api/patients/{patient_id}/deliveries/{delivery_id}/visits/{visit_id}/
```

#### Get, Update or Delete Specific visit to specific pregnancy

```
GET PATCH DELETE /api/patients/{patient_id}/pregnancies/{delivery_id}/visits/{visit_id}/

```

---

## Analytics Endpoints

### 1. Pregnancy Analytics

#### Get Pregnancy Summary (JSON)
```
GET /api/patients/{patient_id}/analytics/pregnancies/summary/
```

**Response:**
```json
{
  "total_pregnancies": 3,
  "by_blood_type": {
    "O+": 2,
    "A-": 1
  },
  "average_gestational_age_weeks": 24.5,
  "monthly_expected_deliveries": [
    {"month": "2024-10", "count": 2},
    {"month": "2024-11", "count": 1}
  ]
}
```

#### Export Pregnancies to CSV
```
GET /api/patients/{patient_id}/analytics/pregnancies/export/
```

**Note**: Global analytics (`/api/analytics/pregnancies/summary/`) restricted to clinicians/admins only. Patients must request their own data with patient_id.

---

### 2. Delivery Analytics

#### Get Delivery Summary (JSON)
```
GET /api/patients/{patient_id}/analytics/deliveries/summary/
```

**Response:**
```json
{
  "total_deliveries": 2,
  "by_mode": {
    "vaginal": 1,
    "cesarean": 1
  },
  "average_birth_weight_g": 3400,
  "alive_counts": {
    "true": 2
  },
  "monthly_deliveries": [
    {"month": "2024-06", "count": 1},
    {"month": "2024-10", "count": 1}
  ]
}
```

#### Export Deliveries to CSV
```
GET /api/patients/{patient_id}/analytics/deliveries/export/
```

---

### 3. Visit Analytics

#### Get Visit Summary (JSON)
```
GET /api/patients/{patient_id}/analytics/visits/summary/
```

**Response:**
```json
{
  "total_visits": 8,
  "by_type": {
    "prenatal": 5,
    "postnatal": 2,
    "general": 1
  },
  "average_weight_kg": 65.2,
  "average_hemoglobin_level": 11.8,
  "monthly_visits": [
    {"month": "2024-06", "count": 2},
    {"month": "2024-07", "count": 3}
  ]
}
```

#### Export Visits to CSV
```
GET /api/patients/{patient_id}/analytics/visits/export/
```

---

## Authorization & Access Control

### Role-Based Access

| Endpoint | Patient | Doctor | Nurse | Admin |
|----------|---------|--------|-------|-------|
| View own data | ✅ | ✅ | ✅ | ✅ |
| View any patient data | ❌ | ✅ | ✅ | ✅ |
| Create records | ❌ | ✅ | ✅ | ✅ |
| Edit records | ❌ | ✅ | ✅ | ✅ |
| Delete records | ❌ | ✅ | ✅ | ✅ |
| Access global analytics | ❌ | ✅ | ✅ | ✅ |

### Key Rules

- **Patients** can only access their own data via endpoints with their after login
- **Patients cannot** access global analytics endpoints (e.g., `/api/analytics/pregnancies/summary/`), patient access only her own data summary after login.
- **Clinicians** (doctors, nurses, admins) can access any patient's data using the patient_id
- **Authentication required** for all endpoints

### Example - Patient Access
```bash
# Patient can view their own pregnancies data
GET /api/patients/5/pregnancies/        # ✅ If patient_id=5

# Patient cannot view other patients
GET /api/patients/3/pregnancies/        # ❌ 403 Forbidden (if logged in as patient 5)

# Patient cannot access overall summary of global analytics, on sees her own summary
GET /api/analytics/pregnancies/summary/ # Only her own summary. But Other roles will access overall systems summary.
```

---

## Error Handling

### Common HTTP Responses

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | OK - Request successful | User fetches their data |
| 201 | Created - Resource created | New pregnancy record added |
| 204 | No Content - Success, no body | Successful DELETE |
| 400 | Bad Request - Invalid input | Missing required field |
| 401 | Unauthorized - Not authenticated | Not logged in |
| 403 | Forbidden - Access denied | Patient viewing other patient's data |
| 404 | Not Found - Resource doesn't exist | Invalid patient_id |
| 500 | Server Error | Unexpected error on server |

### Error Response Format
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Example Workflows

### Workflow 1: Patient Views Own Pregnancy Data
```bash
# 1. Login
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jane_doe", "password": "password123"}'

# 2. Get own pregnancies (assuming patient_id=10)
curl -X GET http://localhost:8000/api/pregnancies/ \
  -H "Cookie: sessionid=..."

# 3. View pregnancy summary
curl -X GET http://localhost:8000/api/analytics/pregnancies/summary/ \
  -H "Cookie: sessionid=..."
```

### Workflow 2: Doctor Creates Delivery Record
```bash
# 1. Login as doctor
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "dr_smith", "password": "password123"}'

# 2. Create delivery for patient 10
curl -X POST http://localhost:8000/api/patients/10/deliveries/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{
    "pregnancy_id": 5,
    "delivery_date": "2024-10-27",
    "delivery_mode": "vaginal",
    "birth_weight_g": 3450,
    "place_of_delivery": "Hospital XYZ",
    "skilled_birth_attendant": true,
    "newborn_gender": "Female",
    "apgar_score_1min": 8,
    "apgar_score_5min": 9,
    "alive": true
  }'

# 3. View global delivery analytics
curl -X GET http://localhost:8000/api/analytics/deliveries/summary/ \
  -H "Cookie: sessionid=..."
```

---

## Database Schema

### Core Models

**Patient**
- user (OneToOne to User)
- first_name, last_name
- medical_record_number (unique)
- date_of_birth
- national_id (unique)
- phone_number, address
- marital_status, educational_level, occupation
- gravidity, parity (pregnancy history)

**Pregnancy**
- patient (ForeignKey)
- gestational_age_weeks
- last_menstrual_period, expected_delivery_date
- blood_type
- Risk flags: hiv_status, diabetes_status, hypertension_status, multiple_pregnancy
- created_by, updated_by (audit trail)

**Delivery**
- pregnancy (ForeignKey), patient (ForeignKey)
- delivery_date, delivery_mode
- birth_weight_g, place_of_delivery
- skilled_birth_attendant
- Newborn health: newborn_gender, apgar_score_1min, apgar_score_5min, alive
- complications, interventions
- created_by, updated_by

**Visit**
- patient (ForeignKey), pregnancy (ForeignKey), delivery (ForeignKey)
- visit_date, visit_type (prenatal/postnatal/general)
- Vitals: weight_kg, hemoglobin_level, blood_pressure_systolic, blood_pressure_diastolic
- notes, created_by, updated_by

---

### Database Migrations
```bash
python manage.py makemigrations        # Create migration files
python manage.py migrate               # Apply migrations
python manage.py migrate --fake-initial # When incorporating existing data
```

### Shell Access
```bash
python manage.py shell
```

---

## Deployment Considerations

### Before Production
- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure allowed hosts
- [ ] Use environment variables for secrets
- [ ] Set up HTTPS/SSL
- [ ] Configure database (PostgreSQL recommended)
- [ ] Set up logging and monitoring
- [ ] Implement rate limiting
- [ ] Back up database regularly

### Security Best Practices
- Enforce strong passwords
- Keep dependencies updated
- Use HTTPS only
- Implement audit logging
- Restrict database access
- Regular security audits

---

## Contributing

Contributions are welcome! Please:
1. Create a feature branch (`git checkout -b feature/new-feature`)
2. Write tests for new functionality
3. Follow PEP 8 style guidelines
4. Commit with clear messages
5. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

## Support & Documentation

For issues, feature requests, or documentation visit:
- **GitHub Issues**: [(https://github.com/ndamukunda139/Maternal_health_tracker)]
- **API Documentation**: `/api/docs/` (when available)
- **Contact**: ndamukunda139@gmail.com
---

## Version History

**v1.0.0** (Feb 2026)
- Initial API release
- Pregnancies, Deliveries, Visits management
- Patient-specific analytics
- Role-based access control

