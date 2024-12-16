from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.exceptions import ResponseValidationError
from sqlalchemy import create_engine, Column, Integer, Date, DECIMAL
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import os
from pathlib import Path

# Create a 'data' directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{data_dir}/database.sqlite"
)

app = FastAPI()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class TUFERecords(Base):
    __tablename__ = "tuik_tufe_records"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Date, nullable=False, unique=True)
    general_tufe = Column(DECIMAL(5, 2))
    general_tufe_change_rate = Column(DECIMAL(5, 2))
    health = Column(DECIMAL(5, 2))
    energy = Column(DECIMAL(5, 2))
    food_and_non_alcoholic_beverages = Column(DECIMAL(5, 2))
    communication = Column(DECIMAL(5, 2))
    transportation = Column(DECIMAL(5, 2))

class Income(Base):
    __tablename__ = "income"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Date, nullable=False, unique=True)
    average_income = Column(DECIMAL(10, 2))

class HeartDiseaseMortalities(Base):
    __tablename__ = "heart_disease_mortalities"
    id = Column(Integer, primary_key=True, index=True)
    month = Column(Date, nullable=False, unique=True)
    mortality_count = Column(Integer)

# Pydantic Models
class TUFESchema(BaseModel):
    month: str
    general_tufe: float = Field(..., ge=0)
    general_tufe_change_rate: float = Field(..., ge=0, le=100)
    health: float = Field(..., ge=0)
    energy: float = Field(..., ge=0)
    food_and_non_alcoholic_beverages: float = Field(..., ge=0)
    communication: float = Field(..., ge=0)
    transportation: float = Field(..., ge=0)

    class Config:
        orm_mode = True

    def from_orm(self, obj):
        # Create a dictionary from the SQLAlchemy model
        data = {
            'month': obj.month.strftime('%Y-%m-%d'),
            'general_tufe': float(obj.general_tufe),
            'general_tufe_change_rate': float(obj.general_tufe_change_rate),
            'health': float(obj.health),
            'energy': float(obj.energy),
            'food_and_non_alcoholic_beverages': float(obj.food_and_non_alcoholic_beverages),
            'communication': float(obj.communication),
            'transportation': float(obj.transportation)
        }
        return TUFESchema(**data)

class IncomeSchema(BaseModel):
    month: str
    average_income: float = Field(..., ge=0)

    class Config:
        orm_mode = True

class HeartDiseaseMortalitiesSchema(BaseModel):
    month: str
    mortality_count: int = Field(..., ge=0)

    class Config:
        orm_mode = True

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
def root():
    return {"message": "Welcome to the TUFE API"}

@app.get("/tufe", response_model=List[TUFESchema])
def get_all_tufe_records(skip: int = 0, limit: int = 10, db=Depends(get_db)):
    records = db.query(TUFERecords).offset(skip).limit(limit).all()
    return [TUFESchema.from_orm(record) for record in records]

@app.post("/tufe", response_model=TUFESchema)
async def create_tufe_record(record: TUFESchema = Body(...), db=Depends(get_db)):
    try:
        record_dict = record.dict()
        record_dict['month'] = datetime.strptime(record_dict['month'], '%Y-%m-%d').date()
        existing_record = db.query(TUFERecords).filter(TUFERecords.month == record_dict['month']).first()
        if existing_record:
            raise HTTPException(status_code=400, detail=f"A record for month {record_dict['month']} already exists")
        db_record = TUFERecords(**record_dict)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ResponseValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tufe/{month}", response_model=TUFESchema)
def get_tufe_record(month: str, db=Depends(get_db)):
    try:
        date_obj = datetime.strptime(month, '%Y-%m-%d').date()
        record = db.query(TUFERecords).filter(TUFERecords.month == date_obj).first()
        if not record:
            raise HTTPException(status_code=404, detail="TUFE record not found")
        return TUFESchema.from_orm(record)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@app.put("/tufe/{month}", response_model=TUFESchema)
def update_tufe_record(month: str, record: TUFESchema, db=Depends(get_db)):
    try:
        date_obj = datetime.strptime(month, '%Y-%m-%d').date()
        db_record = db.query(TUFERecords).filter(TUFERecords.month == date_obj).first()
        if not db_record:
            raise HTTPException(status_code=404, detail="TUFE record not found")
        for key, value in record.dict(exclude_unset=True).items():
            setattr(db_record, key, value)
        db.commit()
        db.refresh(db_record)
        return db_record
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@app.delete("/tufe/{month}")
def delete_tufe_record(month: str, db=Depends(get_db)):
    try:
        date_obj = datetime.strptime(month, '%Y-%m-%d').date()
        db_record = db.query(TUFERecords).filter(TUFERecords.month == date_obj).first()
        if not db_record:
            raise HTTPException(status_code=404, detail="TUFE record not found")
        db.delete(db_record)
        db.commit()
        return {"message": "TUFE record deleted"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")