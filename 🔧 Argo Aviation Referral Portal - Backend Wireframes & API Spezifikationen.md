# 🔧 Argo Aviation Referral Portal - Backend Wireframes & API Spezifikationen

## 🎯 Übersicht

Diese Dokumentation definiert die komplette Backend-Architektur für das Argo Aviation Referral Portal MVP. Sie umfasst API-Endpunkte, Datenbank-Schema, Geschäftslogik und Integrations-Spezifikationen.

---

## 🗄️ **1. Erweiterte Datenbank-Schema Spezifikation**

### **Bestehende Modelle (bereits implementiert):**

#### **Users Tabelle:**
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    email NVARCHAR(120) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    first_name NVARCHAR(80) NOT NULL,
    last_name NVARCHAR(80) NOT NULL,
    phone_number NVARCHAR(20),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    last_login DATETIME2,
    profile_image_url NVARCHAR(255),
    linkedin_url NVARCHAR(255),
    twitter_url NVARCHAR(255),
    website_url NVARCHAR(255)
);
```

#### **JobListings Tabelle:**
```sql
CREATE TABLE job_listings (
    job_id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(200) NOT NULL,
    company NVARCHAR(100) NOT NULL,
    location NVARCHAR(100) NOT NULL,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    employment_type NVARCHAR(50) DEFAULT 'Vollzeit',
    referral_bonus DECIMAL(10,2) NOT NULL,
    description NTEXT NOT NULL,
    requirements NTEXT,
    benefits NTEXT,
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETDATE(),
    application_deadline DATETIME2,
    created_by INT FOREIGN KEY REFERENCES users(user_id)
);
```

#### **Referrals Tabelle:**
```sql
CREATE TABLE referrals (
    referral_id INT PRIMARY KEY IDENTITY(1,1),
    referrer_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    job_id INT NOT NULL FOREIGN KEY REFERENCES job_listings(job_id),
    candidate_first_name NVARCHAR(80) NOT NULL,
    candidate_last_name NVARCHAR(80) NOT NULL,
    candidate_email NVARCHAR(120) NOT NULL,
    candidate_phone NVARCHAR(20),
    candidate_linkedin NVARCHAR(255),
    resume_file_path NVARCHAR(255),
    recommendation_text NTEXT,
    relationship_type NVARCHAR(50),
    status NVARCHAR(50) DEFAULT 'submitted',
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE(),
    hr_notes NTEXT,
    interview_date DATETIME2,
    hired_date DATETIME2,
    bonus_paid BIT DEFAULT 0,
    bonus_paid_date DATETIME2
);
```

### **Neue Tabellen für erweiterte Funktionalität:**

#### **UserSpecializations Tabelle:**
```sql
CREATE TABLE user_specializations (
    specialization_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    specialization_name NVARCHAR(100) NOT NULL,
    experience_level NVARCHAR(50), -- 'Beginner', 'Intermediate', 'Expert'
    created_at DATETIME2 DEFAULT GETDATE()
);
```

#### **ReferralStatusHistory Tabelle:**
```sql
CREATE TABLE referral_status_history (
    history_id INT PRIMARY KEY IDENTITY(1,1),
    referral_id INT NOT NULL FOREIGN KEY REFERENCES referrals(referral_id),
    old_status NVARCHAR(50),
    new_status NVARCHAR(50) NOT NULL,
    changed_by INT FOREIGN KEY REFERENCES users(user_id),
    change_reason NTEXT,
    created_at DATETIME2 DEFAULT GETDATE()
);
```

#### **Payments Tabelle:**
```sql
CREATE TABLE payments (
    payment_id INT PRIMARY KEY IDENTITY(1,1),
    referral_id INT NOT NULL FOREIGN KEY REFERENCES referrals(referral_id),
    referrer_id INT NOT NULL FOREIGN KEY REFERENCES users(user_id),
    amount DECIMAL(10,2) NOT NULL,
    payment_method NVARCHAR(50), -- 'bank_transfer', 'paypal', 'check'
    payment_status NVARCHAR(50) DEFAULT 'pending', -- 'pending', 'processed', 'failed'
    payment_date DATETIME2,
    transaction_id NVARCHAR(100),
    bank_details NTEXT, -- Encrypted bank information
    created_at DATETIME2 DEFAULT GETDATE(),
    processed_by INT FOREIGN KEY REFERENCES users(user_id)
);
```

#### **SystemSettings Tabelle:**
```sql
CREATE TABLE system_settings (
    setting_id INT PRIMARY KEY IDENTITY(1,1),
    setting_key NVARCHAR(100) UNIQUE NOT NULL,
    setting_value NTEXT NOT NULL,
    setting_type NVARCHAR(50) DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
    description NTEXT,
    updated_by INT FOREIGN KEY REFERENCES users(user_id),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

#### **AuditLog Tabelle:**
```sql
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT FOREIGN KEY REFERENCES users(user_id),
    action NVARCHAR(100) NOT NULL,
    table_name NVARCHAR(50),
    record_id INT,
    old_values NTEXT, -- JSON
    new_values NTEXT, -- JSON
    ip_address NVARCHAR(45),
    user_agent NTEXT,
    created_at DATETIME2 DEFAULT GETDATE()
);
```

#### **EmailTemplates Tabelle:**
```sql
CREATE TABLE email_templates (
    template_id INT PRIMARY KEY IDENTITY(1,1),
    template_name NVARCHAR(100) UNIQUE NOT NULL,
    subject NVARCHAR(255) NOT NULL,
    body_html NTEXT NOT NULL,
    body_text NTEXT,
    variables NTEXT, -- JSON array of available variables
    is_active BIT DEFAULT 1,
    created_by INT FOREIGN KEY REFERENCES users(user_id),
    created_at DATETIME2 DEFAULT GETDATE(),
    updated_at DATETIME2 DEFAULT GETDATE()
);
```

#### **NotificationQueue Tabelle:**
```sql
CREATE TABLE notification_queue (
    notification_id INT PRIMARY KEY IDENTITY(1,1),
    recipient_email NVARCHAR(120) NOT NULL,
    subject NVARCHAR(255) NOT NULL,
    body_html NTEXT NOT NULL,
    body_text NTEXT,
    notification_type NVARCHAR(50), -- 'referral_update', 'payment_notification', 'system_alert'
    status NVARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    attempts INT DEFAULT 0,
    max_attempts INT DEFAULT 3,
    scheduled_for DATETIME2 DEFAULT GETDATE(),
    sent_at DATETIME2,
    error_message NTEXT,
    created_at DATETIME2 DEFAULT GETDATE()
);
```

---

## 🔌 **2. API-Endpunkt Spezifikationen**

### **Authentifizierung & Benutzer-Management**

#### **POST /api/auth/register**
```json
{
  "endpoint": "/api/auth/register",
  "method": "POST",
  "description": "Registriert einen neuen Benutzer",
  "request_body": {
    "first_name": "string (required)",
    "last_name": "string (required)",
    "email": "string (required, unique)",
    "password": "string (required, min 6 chars)",
    "phone_number": "string (optional)"
  },
  "responses": {
    "201": {
      "message": "User created successfully",
      "user_id": "integer",
      "is_superadmin": "boolean"
    },
    "400": {
      "error": "Validation error",
      "details": "object"
    },
    "409": {
      "error": "Email already exists"
    }
  }
}
```

#### **POST /api/auth/login**
```json
{
  "endpoint": "/api/auth/login",
  "method": "POST",
  "description": "Authentifiziert einen Benutzer",
  "request_body": {
    "email": "string (required)",
    "password": "string (required)"
  },
  "responses": {
    "200": {
      "message": "Login successful",
      "user": {
        "user_id": "integer",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "is_superadmin": "boolean"
      },
      "session_token": "string"
    },
    "401": {
      "error": "Invalid credentials"
    }
  }
}
```

#### **GET /api/users/profile**
```json
{
  "endpoint": "/api/users/profile",
  "method": "GET",
  "description": "Ruft das Benutzerprofil ab",
  "authentication": "required",
  "responses": {
    "200": {
      "user": {
        "user_id": "integer",
        "email": "string",
        "first_name": "string",
        "last_name": "string",
        "phone_number": "string",
        "profile_image_url": "string",
        "linkedin_url": "string",
        "twitter_url": "string",
        "website_url": "string",
        "specializations": "array",
        "statistics": {
          "total_referrals": "integer",
          "successful_referrals": "integer",
          "total_earnings": "decimal",
          "success_rate": "decimal"
        }
      }
    }
  }
}
```

#### **PUT /api/users/profile**
```json
{
  "endpoint": "/api/users/profile",
  "method": "PUT",
  "description": "Aktualisiert das Benutzerprofil",
  "authentication": "required",
  "request_body": {
    "first_name": "string (optional)",
    "last_name": "string (optional)",
    "phone_number": "string (optional)",
    "linkedin_url": "string (optional)",
    "twitter_url": "string (optional)",
    "website_url": "string (optional)"
  },
  "responses": {
    "200": {
      "message": "Profile updated successfully",
      "user": "object"
    }
  }
}
```

### **Job-Management APIs**

#### **GET /api/jobs**
```json
{
  "endpoint": "/api/jobs",
  "method": "GET",
  "description": "Ruft aktive Stellenausschreibungen ab",
  "authentication": "required",
  "query_parameters": {
    "page": "integer (default: 1)",
    "per_page": "integer (default: 10, max: 50)",
    "search": "string (optional)",
    "location": "string (optional)",
    "employment_type": "string (optional)",
    "min_salary": "decimal (optional)",
    "max_salary": "decimal (optional)",
    "sort_by": "string (default: 'created_at')",
    "sort_order": "string (default: 'desc')"
  },
  "responses": {
    "200": {
      "jobs": "array",
      "pagination": {
        "page": "integer",
        "per_page": "integer",
        "total": "integer",
        "pages": "integer"
      }
    }
  }
}
```

#### **GET /api/jobs/{job_id}**
```json
{
  "endpoint": "/api/jobs/{job_id}",
  "method": "GET",
  "description": "Ruft Details einer spezifischen Stellenausschreibung ab",
  "authentication": "required",
  "responses": {
    "200": {
      "job": {
        "job_id": "integer",
        "title": "string",
        "company": "string",
        "location": "string",
        "salary_min": "decimal",
        "salary_max": "decimal",
        "employment_type": "string",
        "referral_bonus": "decimal",
        "description": "string",
        "requirements": "string",
        "benefits": "string",
        "application_deadline": "datetime",
        "created_at": "datetime",
        "referral_count": "integer"
      }
    },
    "404": {
      "error": "Job not found"
    }
  }
}
```

#### **POST /api/jobs** (Superadmin only)
```json
{
  "endpoint": "/api/jobs",
  "method": "POST",
  "description": "Erstellt eine neue Stellenausschreibung",
  "authentication": "required (superadmin)",
  "request_body": {
    "title": "string (required)",
    "company": "string (required)",
    "location": "string (required)",
    "salary_min": "decimal (optional)",
    "salary_max": "decimal (optional)",
    "employment_type": "string (default: 'Vollzeit')",
    "referral_bonus": "decimal (required)",
    "description": "string (required)",
    "requirements": "string (optional)",
    "benefits": "string (optional)",
    "application_deadline": "datetime (optional)"
  },
  "responses": {
    "201": {
      "message": "Job created successfully",
      "job": "object"
    }
  }
}
```

### **Referral-Management APIs**

#### **POST /api/referrals**
```json
{
  "endpoint": "/api/referrals",
  "method": "POST",
  "description": "Erstellt eine neue Referral-Empfehlung",
  "authentication": "required",
  "content_type": "multipart/form-data",
  "request_body": {
    "job_id": "integer (required)",
    "candidate_first_name": "string (required)",
    "candidate_last_name": "string (required)",
    "candidate_email": "string (required)",
    "candidate_phone": "string (optional)",
    "candidate_linkedin": "string (optional)",
    "resume_file": "file (optional, PDF/DOC, max 5MB)",
    "recommendation_text": "string (required)",
    "relationship_type": "string (required)",
    "consent_confirmed": "boolean (required, must be true)"
  },
  "responses": {
    "201": {
      "message": "Referral submitted successfully",
      "referral": {
        "referral_id": "integer",
        "status": "string",
        "created_at": "datetime"
      }
    },
    "400": {
      "error": "Validation error",
      "details": "object"
    }
  }
}
```

#### **GET /api/referrals**
```json
{
  "endpoint": "/api/referrals",
  "method": "GET",
  "description": "Ruft Referrals des aktuellen Benutzers ab",
  "authentication": "required",
  "query_parameters": {
    "page": "integer (default: 1)",
    "per_page": "integer (default: 10)",
    "status": "string (optional)",
    "job_id": "integer (optional)",
    "date_from": "date (optional)",
    "date_to": "date (optional)"
  },
  "responses": {
    "200": {
      "referrals": "array",
      "statistics": {
        "total": "integer",
        "pending": "integer",
        "in_review": "integer",
        "interviewed": "integer",
        "hired": "integer",
        "rejected": "integer",
        "total_earnings": "decimal",
        "pending_earnings": "decimal"
      },
      "pagination": "object"
    }
  }
}
```

#### **GET /api/referrals/{referral_id}**
```json
{
  "endpoint": "/api/referrals/{referral_id}",
  "method": "GET",
  "description": "Ruft Details einer spezifischen Referral ab",
  "authentication": "required",
  "responses": {
    "200": {
      "referral": {
        "referral_id": "integer",
        "job": "object",
        "candidate_first_name": "string",
        "candidate_last_name": "string",
        "candidate_email": "string",
        "status": "string",
        "status_history": "array",
        "recommendation_text": "string",
        "relationship_type": "string",
        "created_at": "datetime",
        "updated_at": "datetime",
        "interview_date": "datetime",
        "hr_notes": "string",
        "bonus_amount": "decimal",
        "bonus_paid": "boolean"
      }
    },
    "403": {
      "error": "Access denied"
    },
    "404": {
      "error": "Referral not found"
    }
  }
}
```

#### **PUT /api/referrals/{referral_id}/status** (Superadmin only)
```json
{
  "endpoint": "/api/referrals/{referral_id}/status",
  "method": "PUT",
  "description": "Aktualisiert den Status einer Referral",
  "authentication": "required (superadmin)",
  "request_body": {
    "status": "string (required)",
    "hr_notes": "string (optional)",
    "interview_date": "datetime (optional)",
    "change_reason": "string (optional)"
  },
  "responses": {
    "200": {
      "message": "Status updated successfully",
      "referral": "object"
    }
  }
}
```

### **Payment-Management APIs**

#### **GET /api/payments**
```json
{
  "endpoint": "/api/payments",
  "method": "GET",
  "description": "Ruft Zahlungsinformationen ab",
  "authentication": "required",
  "query_parameters": {
    "page": "integer (default: 1)",
    "status": "string (optional)",
    "date_from": "date (optional)",
    "date_to": "date (optional)"
  },
  "responses": {
    "200": {
      "payments": "array",
      "summary": {
        "total_earned": "decimal",
        "total_paid": "decimal",
        "pending_amount": "decimal",
        "next_payment_date": "date"
      }
    }
  }
}
```

#### **POST /api/payments/process** (Superadmin only)
```json
{
  "endpoint": "/api/payments/process",
  "method": "POST",
  "description": "Verarbeitet ausstehende Zahlungen",
  "authentication": "required (superadmin)",
  "request_body": {
    "referral_ids": "array (required)",
    "payment_method": "string (required)",
    "payment_date": "date (optional, default: today)"
  },
  "responses": {
    "200": {
      "message": "Payments processed successfully",
      "processed_payments": "array",
      "total_amount": "decimal"
    }
  }
}
```

### **Analytics & Reporting APIs**

#### **GET /api/analytics/dashboard**
```json
{
  "endpoint": "/api/analytics/dashboard",
  "method": "GET",
  "description": "Ruft Dashboard-Statistiken ab",
  "authentication": "required",
  "responses": {
    "200": {
      "user_stats": {
        "total_referrals": "integer",
        "successful_referrals": "integer",
        "success_rate": "decimal",
        "total_earnings": "decimal",
        "pending_earnings": "decimal",
        "rank": "string"
      },
      "recent_activity": "array",
      "trending_jobs": "array"
    }
  }
}
```

#### **GET /api/analytics/admin** (Superadmin only)
```json
{
  "endpoint": "/api/analytics/admin",
  "method": "GET",
  "description": "Ruft System-weite Statistiken ab",
  "authentication": "required (superadmin)",
  "query_parameters": {
    "period": "string (default: '30d')",
    "metric": "string (optional)"
  },
  "responses": {
    "200": {
      "system_stats": {
        "total_users": "integer",
        "active_users": "integer",
        "total_jobs": "integer",
        "active_jobs": "integer",
        "total_referrals": "integer",
        "successful_referrals": "integer",
        "total_payments": "decimal",
        "pending_payments": "decimal"
      },
      "trends": {
        "user_growth": "array",
        "referral_volume": "array",
        "success_rates": "array"
      },
      "top_performers": "array"
    }
  }
}
```

### **File Upload APIs**

#### **POST /api/upload/resume**
```json
{
  "endpoint": "/api/upload/resume",
  "method": "POST",
  "description": "Lädt einen Lebenslauf hoch",
  "authentication": "required",
  "content_type": "multipart/form-data",
  "request_body": {
    "file": "file (required, PDF/DOC/DOCX, max 5MB)",
    "referral_id": "integer (optional)"
  },
  "responses": {
    "200": {
      "message": "File uploaded successfully",
      "file_path": "string",
      "file_size": "integer",
      "file_type": "string"
    },
    "400": {
      "error": "Invalid file format or size"
    }
  }
}
```

#### **POST /api/upload/profile-image**
```json
{
  "endpoint": "/api/upload/profile-image",
  "method": "POST",
  "description": "Lädt ein Profilbild hoch",
  "authentication": "required",
  "content_type": "multipart/form-data",
  "request_body": {
    "image": "file (required, JPG/PNG, max 2MB)"
  },
  "responses": {
    "200": {
      "message": "Profile image uploaded successfully",
      "image_url": "string"
    }
  }
}
```

---

## ⚙️ **3. Geschäftslogik-Spezifikationen**

### **Referral-Workflow Engine**

#### **Status-Übergänge:**
```python
REFERRAL_STATUS_FLOW = {
    'submitted': ['in_review', 'rejected'],
    'in_review': ['phone_screening', 'rejected'],
    'phone_screening': ['interview_scheduled', 'rejected'],
    'interview_scheduled': ['interviewed', 'no_show', 'rejected'],
    'interviewed': ['second_interview', 'offer_made', 'rejected'],
    'second_interview': ['offer_made', 'rejected'],
    'offer_made': ['offer_accepted', 'offer_declined', 'rejected'],
    'offer_accepted': ['hired', 'background_check_failed'],
    'hired': ['probation_passed', 'probation_failed'],
    'probation_passed': ['bonus_eligible'],
    'bonus_eligible': ['bonus_paid']
}
```

#### **Automatische Benachrichtigungen:**
```python
NOTIFICATION_TRIGGERS = {
    'status_change': {
        'recipients': ['referrer', 'hr_team'],
        'template': 'referral_status_update',
        'delay': 0
    },
    'interview_scheduled': {
        'recipients': ['referrer', 'candidate'],
        'template': 'interview_notification',
        'delay': 0
    },
    'bonus_eligible': {
        'recipients': ['referrer', 'finance_team'],
        'template': 'bonus_notification',
        'delay': 0
    },
    'payment_processed': {
        'recipients': ['referrer'],
        'template': 'payment_confirmation',
        'delay': 0
    }
}
```

### **Bonus-Berechnungs-Engine**

#### **Bonus-Regeln:**
```python
BONUS_CALCULATION_RULES = {
    'base_bonus': 'job_listing.referral_bonus',
    'multipliers': {
        'first_referral': 1.1,  # 10% Bonus für erste Empfehlung
        'multiple_hires': 1.05,  # 5% Bonus ab 3. erfolgreicher Empfehlung
        'hard_to_fill': 1.2,    # 20% Bonus für schwer zu besetzende Positionen
        'quick_hire': 1.15      # 15% Bonus wenn Einstellung < 30 Tage
    },
    'payment_schedule': {
        'probation_period': 90,  # Tage
        'payment_delay': 30      # Tage nach bestandener Probezeit
    }
}
```

### **Benutzer-Ranking-System**

#### **Rang-Berechnung:**
```python
USER_RANKING_SYSTEM = {
    'bronze': {
        'min_referrals': 1,
        'min_success_rate': 0.0,
        'benefits': ['basic_dashboard']
    },
    'silver': {
        'min_referrals': 5,
        'min_success_rate': 0.2,
        'benefits': ['priority_notifications', 'early_job_access']
    },
    'gold': {
        'min_referrals': 15,
        'min_success_rate': 0.3,
        'benefits': ['bonus_multiplier_1.05', 'exclusive_jobs']
    },
    'platinum': {
        'min_referrals': 30,
        'min_success_rate': 0.4,
        'benefits': ['bonus_multiplier_1.1', 'direct_hr_contact']
    }
}
```

---

## 🔗 **4. Externe Integrations-Spezifikationen**

### **Zoho ATS Integration**

#### **Webhook-Endpunkte:**
```python
ZOHO_WEBHOOK_ENDPOINTS = {
    'candidate_status_update': '/api/webhooks/zoho/candidate-status',
    'interview_scheduled': '/api/webhooks/zoho/interview-scheduled',
    'offer_made': '/api/webhooks/zoho/offer-made',
    'candidate_hired': '/api/webhooks/zoho/candidate-hired'
}
```

#### **API-Mapping:**
```python
ZOHO_FIELD_MAPPING = {
    'candidate_email': 'Email',
    'candidate_first_name': 'First_Name',
    'candidate_last_name': 'Last_Name',
    'candidate_phone': 'Phone',
    'job_title': 'Job_Opening_Name',
    'referrer_email': 'Referrer_Email',
    'application_status': 'Candidate_Status'
}
```

### **E-Mail-Service Integration**

#### **SendGrid/SMTP Konfiguration:**
```python
EMAIL_SERVICE_CONFIG = {
    'provider': 'sendgrid',  # oder 'smtp'
    'templates': {
        'referral_confirmation': 'template_id_1',
        'status_update': 'template_id_2',
        'interview_notification': 'template_id_3',
        'bonus_notification': 'template_id_4'
    },
    'sender_email': 'noreply@argo-aviation.com',
    'sender_name': 'Argo Aviation Referral Portal'
}
```

### **Payment-Gateway Integration**

#### **PayPal/Stripe Integration:**
```python
PAYMENT_GATEWAY_CONFIG = {
    'primary_provider': 'paypal',
    'fallback_provider': 'bank_transfer',
    'minimum_payout': 50.00,
    'payout_schedule': 'monthly',  # 'weekly', 'monthly', 'quarterly'
    'supported_currencies': ['EUR', 'USD'],
    'tax_handling': 'gross_payment'  # Brutto-Zahlung, Steuern trägt Empfänger
}
```

---

## 🔒 **5. Sicherheits-Spezifikationen**

### **Authentifizierung & Autorisierung**

#### **JWT Token-Konfiguration:**
```python
JWT_CONFIG = {
    'algorithm': 'HS256',
    'access_token_expire': 3600,  # 1 Stunde
    'refresh_token_expire': 604800,  # 7 Tage
    'issuer': 'argo-aviation-portal',
    'audience': 'portal-users'
}
```

#### **Rollen-basierte Zugriffskontrolle:**
```python
RBAC_PERMISSIONS = {
    'user': [
        'view_jobs',
        'create_referral',
        'view_own_referrals',
        'update_own_profile'
    ],
    'hr_manager': [
        'view_all_referrals',
        'update_referral_status',
        'view_candidate_details',
        'schedule_interviews'
    ],
    'superadmin': [
        'all_permissions',
        'manage_users',
        'manage_jobs',
        'process_payments',
        'view_analytics',
        'system_settings'
    ]
}
```

### **Daten-Verschlüsselung**

#### **Sensitive Daten-Felder:**
```python
ENCRYPTED_FIELDS = {
    'users': ['password_hash'],
    'payments': ['bank_details', 'transaction_id'],
    'audit_log': ['old_values', 'new_values'],
    'notification_queue': ['body_html', 'body_text']
}
```

### **Rate Limiting**

#### **API-Rate-Limits:**
```python
RATE_LIMITS = {
    'auth_endpoints': '5/minute',
    'referral_submission': '3/hour',
    'file_upload': '10/hour',
    'general_api': '100/hour',
    'admin_api': '1000/hour'
}
```

---

## 📊 **6. Performance & Monitoring Spezifikationen**

### **Caching-Strategie**

#### **Redis Cache-Konfiguration:**
```python
CACHE_CONFIG = {
    'job_listings': {
        'ttl': 300,  # 5 Minuten
        'key_pattern': 'jobs:list:{filters_hash}'
    },
    'user_stats': {
        'ttl': 900,  # 15 Minuten
        'key_pattern': 'user:stats:{user_id}'
    },
    'system_stats': {
        'ttl': 1800,  # 30 Minuten
        'key_pattern': 'system:stats:{period}'
    }
}
```

### **Datenbank-Optimierung**

#### **Index-Strategien:**
```sql
-- Performance-kritische Indizes
CREATE INDEX idx_referrals_referrer_status ON referrals(referrer_id, status);
CREATE INDEX idx_referrals_job_created ON referrals(job_id, created_at);
CREATE INDEX idx_jobs_active_created ON job_listings(is_active, created_at);
CREATE INDEX idx_users_email_active ON users(email, is_active);
CREATE INDEX idx_payments_referrer_status ON payments(referrer_id, payment_status);
```

### **Logging & Monitoring**

#### **Application Logging:**
```python
LOGGING_CONFIG = {
    'levels': {
        'production': 'WARNING',
        'staging': 'INFO',
        'development': 'DEBUG'
    },
    'handlers': {
        'file': 'logs/application.log',
        'azure_insights': 'enabled',
        'email_alerts': 'critical_errors_only'
    },
    'audit_events': [
        'user_login',
        'referral_submission',
        'status_change',
        'payment_processing',
        'admin_actions'
    ]
}
```

---

## 🚀 **7. Deployment & DevOps Spezifikationen**

### **Azure DevOps Pipeline**

#### **Build-Pipeline:**
```yaml
# azure-pipelines-backend.yml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - app/
    - requirements.txt
    - config.py

stages:
- stage: Build
  jobs:
  - job: BuildBackend
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
    - script: |
        pip install -r requirements.txt
        python -m pytest tests/
        python -m flake8 app/
      displayName: 'Test and Lint'
    - task: ArchiveFiles@2
      inputs:
        rootFolderOrFile: '$(Build.SourcesDirectory)'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/backend.zip'
    - task: PublishBuildArtifacts@1
```

#### **Deployment-Pipeline:**
```yaml
# azure-pipelines-deploy.yml
stages:
- stage: DeployDev
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/develop')
  jobs:
  - deployment: DeployToDevEnvironment
    environment: 'argo-aviation-dev'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'Azure-Subscription'
              appType: 'webAppLinux'
              appName: 'argo-aviation-dev'
              package: '$(Pipeline.Workspace)/drop/backend.zip'

- stage: DeployProd
  condition: eq(variables['Build.SourceBranch'], 'refs/heads/main')
  jobs:
  - deployment: DeployToProduction
    environment: 'argo-aviation-prod'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: 'Azure-Subscription'
              appType: 'webAppLinux'
              appName: 'argo-aviation-prod'
              package: '$(Pipeline.Workspace)/drop/backend.zip'
```

### **Environment-Konfiguration**

#### **Development Environment:**
```python
DEVELOPMENT_CONFIG = {
    'DEBUG': True,
    'TESTING': False,
    'DATABASE_URL': 'sqlite:///dev.db',
    'REDIS_URL': 'redis://localhost:6379/0',
    'EMAIL_BACKEND': 'console',
    'FILE_STORAGE': 'local',
    'CORS_ORIGINS': ['http://localhost:3000', 'http://localhost:5000']
}
```

#### **Production Environment:**
```python
PRODUCTION_CONFIG = {
    'DEBUG': False,
    'TESTING': False,
    'DATABASE_URL': 'azure_sql_connection_string',
    'REDIS_URL': 'azure_redis_connection_string',
    'EMAIL_BACKEND': 'sendgrid',
    'FILE_STORAGE': 'azure_blob',
    'CORS_ORIGINS': ['https://argo-aviation.com'],
    'SSL_REQUIRED': True,
    'SESSION_COOKIE_SECURE': True
}
```

---

## 📋 **8. Testing-Spezifikationen**

### **Unit Tests**

#### **Test-Coverage-Ziele:**
```python
TEST_COVERAGE_TARGETS = {
    'models': 95,
    'api_endpoints': 90,
    'business_logic': 95,
    'utilities': 85,
    'overall': 90
}
```

#### **Test-Kategorien:**
```python
TEST_CATEGORIES = {
    'unit_tests': {
        'models': 'test_models.py',
        'api': 'test_api.py',
        'auth': 'test_auth.py',
        'business_logic': 'test_business_logic.py'
    },
    'integration_tests': {
        'database': 'test_database_integration.py',
        'external_apis': 'test_external_integrations.py',
        'email_service': 'test_email_integration.py'
    },
    'end_to_end_tests': {
        'user_workflows': 'test_user_workflows.py',
        'admin_workflows': 'test_admin_workflows.py'
    }
}
```

### **API Testing**

#### **Postman Collection Structure:**
```json
{
  "collection_name": "Argo Aviation API Tests",
  "folders": [
    {
      "name": "Authentication",
      "requests": ["Register", "Login", "Logout", "Profile"]
    },
    {
      "name": "Jobs",
      "requests": ["List Jobs", "Get Job", "Create Job", "Update Job"]
    },
    {
      "name": "Referrals",
      "requests": ["Submit Referral", "List Referrals", "Update Status"]
    },
    {
      "name": "Payments",
      "requests": ["List Payments", "Process Payment"]
    },
    {
      "name": "Admin",
      "requests": ["System Stats", "User Management", "Analytics"]
    }
  ]
}
```

---

## 🔄 **9. Migration & Upgrade-Pfade**

### **Datenbank-Migrationen**

#### **Migration-Skripte:**
```python
# migrations/versions/002_add_specializations.py
def upgrade():
    op.create_table('user_specializations',
        sa.Column('specialization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('specialization_name', sa.String(100), nullable=False),
        sa.Column('experience_level', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('specialization_id')
    )

def downgrade():
    op.drop_table('user_specializations')
```

### **API-Versionierung**

#### **Versioning-Strategie:**
```python
API_VERSIONING = {
    'strategy': 'url_path',  # /api/v1/, /api/v2/
    'current_version': 'v1',
    'supported_versions': ['v1'],
    'deprecation_policy': {
        'notice_period': '6_months',
        'support_period': '12_months'
    }
}
```

---

## 📈 **10. Skalierungs-Spezifikationen**

### **Horizontal Scaling**

#### **Load Balancing:**
```python
SCALING_CONFIG = {
    'web_servers': {
        'min_instances': 2,
        'max_instances': 10,
        'cpu_threshold': 70,
        'memory_threshold': 80
    },
    'background_workers': {
        'min_instances': 1,
        'max_instances': 5,
        'queue_threshold': 100
    },
    'database': {
        'read_replicas': 2,
        'connection_pooling': True,
        'max_connections': 100
    }
}
```

### **Caching-Layers**

#### **Multi-Level Caching:**
```python
CACHING_LAYERS = {
    'application_cache': 'Redis',
    'database_cache': 'Azure SQL Cache',
    'cdn_cache': 'Azure CDN',
    'browser_cache': 'HTTP Headers'
}
```

---

Diese Backend-Wireframes und API-Spezifikationen bilden die vollständige technische Grundlage für die Implementierung des Argo Aviation Referral Portals. Sie definieren alle notwendigen Komponenten für ein Enterprise-level System mit hoher Skalierbarkeit, Sicherheit und Performance.

