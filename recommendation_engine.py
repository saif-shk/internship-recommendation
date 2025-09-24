from typing import List, Tuple
from models import UserProfile, Internship, Recommendation
from database import db
import datetime

class RecommendationEngine:
    def __init__(self):
        # Skill synonym mapping
        self.skill_synonyms = {
            "programming": ["coding", "development", "software"],
            "python": ["django", "flask"],
            "javascript": ["js", "react", "node"],
            "design": ["graphic design", "ui", "ux", "visual"],
            "marketing": ["digital marketing", "social media"],
            "writing": ["content writing", "copywriting", "blogging"],
            "analysis": ["data analysis", "analytics", "research"]
        }

        # Weights (can be tuned later)
        self.weights = {
            "skills": 0.4,
            "education": 0.2,
            "location": 0.2,
            "interests": 0.2,
        }

    # ---------------- Matching Methods ----------------
    def calculate_skill_match(self, user_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str]]:
        user_skills_lower = [skill.lower().strip() for skill in user_skills]
        required_skills_lower = [skill.lower().strip() for skill in required_skills]
        
        matches = []
        match_score = 0
        
        for user_skill in user_skills_lower:
            # Direct & partial matches
            for req_skill in required_skills_lower:
                if user_skill == req_skill:
                    matches.append(req_skill.title())
                    match_score += 1
                    break
                elif user_skill in req_skill or req_skill in user_skill:
                    matches.append(req_skill.title())
                    match_score += 0.7
                    break
            
            # Synonym matches
            for synonym_group in self.skill_synonyms.values():
                if user_skill in synonym_group:
                    for req_skill in required_skills_lower:
                        if req_skill in synonym_group:
                            matches.append(req_skill.title())
                            match_score += 0.8
                            break
        
        # Normalize
        if required_skills:
            skill_score = min(match_score / len(required_skills), 1.0)
        else:
            skill_score = 0
            
        return skill_score, matches

    def calculate_education_match(self, user_education: str, required_education: str) -> float:
        education_hierarchy = {
            "high_school": 1,
            "diploma": 2,
            "undergraduate": 3,
            "postgraduate": 4
        }
        user_level = education_hierarchy.get(str(user_education).lower(), 0)
        required_level = education_hierarchy.get(required_education.lower(), 0)
        
        if user_level >= required_level:
            return 1.0
        elif user_level == required_level - 1:
            return 0.7
        else:
            return 0.3

    def calculate_location_match(self, user_location: str, preferred_locations: List[str], 
                               internship_location: str, remote_option: bool) -> float:
        if remote_option:
            return 1.0
        
        user_location_lower = user_location.lower().strip()
        internship_location_lower = internship_location.lower().strip()
        preferred_lower = [loc.lower().strip() for loc in preferred_locations]
        
        if user_location_lower == internship_location_lower:
            return 1.0
        if internship_location_lower in preferred_lower:
            return 0.9
        if any(loc in internship_location_lower or internship_location_lower in loc 
               for loc in [user_location_lower] + preferred_lower):
            return 0.6
        
        return 0.2

    def calculate_interest_match(self, user_interests: List[str], internship_sector: str, 
                               internship_title: str, internship_description: str) -> Tuple[float, List[str]]:
        user_interests_lower = [interest.lower().strip() for interest in user_interests]
        internship_text = f"{internship_sector} {internship_title} {internship_description}".lower()
        
        matches = []
        match_score = 0
        
        for interest in user_interests_lower:
            if interest in internship_text:
                matches.append(interest.title())
                match_score += 1
            elif any(word in internship_text for word in interest.split()):
                matches.append(interest.title())
                match_score += 0.7
        
        interest_score = min(match_score / len(user_interests), 1.0) if user_interests else 0
        return interest_score, matches

    # ---------------- Main Recommendation ----------------
    def get_recommendations(self, user_profile: UserProfile, session_id: str = None, limit: int = 5) -> List[Recommendation]:
        all_internships = db.get_all_internships()
        recommendations = []

        # Exclude already applied internships
        applied_ids = []
        if session_id:
            applied_ids = [app["internship_id"] for app in db.get_applications_by_user(session_id)]

        for internship in all_internships:
            if internship.id in applied_ids:
                continue  # skip already applied

            skill_score, skill_matches = self.calculate_skill_match(user_profile.skills, internship.required_skills)
            education_score = self.calculate_education_match(user_profile.education_level, internship.education_requirement)
            location_score = self.calculate_location_match(
                user_profile.location, user_profile.preferred_locations,
                internship.location, internship.remote_option
            )
            interest_score, interest_matches = self.calculate_interest_match(
                user_profile.interests, internship.sector, internship.title, internship.description
            )
            
            final_score = (
                skill_score * self.weights["skills"] +
                education_score * self.weights["education"] +
                location_score * self.weights["location"] +
                interest_score * self.weights["interests"]
            )
            
            match_reasons = []
            if skill_matches:
                match_reasons.append(f"Skills match: {', '.join(skill_matches[:3])}")
            if education_score >= 0.7:
                match_reasons.append("Education requirement met")
            if location_score >= 0.9:
                match_reasons.append("Remote work available" if internship.remote_option else "Location matches preference")
            if interest_matches:
                match_reasons.append(f"Interests align: {', '.join(interest_matches[:2])}")
            if internship.experience_required.lower() == user_profile.experience_level.lower():
                match_reasons.append("Experience level perfect match")
            
            if final_score > 0.3:
                recommendations.append(Recommendation(
                    internship=internship,
                    match_score=round(final_score * 100, 1),
                    match_reasons=match_reasons
                ))
        
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        return recommendations[:limit]

# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
