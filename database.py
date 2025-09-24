import sqlite3
from typing import List, Dict, Any, Optional
from models import Internship

DB_NAME = "internships.db"

class SQLiteDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.load_sample_data()

    def create_tables(self):
        cur = self.conn.cursor()

        # Internships
        cur.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            location TEXT,
            sector TEXT,
            duration TEXT,
            stipend TEXT,
            description TEXT,
            required_skills TEXT,
            education_requirement TEXT,
            experience_required TEXT,
            remote_option INTEGER,
            application_deadline TEXT
        )
        """)

        # User Profiles
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            session_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            education_level TEXT,
            field_of_study TEXT,
            skills TEXT,
            interests TEXT,
            location TEXT,
            preferred_locations TEXT,
            experience_level TEXT,
            language_preference TEXT
        )
        """)

        # Applications
        cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            application_id TEXT PRIMARY KEY,
            user_id TEXT,
            internship_id TEXT,
            status TEXT
        )
        """)

        self.conn.commit()

    def load_sample_data(self):
        """Seed sample internships if DB is empty"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM internships")
        count = cur.fetchone()[0]
        if count > 0:
            return

        sample_internships = [
            {
                "title": "Software Development Intern",
                "company": "TechCorp India",
                "location": "Bangalore",
                "sector": "Technology",
                "duration": "3 months",
                "stipend": "₹15,000/month",
                "description": "Work on web applications using Python and React",
                "required_skills": ["Python", "JavaScript", "React", "Database"],
                "education_requirement": "undergraduate",
                "experience_required": "beginner",
                "remote_option": True,
                "application_deadline": "2025-10-15",
            },
            {
                "title": "Digital Marketing Intern",
                "company": "Marketing Solutions Ltd",
                "location": "Mumbai",
                "sector": "Marketing",
                "duration": "2 months",
                "stipend": "₹12,000/month",
                "description": "Assist in social media campaigns and content creation",
                "required_skills": ["Social Media", "Content Writing", "Analytics", "Communication"],
                "education_requirement": "undergraduate",
                "experience_required": "beginner",
                "remote_option": True,
                "application_deadline": "2025-10-20",
            },
        ]

        for internship in sample_internships:
            self.add_internship(internship)

    # ---------------- Internships ----------------
    def get_all_internships(self) -> List[Internship]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM internships")
        rows = cur.fetchall()
        return [Internship(
            id=row["id"],
            title=row["title"],
            company=row["company"],
            location=row["location"],
            sector=row["sector"],
            duration=row["duration"],
            stipend=row["stipend"],
            description=row["description"],
            required_skills=row["required_skills"].split(","),
            education_requirement=row["education_requirement"],
            experience_required=row["experience_required"],
            remote_option=bool(row["remote_option"]),
            application_deadline=row["application_deadline"]
        ) for row in rows]

    def get_internship_by_id(self, internship_id: str) -> Optional[Internship]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM internships WHERE id=?", (internship_id,))
        row = cur.fetchone()
        if row:
            return Internship(
                id=row["id"],
                title=row["title"],
                company=row["company"],
                location=row["location"],
                sector=row["sector"],
                duration=row["duration"],
                stipend=row["stipend"],
                description=row["description"],
                required_skills=row["required_skills"].split(","),
                education_requirement=row["education_requirement"],
                experience_required=row["experience_required"],
                remote_option=bool(row["remote_option"]),
                application_deadline=row["application_deadline"]
            )
        return None

    def add_internship(self, internship_data: dict) -> Internship:
        """Add internship with auto-generated ID"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM internships")
        count = cur.fetchone()[0]
        new_id = f"INT{count + 1:03d}"

        cur.execute("""
            INSERT OR REPLACE INTO internships VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            new_id,
            internship_data["title"],
            internship_data["company"],
            internship_data["location"],
            internship_data["sector"],
            internship_data["duration"],
            internship_data.get("stipend"),
            internship_data["description"],
            ",".join(internship_data["required_skills"]),
            internship_data["education_requirement"],
            internship_data["experience_required"],
            int(internship_data["remote_option"]),
            internship_data["application_deadline"]
        ))
        self.conn.commit()
        return self.get_internship_by_id(new_id)

    # ---------------- User Profiles ----------------
    def save_user_profile(self, profile_data: dict) -> str:
        session_id = f"user_{profile_data['name']}_{len(profile_data['skills'])}"
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO user_profiles VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            session_id,
            profile_data["name"],
            profile_data["age"],
            profile_data["education_level"],
            profile_data["field_of_study"],
            ",".join(profile_data["skills"]),
            ",".join(profile_data["interests"]),
            profile_data["location"],
            ",".join(profile_data["preferred_locations"]),
            profile_data["experience_level"],
            profile_data["language_preference"]
        ))
        self.conn.commit()
        return session_id

    def get_user_profile(self, session_id: str) -> Optional[dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM user_profiles WHERE session_id=?", (session_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
        return None

    # ---------------- Applications ----------------
    def apply_to_internship(self, session_id: str, internship_id: str) -> Dict[str, Any]:
        internship = self.get_internship_by_id(internship_id)
        if not internship:
            return {"error": "Internship not found"}

        user_profile = self.get_user_profile(session_id)
        if not user_profile:
            return {"error": "User profile not found"}

        application_id = f"APP{session_id}_{internship_id}"
        cur = self.conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO applications VALUES (?,?,?,?)
        """, (application_id, session_id, internship_id, "Applied"))
        self.conn.commit()

        return {"application_id": application_id, "user_id": session_id, "internship_id": internship_id, "status": "Applied"}

    def get_applications_by_user(self, session_id: str) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM applications WHERE user_id=?", (session_id,))
        return [dict(row) for row in cur.fetchall()]

    # Compatibility wrappers
    def apply_for_internship(self, session_id: str, internship_id: str) -> bool:
        result = self.apply_to_internship(session_id, internship_id)
        return "error" not in result

    def get_user_applications(self, session_id: str):
        apps = self.get_applications_by_user(session_id)
        internships = []
        for app in apps:
            internship = self.get_internship_by_id(app["internship_id"])
            if internship:
                internships.append(internship.model_dump())
        return internships


# Global DB instance
db = SQLiteDatabase()
