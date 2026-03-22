from fastapi import FastAPI ,HTTPException   
from pydantic import BaseModel, Field
from typing import List, Optional

app=FastAPI()
#==================Models======================
class AppointmentRequest(BaseModel):
   patient_name: str = Field(min_length=2)
   doctor_id: int = Field(gt=0)
   date: str = Field(min_length=8)
   reason: str = Field(min_length=5)
   appointment_type: str = "in-person"
   senior_citizen: bool = False
class AppointmentRequest(BaseModel):
    patient_name: str = Field(min_length=2)
    doctor_id: int = Field(gt=0)
    date: str = Field(min_length=8)
    reason: str = Field(min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool = False
class NewDoctor(BaseModel):
    name: str = Field(min_length=2)
    specialization: str = Field(min_length=2)
    fee: int = Field(gt=0)
    experience_years: int = Field(gt=0)
    is_available: bool = True


#---------DATA--------#
doctors=[
    {"id": 1, "name": "Dr. Chandra Shekar", "specialization": "Cardiologist", "fee": 800, "experience_years": 15, "is_available": True},
    {"id": 2, "name": "Dr. Nagaraj Sharma", "specialization": "Dermatologist", "fee": 500, "experience_years": 8, "is_available": True},
    {"id": 3, "name": "Dr. Suresh Reddy", "specialization": "Pediatrician", "fee": 600, "experience_years": 10, "is_available": False},
    {"id": 4, "name": "Dr. Deepika Reddy", "specialization": "Cardiologist", "fee": 300, "experience_years": 5, "is_available": True},
    {"id": 5, "name": "Dr. Vasudha", "specialization": "Gynaecologist", "fee": 900, "experience_years": 18, "is_available": False},
    {"id": 6, "name": "Dr. Meena Gupta", "specialization": "Dermatologist", "fee": 450, "experience_years": 7, "is_available": True}
]
appointments=[]
appt_counter=1
#------------Q1-------------
@app.get("/")
def home():
    return{"Message":"Welcome to Medicare Clinic"}
#------------Q2--------
@app.get("/doctors")
def get_all_doctors():
   return {'doctors': doctors, 'total': len(doctors)}
#--------------Q4--------
@app.get("/appointmenst")
def get_appointments():
    return{"appointments":appointments,
           "total":len(appointments)
           }
#--------------Q5-------------
@app.get("/doctors/summary")
def doctors_summary():
    available_count = sum(1 for d in doctors if d["is_available"])
    most_exp = max(doctors, key=lambda x: x["experience_years"])
    cheapest = min(doctors, key=lambda x: x["fee"])
    spec_count = {}
    for d in doctors:
        spec = d["specialization"]
        spec_count[spec] = spec_count.get(spec, 0) + 1
    return {
        "total_doctors": len(doctors),
        "available_count": available_count,
        "most_experienced": most_exp["name"],
        "cheapest_fee": cheapest["fee"],
        "specialization_count": spec_count
    }

#---------------------Q7------------
def find_doctor(doctor_id):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    return None
def calculate_fee(base_fee, appointment_type, senior=False):
    if appointment_type == "video":
        fee = base_fee * 0.8
    elif appointment_type == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee
    original_fee = fee
    if senior:
        fee = fee * 0.85  # 15% discount
    return original_fee, fee
#------------------Q8---------
@app.post("/appointments")
def create_appointment(req: AppointmentRequest):
    global appt_counter
    doctor = find_doctor(req.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor["is_available"]:
        raise HTTPException(status_code=400, detail="Doctor not available")
    original_fee, final_fee = calculate_fee(
        doctor["fee"], req.appointment_type, req.senior_citizen
    )
    appointment = {
        "appointment_id": appt_counter,
        "patient": req.patient_name,
        "doctor_name": doctor["name"],
        "doctor_id": doctor["id"],
        "date": req.date,
        "type": req.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    
    }
    appointments.append(appointment)
    appt_counter += 1
    doctor["is_available"] = True
    return appointment
#---------------------------10---------
@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = doctors
    if specialization is not None:
        result = [d for d in result if d["specialization"].lower() == specialization.lower()]
    if max_fee is not None:
        result = [d for d in result if d["fee"] <= max_fee]
    if min_experience is not None:
        result = [d for d in result if d["experience_years"] >= min_experience]
    if is_available is not None:
        result = [d for d in result if d["is_available"] == is_available]
    return {
        "filtered_doctors": result,
        "count": len(result)
    }

#-------------------Q11--------------
@app.post("/doctors", status_code=201)
def add_doctor(doc: NewDoctor):
    for d in doctors:
        if d["name"].lower() == doc.name.lower():
            raise HTTPException(status_code=400, detail="Doctor already exists")
    new_doc = doc.dict()
    new_doc["id"] = len(doctors) + 1
    doctors.append(new_doc)
    return new_doc
#----------------Q12-----------
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int, fee: int = None, is_available: bool = None):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if fee is not None:
        doctor["fee"] = fee
    if is_available is not None:
        doctor["is_available"] = is_available
    return doctor
#-------------------------Q13------------
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for appt in appointments:
        if appt["doctor_id"] == doctor_id and appt["status"] == "scheduled":
            raise HTTPException(status_code=400, detail="Doctor has active appointments")
    doctors.remove(doctor)
    return {"message": "Doctor deleted successfully"}
#---------------Q14-------------
def find_appointment(appt_id):
    for a in appointments:
        if a["appointment_id"] == appt_id:
            return a
    return None
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt["status"] = "confirmed"
    return appt
@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt["status"] = "cancelled"
    doctor = find_doctor(appt["doctor_id"])
    if doctor:
        doctor["is_available"] = True
    return appt
#-------------Q16-------------
@app.get("/doctors/search")
def search_doctors(keyword: str):
    result = [
        d for d in doctors
        if keyword.lower() in d["name"].lower()
        or keyword.lower() in d["specialization"].lower()
    ]
    if not result:
        return {"message": "No doctors found"}
    return {"results": result, "total_found": len(result)}
#------------------Q15------------
@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    appt["status"] = "completed"
    return appt
@app.get("/appointments/active")
def active_appointments():
    result = [a for a in appointments if a["status"] in ["scheduled", "confirmed"]]
    return {"active_appointments": result, "count": len(result)}
@app.get("/appointments/by-doctor/{doctor_id}")
def appointments_by_doctor(doctor_id: int):
    result = [a for a in appointments if a["doctor_id"] == doctor_id]
    return {"appointments": result, "count": len(result)}
#--------------------Q17------------
@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee"):
    if sort_by not in ["fee", "name", "experience_years"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    sorted_list = sorted(doctors, key=lambda x: x[sort_by])
    return {
        "sorted_by": sort_by,
        "doctors": sorted_list
    }
#--------------------Q18----------------
import math
@app.get("/doctors/page")
def paginate_doctors(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    end = start + limit
    total = len(doctors)
    total_pages = math.ceil(total / limit)
    return {
        "page": page,
        "total_pages": total_pages,
        "data": doctors[start:end]
    }
#--------------------Q19--------------
@app.get("/appointments/search")
def search_appointments(patient_name: str):
    result = [
        a for a in appointments
        if patient_name.lower() in a["patient"].lower()
    ]
    return {"results": result, "count": len(result)}
@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "date"):
    if sort_by not in ["fee", "date"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    return {"data": sorted(appointments, key=lambda x: x.get(sort_by, 0))}

@app.get("/appointments/page")
def paginate_appointments(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "data": appointments[start:end]
    }
#-----------------Q20-------------
@app.get("/doctors/browse")
def browse_doctors(
    keyword: str = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = doctors
    # ----------- Filter
    if keyword:
        result = [
            d for d in result
            if keyword.lower() in d["name"].lower()
            or keyword.lower() in d["specialization"].lower()
        ]
   #------   Sort-------
    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)
    # -------------Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    return {
        "total": len(result),
        "page": page,
        "limit": limit,
        "results": paginated
    }
#----------------Q3---------
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int):
    for doc in doctors:
        if doc["id"] == doctor_id:
            return doc
    raise HTTPException(status_code=404, detail="Doctor not found")