from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import UserProfile, RecommendationResponse
from database import db
from recommendation_engine import recommendation_engine

app = FastAPI(
    title="PM Internship Recommendation System",
    description="AI-powered internship matching for PM Internship Scheme",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# =====================
# Home + Profile Routes
# =====================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_form(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.post("/create-profile")
async def create_profile(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    education_level: str = Form(...),
    field_of_study: str = Form(...),
    skills: str = Form(...),
    interests: str = Form(...),
    location: str = Form(...),
    preferred_locations: str = Form(default=""),
    experience_level: str = Form(default="beginner"),
    language_preference: str = Form(default="english")
):
    try:
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]
        interests_list = [i.strip() for i in interests.split(",") if i.strip()]
        preferred_locations_list = [l.strip() for l in preferred_locations.split(",") if l.strip()]

        user_profile = UserProfile(
            name=name,
            age=age,
            education_level=education_level,
            field_of_study=field_of_study,
            skills=skills_list,
            interests=interests_list,
            location=location,
            preferred_locations=preferred_locations_list,
            experience_level=experience_level,
            language_preference=language_preference
        )

        session_id = db.save_user_profile(user_profile.model_dump())
        recommendations = recommendation_engine.get_recommendations(user_profile, session_id)

        return templates.TemplateResponse("recommendations.html", {
            "request": request,
            "user_name": user_profile.name,
            "recommendations": [rec.model_dump() for rec in recommendations],
            "total_matches": len(recommendations),
            "session_id": session_id
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing profile: {str(e)}")


# =====================
# Admin Panel
# =====================
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    internships = db.get_all_internships()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "internships": [i.model_dump() for i in internships]
    })


@app.post("/admin/add-internship")
async def add_internship(
    request: Request,
    title: str = Form(...),
    company: str = Form(...),
    location: str = Form(...),
    sector: str = Form(...),
    duration: str = Form(...),
    stipend: str = Form(...),
    description: str = Form(...),
    required_skills: str = Form(...),
    education_requirement: str = Form(...),
    experience_required: str = Form(...),
    remote_option: bool = Form(False),
    application_deadline: str = Form(...)
):
    internship_data = {
        "title": title,
        "company": company,
        "location": location,
        "sector": sector,
        "duration": duration,
        "stipend": stipend,
        "description": description,
        "required_skills": [s.strip() for s in required_skills.split(",")],
        "education_requirement": education_requirement,
        "experience_required": experience_required,
        "remote_option": remote_option,
        "application_deadline": application_deadline
    }
    db.add_internship(internship_data)
    return RedirectResponse(url="/admin", status_code=303)


# =====================
# Internships + Applications
# =====================
@app.get("/internships", response_class=HTMLResponse)
async def browse_internships(request: Request):
    internships = db.get_all_internships()
    return templates.TemplateResponse("internships.html", {
        "request": request,
        "internships": [i.model_dump() for i in internships]
    })


@app.post("/apply/{internship_id}")
async def apply_to_internship(
    request: Request,
    internship_id: str,
    session_id: str = Form(...)
):
    success = db.apply_for_internship(session_id, internship_id)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid application")
    return RedirectResponse(url=f"/my-applications/{session_id}", status_code=303)


@app.get("/my-applications/{session_id}", response_class=HTMLResponse)
async def my_applications(request: Request, session_id: str):
    apps = db.get_user_applications(session_id)
    return templates.TemplateResponse("applications.html", {
        "request": request,
        "applications": apps
    })


# =====================
# API Endpoints
# =====================
@app.get("/api/internships")
async def get_all_internships():
    return {"internships": [internship.model_dump() for internship in db.get_all_internships()]}


@app.get("/api/recommendations/{session_id}")
async def get_recommendations_api(session_id: str):
    user_data = db.get_user_profile(session_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User session not found")

    user_profile = UserProfile(**user_data)
    recommendations = recommendation_engine.get_recommendations(user_profile, session_id)

    return RecommendationResponse(
        user_name=user_profile.name,
        recommendations=recommendations,
        total_matches=len(recommendations)
    )


# =====================
# Health Check
# =====================
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "PM Internship Recommendation System is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
