# EzyAgric Mini Farm Manager - Backend API. Created by MUJUZI DENIS

A FastAPI-based backend application for managing farmers, farms, and season planning with activity tracking. This application allows field officers to register farmers and farms, create season plans with planned activities, log actual field activities, and view plan vs actual summaries.

Zero trust architecture approach has been implemented to ensure that only authenticated and authorized users can access resources. All sensitive endpoints require JWT authentication, and admin-level actions require a separate admin key. This minimizes the risk of unauthorized access and enforces strict separation of privileges.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Design and Assumptions](#design-and-assumptions)
- [Plan vs Actual Logic](#plan-vs-actual-logic)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Future Improvements](#future-improvements)

## Features

- **Farmer Management**: Register and manage farmers with authentication
- **Farm Management**: Create and manage farms associated with farmers
- **Season Planning**: Create season plans for crops with planned activities and estimated costs
- **Activity Tracking**: Log actual field activities with costs and notes
- **Plan vs Actual Summary**: View comparisons between planned and actual activities, including:
  - Activity statuses (Completed, Upcoming, Overdue)
  - Total estimated vs actual costs
  - Count of overdue activities

## Technology Stack

- **Framework**: FastAPI 0.115.13
- **ORM**: SQLAlchemy 2.0.41
- **Database**: SQLite (sqlitedb.db)
- **Migrations**: Alembic 1.16.2
- **Authentication**: JWT (PyJWT 2.10.1)
- **Password Hashing**: bcrypt 5.0.0
- **Python Version**: 3.13+

## Project Structure

```
ezyagric-backend/
├── alembic/                 # Database migrations
│   └── versions/
├── routers/                 # API route handlers
│   ├── farmers/            # Farmer endpoints
│   ├── farms/              # Farm endpoints
│   └── seasons/            # Season planning endpoints
├── main.py                  # FastAPI application entry point
├── models.py                # SQLAlchemy database models
├── database.py              # Database configuration
├── dependencies.py          # Dependency injection (auth, timezone)
├── utils.py                 # Settings and configuration
├── requirements.txt         # Python dependencies
├── alembic.ini              # Alembic configuration
└── sqlitedb.db              # SQLite database file
```

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd ezyagric-backend
   ```

2. **Create a virtual environment** (if not already created):
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate     # On Windows
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   Create a `.env` file in the project root with the following variables:
   ```env
   JWT_SECRET_KEY=your-secret-key-here-change-in-production
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
   ADMIN_KEY=your-admin-key-here-change-in-production
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

## Running the Application

1. **Activate the virtual environment** (if not already active):
   ```bash
   source venv/bin/activate
   ```

2. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```

   The application will start on `http://localhost:8000` by default.

3. **Access the API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

4. **Health check**: This helps to know if db connections are failing:
   ```bash
   curl http://localhost:8000/health
   ```

## API Endpoints

### Authentication

All endpoints (except `/farmers/login` and `/farmers` POST with admin key) require JWT authentication via the `Authorization` header(token):
```
token: JWT <token>
```

### Farmers

- `POST /farmers` - Create a new farmer (requires `admin-key` header)
- `GET /farmers` - Get all farmers (requires `admin-key` header)
- `POST /farmers/login` - Farmer login (returns JWT token)

### Farms

- `POST /farms` - Create a new farm (requires JWT authentication)
- `GET /farms?farmerId={id}` - Get farms, optionally filtered by farmerId
  - With JWT: Returns farms for authenticated farmer
  - With `admin-key` header: Returns all farms or filtered by farmerId

### Seasons

- `POST /seasons` - Create a new season plan (requires JWT authentication)
- `POST /seasons/{seasonId}/planned-activities` - Add planned activities to a season
- `POST /seasons/{seasonId}/actual-activities` - Log actual activities for a season
- `GET /seasons/{seasonId}` - Get season details with planned and actual activities
- `GET /seasons/{seasonId}/summary` - Get plan vs actual summary

## Design and Assumptions

### Domain Modeling

The application models the following core entities:

1. **Farmer**: Represents a farmer with authentication credentials
   - Fields: id, name, phoneNumber, email, hashedPassword, createdAt
   - Phone numbers and emails are unique

2. **Farm**: Represents a farm belonging to a farmer
   - Fields: id, farmerId, name, sizeAcres
   - One farmer can have multiple farms

3. **SeasonPlan**: Represents a cropping season for a farm
   - Fields: id, farmId, cropName, seasonName, totalEstimatedCostUgx, totalActualCostUgx, overDueActivitiesCount
   - One farm can have multiple season plans

4. **PlannedActivity**: Represents a planned activity in a season
   - Fields: id, seasonPlanId, activityType, targetDate, estimatedCostUgx, status
   - Status can be: COMPLETED, UPCOMING, or OVERDUE

5. **ActualActivity**: Represents an actual activity performed
   - Fields: id, seasonPlanId, activityType, actualDate, actualCostUgx, notes, plannedActivityId
   - Can be linked to a planned activity (optional) or added as extra

### Design Decisions

1. **Database Choice**: SQLite was chosen for simplicity and ease of setup, suitable for the assignment scope. The schema can easily be migrated to PostgreSQL or MySQL for production.

2. **Authentication**: JWT-based authentication ensures secure access. Farmers authenticate once and use tokens for subsequent requests.

3. **Authorization**: 
   - Farmers can only access their own farms and seasons
   - Admin endpoints require an admin key header
   - Field officers would authenticate as farmers in this implementation

4. **Timezone Handling**: Uses Africa/Nairobi timezone for date operations to align with EzyAgric's operational region.

5. **Cost Storage**: Total costs are stored as computed on request, and they are updated via the querying of planned activities if date.now is past the target date

6. **Status Management**: Activity status is stored in the PlannedActivity model. Status is recalculated based on:
   - Presence of matching actual activity (COMPLETED)
   - Comparison of targetDate with today's date (UPCOMING vs OVERDUE)

### Assumptions

1. **Activity Types**: Activity types are stored as strings (e.g., "LAND_PREPARATION", "PLANTING", "WEEDING", "SPRAYING", "HARVEST"). No strict enum validation is enforced at the API level.

2. **Date Handling**: All dates are stored as Date objects (without time). The system date is used for "today" comparisons.

3. **Cost Currency**: All costs are in Ugandan Shillings (UGX) and stored as Numeric with 2 decimal places.

4. **One-to-Many Relationships**: 
   - One farmer → many farms
   - One farm → many season plans
   - One season plan → many planned activities
   - One season plan → many actual activities
   - One planned activity → many actual activities (for tracking multiple executions)

5. **Cascade Deletes**: Deleting a farmer cascades to farms, which cascades to season plans, which cascades to activities.


## Future Improvements

If given more time, the following improvements would enhance the application:

### 1. **Introducing Caching at the data access layer**
   - Redis cache can be used for caching heavy responses like the /seasons/{id}/summary and /seasons/{id}

### 2. **Enhanced Activity Matching**
   - Improve logic to match actual activities to planned activities by activity type and date proximity
   - Support multiple actual activities for a single planned activity (e.g., multiple weeding sessions)

### 3. **Multi-Season Support**
   - Add endpoints to list all seasons for a farm
   - Support season templates that can be reused
   - Historical season comparison views

### 4. **Backend Sync Capabilities**
   - Add endpoints for bulk data synchronization
   - Support offline-first architecture for mobile apps
   - Implement conflict resolution for concurrent updates

### 5. **Improved UX Features**
   - Add filtering and pagination for list endpoints
   - Support date range queries for activities
   - Add activity type filtering in summary views
   - Include activity notes in summary responses
   - adding more CRUD endpoints on resources to be used on deleting and updating.
   - Sending notifications to farmers on the overdue tasks. via sms, email or also app notications using the firebase cloud messaging.

### 6. **Testing**
   - Add unit tests for business logic
   - Add integration tests for API endpoints
   - Add tests for authentication and authorization

### 7. **Documentation**
   - Add more detailed API documentation with examples
   - Include request/response examples in Swagger
   - Add error code documentation

### 8. **Production Readiness**
   - Migrate to PostgreSQL for production use
   - Add logging and monitoring
   - Implement rate limiting
   - Add input sanitization and SQL injection prevention (already handled by SQLAlchemy ORM)
   - Set up CI/CD pipeline

---

## Contact

For questions or issues, please contact:
- Email: dmujuzi0@gmail.com, +256743056702

---

**Note**: This is a technical assignment submission for EzyAgric's Software Engineer position.

