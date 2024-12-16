# TUFE-Heart Disease Correlation API

## Overview
This API is a FastAPI-based web application that manages consumer price index (TUFE) records and heart disease mortality statistics, enabling analysis of potential correlations between economic indicators and public health outcomes. The API provides CRUD operations for both TUFE and mortality datasets, along with endpoints to explore relationships between economic factors and heart disease mortality rates.

## Features

- Retrieve TUFE Records: Fetch a list of TUFE records with pagination support.
- Create TUFE Records: Add new TUFE records with detailed attributes like health, energy, and food expenses.
- Update TUFE Records: Modify existing TUFE records by month.
- Delete TUFE Records: Remove TUFE records by month.
- Retrieve Single Record: Fetch detailed information for a specific month.
- SQLite Database: Data is stored in an SQLite database, with tables created automatically on startup.

## Endpoints

### Root Endpoint

- `GET /`
  - Returns a welcome message.

### TUFE Records

- `GET /tufe`
  - Fetch all TUFE records with pagination.
  - Query Parameters:
    - `skip` (default: 0): Number of records to skip.
    - `limit` (default: 10): Number of records to fetch.

- `POST /tufe`
  - Create a new TUFE record.
  - Request Body:
    - `month` (string, YYYY-MM-DD): Date of the record.
    - `general_tufe` (float): General TUFE index.
    - Other fields include detailed TUFE categories (health, energy, etc.).

- `GET /tufe/{month}`
  - Fetch a single TUFE record by month.
  - Path Parameter:
    - `month` (string, YYYY-MM-DD): Date of the record.

- `PUT /tufe/{month}`
  - Update an existing TUFE record by month.
  - Path Parameter:
    - `month` (string, YYYY-MM-DD): Date of the record.
  - Request Body: Same as POST /tufe.

- `DELETE /tufe/{month}`
  - Delete a TUFE record by month.
  - Path Parameter:
    - `month` (string, YYYY-MM-DD): Date of the record.

## Database Schema

### TUFERecords Table
- `id` (Integer, Primary Key)
- `month` (Date, Unique)
- `general_tufe` (Decimal)
- `general_tufe_change_rate` (Decimal)
- `health` (Decimal)
- `energy` (Decimal)
- `food_and_non_alcoholic_beverages` (Decimal)
- `communication` (Decimal)
- `transportation` (Decimal)

### Income Table
- `id` (Integer, Primary Key)
- `month` (Date, Unique)
- `average_income` (Decimal)

### HeartDiseaseMortalities Table
- `id` (Integer, Primary Key)
- `month` (Date, Unique)
- `mortality_count` (Integer)

## Setup Instructions

1. Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. Run the API
   ```bash
   uvicorn main:app --reload
   ```

3. Environment Variable
   - Set the `DATABASE_URL` environment variable to customize the database location (optional). By default, an SQLite database is created in the data directory.

4. Access the API
   - The API is available at http://127.0.0.1:8000.

5. Interactive Documentation
   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc
