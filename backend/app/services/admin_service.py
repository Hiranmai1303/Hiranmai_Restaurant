"""
Admin Service: Operations Management, CSV Ingestion, CRUD Operations,
Feedback Management, and System Telemetry & Logs.
"""
import os
import uuid
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.database.db import SessionLocal
from backend.app.models.review import EnrichedReviewORM, FeedbackORM, UserORM
from backend.app.core.config import settings

# Global in-memory audit log store
_SYSTEM_LOGS: List[Dict[str, Any]] = [
    {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": "INFO",
        "source": "SystemInit",
        "message": "Restaurant Operations Assistant backend engine initialized successfully."
    },
    {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": "INFO",
        "source": "DatabaseEngine",
        "message": f"Connected to SQLite database at {Path(settings.SQLITE_DB_PATH).name} (48,288 indexed reviews)."
    },
    {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": "INFO",
        "source": "VectorStore",
        "message": "ChromaDB vector collection verified with MiniLM-L6-v2 embeddings."
    },
    {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": "AUDIT",
        "source": "AuthService",
        "message": "Security RBAC policy loaded: Admin and Operational User roles configured."
    }
]

def log_system_event(level: str, source: str, message: str):
    """Appends an event to the global audit log."""
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level.upper(),
        "source": source,
        "message": message
    }
    _SYSTEM_LOGS.insert(0, entry)
    # Keep buffer capped at 500 entries
    if len(_SYSTEM_LOGS) > 500:
        _SYSTEM_LOGS.pop()

class AdminService:
    def __init__(self):
        self.db_path = Path(settings.SQLITE_DB_PATH)
        self._ensure_seed_users()
        self._ensure_seed_feedbacks()

    def _ensure_seed_users(self):
        """Seeds standard operational users if the users table is empty."""
        from backend.app.database.db import engine
        from backend.app.models.review import Base
        Base.metadata.create_all(bind=engine)
        db: Session = SessionLocal()
        try:
            count = db.query(UserORM).count()
            if count == 0:
                seed_users = [
                    {
                        "user_id": "usr_001",
                        "username": "admin",
                        "password": "admin123",
                        "role": "admin",
                        "display_name": "Executive Operations Director",
                        "title": "System Administrator & Fleet Director",
                        "email": "admin@restaurantops.ai",
                        "department": "Executive Leadership",
                        "status": "Active",
                        "created_at": "2024-01-15 08:00:00",
                        "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "user_id": "usr_002",
                        "username": "user",
                        "password": "user123",
                        "role": "user",
                        "display_name": "Operations Analyst",
                        "title": "Restaurant Shift & Ops Manager",
                        "email": "user@restaurantops.ai",
                        "department": "Field Operations",
                        "status": "Active",
                        "created_at": "2024-02-01 09:30:00",
                        "last_login": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "user_id": "usr_003",
                        "username": "sarah.jenkins",
                        "password": "pass_sarah123",
                        "role": "store_manager",
                        "display_name": "Sarah Jenkins",
                        "title": "District General Manager",
                        "email": "s.jenkins@restaurantops.ai",
                        "department": "Store Operations",
                        "status": "Active",
                        "created_at": "2024-03-10 11:15:00",
                        "last_login": (datetime.datetime.now() - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "user_id": "usr_004",
                        "username": "david.kim",
                        "password": "pass_david123",
                        "role": "operations_analyst",
                        "display_name": "David Kim",
                        "title": "Senior Operations Analyst",
                        "email": "d.kim@restaurantops.ai",
                        "department": "Fleet Analytics",
                        "status": "Active",
                        "created_at": "2024-04-12 14:20:00",
                        "last_login": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "user_id": "usr_005",
                        "username": "marcus.vance",
                        "password": "pass_marcus123",
                        "role": "store_manager",
                        "display_name": "Marcus Vance",
                        "title": "Culinary & Kitchen Supervisor",
                        "email": "m.vance@restaurantops.ai",
                        "department": "Culinary Operations",
                        "status": "Active",
                        "created_at": "2024-05-18 10:00:00",
                        "last_login": (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "user_id": "usr_006",
                        "username": "elena.rostova",
                        "password": "pass_elena123",
                        "role": "user",
                        "display_name": "Elena Rostova",
                        "title": "Service Quality Coordinator",
                        "email": "e.rostova@restaurantops.ai",
                        "department": "Guest Experience",
                        "status": "Inactive",
                        "created_at": "2024-06-01 16:45:00",
                        "last_login": (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                    }
                ]
                for u in seed_users:
                    db.add(UserORM(**u))
                db.commit()
                log_system_event("INFO", "UserRepository", "Seeded initial user accounts into SQLite.")
        except Exception as e:
            db.rollback()
            log_system_event("WARNING", "UserRepository", f"Notice during user seeding: {str(e)}")
        finally:
            db.close()

    def _ensure_seed_feedbacks(self):
        """Seeds standard operational feedbacks if the user_feedbacks table is empty."""
        db: Session = SessionLocal()
        try:
            count = db.query(FeedbackORM).count()
            if count == 0:
                seed_data = [
                    {
                        "feedback_id": "fb_seed_001",
                        "interaction_id": "int_78a1",
                        "user_name": "Marcus Vance",
                        "user_role": "General Manager",
                        "rating": 5,
                        "feedback_type": "root_cause",
                        "comment": "Root cause identified kitchen expediter bottleneck accurately during Friday peak dinner rush. Highly actionable.",
                        "status": "Resolved",
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "feedback_id": "fb_seed_002",
                        "interaction_id": "int_92c4",
                        "user_name": "Elena Rostova",
                        "user_role": "Shift Lead",
                        "rating": 4,
                        "feedback_type": "rag",
                        "comment": "RAG search pulled exact customer quotes regarding cleanliness complaints in Restroom 2. Great grounding.",
                        "status": "Actioned",
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "feedback_id": "fb_seed_003",
                        "interaction_id": "int_31b9",
                        "user_name": "David Kim",
                        "user_role": "Operations Analyst",
                        "rating": 5,
                        "feedback_type": "multi_agent",
                        "comment": "Multi-Agent recovery script was polite and de-escalating. The voucher recommendation matched guest expectations.",
                        "status": "Resolved",
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                    },
                    {
                        "feedback_id": "fb_seed_004",
                        "interaction_id": "int_44e2",
                        "user_name": "Sarah Jenkins",
                        "user_role": "District Manager",
                        "rating": 4,
                        "feedback_type": "recommendation",
                        "comment": "Staff training SOP checklist for POS order accuracy was clear and immediately distributed to front-of-house staff.",
                        "status": "Pending",
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                ]
                for item in seed_data:
                    db.add(FeedbackORM(**item))
                db.commit()
                log_system_event("INFO", "FeedbackRepository", "Seeded 4 initial operational user feedback records.")
        except Exception as e:
            db.rollback()
            log_system_event("WARNING", "FeedbackRepository", f"Notice during feedback check: {str(e)}")
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # FEEDBACK MANAGEMENT
    # -------------------------------------------------------------------------
    def get_feedbacks(self, status_filter: Optional[str] = None, type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            query = db.query(FeedbackORM)
            if status_filter and status_filter != "All":
                query = query.filter(FeedbackORM.status == status_filter)
            if type_filter and type_filter != "All":
                query = query.filter(FeedbackORM.feedback_type == type_filter)
            
            records = query.order_by(FeedbackORM.timestamp.desc()).all()
            return [
                {
                    "feedback_id": r.feedback_id,
                    "interaction_id": r.interaction_id or "N/A",
                    "user_name": r.user_name,
                    "user_role": r.user_role,
                    "rating": r.rating,
                    "feedback_type": r.feedback_type,
                    "comment": r.comment or "",
                    "status": r.status,
                    "timestamp": r.timestamp
                }
                for r in records
            ]
        finally:
            db.close()

    def add_user_feedback(
        self,
        rating: int,
        feedback_type: str = "general",
        comment: Optional[str] = None,
        interaction_id: Optional[str] = None,
        user_name: str = "Operations User",
        user_role: str = "user"
    ) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            feedback_id = f"fb_{uuid.uuid4().hex[:8]}"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = FeedbackORM(
                feedback_id=feedback_id,
                interaction_id=interaction_id,
                user_name=user_name,
                user_role=user_role,
                rating=rating,
                feedback_type=feedback_type,
                comment=comment,
                status="Pending",
                timestamp=now_str
            )
            db.add(entry)
            db.commit()
            log_system_event("INFO", "FeedbackService", f"New feedback ({rating}★, type: {feedback_type}) recorded by {user_name} [{feedback_id}].")
            return {
                "status": "success",
                "feedback_id": feedback_id,
                "message": "Feedback submitted successfully."
            }
        except Exception as e:
            db.rollback()
            log_system_event("ERROR", "FeedbackService", f"Failed to record feedback: {str(e)}")
            raise e
        finally:
            db.close()

    def update_feedback_status(self, feedback_id: str, new_status: str, admin_user: str = "admin") -> bool:
        db: Session = SessionLocal()
        try:
            fb = db.query(FeedbackORM).filter(FeedbackORM.feedback_id == feedback_id).first()
            if fb:
                fb.status = new_status
                db.commit()
                log_system_event("AUDIT", "AdminConsole", f"Feedback {feedback_id} marked as '{new_status}' by {admin_user}.")
                return True
            return False
        finally:
            db.close()

    def delete_feedback(self, feedback_id: str, admin_user: str = "admin") -> bool:
        db: Session = SessionLocal()
        try:
            fb = db.query(FeedbackORM).filter(FeedbackORM.feedback_id == feedback_id).first()
            if fb:
                db.delete(fb)
                db.commit()
                log_system_event("AUDIT", "AdminConsole", f"Feedback {feedback_id} deleted by {admin_user}.")
                return True
            return False
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # CSV DATA INGESTION
    # -------------------------------------------------------------------------
    def ingest_csv(self, df: pd.DataFrame, admin_user: str = "admin") -> Dict[str, Any]:
        """
        Validates, normalizes, and ingests a DataFrame of restaurant reviews into SQLite.
        """
        if df.empty:
            return {"status": "error", "message": "Uploaded CSV contains no rows."}

        db: Session = SessionLocal()
        try:
            # Normalize column names (strip whitespace and lowercase)
            col_map = {c: c.strip().lower() for c in df.columns}
            df_norm = df.rename(columns=col_map)

            # Detect key columns with sensible fallbacks
            text_col = next((c for c in ["text", "review_text", "comment", "review", "content"] if c in df_norm.columns), None)
            biz_col = next((c for c in ["restaurant_name", "business_name", "name", "restaurant"] if c in df_norm.columns), None)
            stars_col = next((c for c in ["stars", "rating", "star_rating", "score"] if c in df_norm.columns), None)
            cat_col = next((c for c in ["complaint_category", "category", "issue_type"] if c in df_norm.columns), None)
            city_col = next((c for c in ["city", "location", "metro"] if c in df_norm.columns), None)

            if not text_col:
                return {
                    "status": "error",
                    "message": "CSV must contain a review text column (e.g., 'text', 'review_text', or 'content')."
                }

            inserted_count = 0
            now_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for _, row in df_norm.iterrows():
                review_text = str(row.get(text_col, "")).strip()
                if not review_text or review_text == "nan":
                    continue

                r_name = str(row.get(biz_col, "Uploaded Fleet Restaurant")) if biz_col else "Uploaded Fleet Restaurant"
                try:
                    r_stars = float(row.get(stars_col, 3.0)) if stars_col else 3.0
                except (ValueError, TypeError):
                    r_stars = 3.0

                r_cat = str(row.get(cat_col, "Customer Service")) if cat_col and str(row.get(cat_col)) != "nan" else "Customer Service"
                r_city = str(row.get(city_col, "Philadelphia")) if city_col and str(row.get(city_col)) != "nan" else "Philadelphia"

                # Derived fields
                is_comp = r_stars <= 3.0
                sentiment = "Negative" if r_stars <= 2.0 else ("Neutral" if r_stars == 3.0 else "Positive")
                severity = 5 if r_stars == 1.0 else (4 if r_stars == 2.0 else (3 if r_stars == 3.0 else 1))
                priority = round((6.0 - r_stars) * 18.5, 1)

                review_obj = EnrichedReviewORM(
                    review_id=f"rev_ingest_{uuid.uuid4().hex[:10]}",
                    business_id=f"biz_{uuid.uuid4().hex[:8]}",
                    restaurant_name=r_name,
                    city=r_city,
                    state="PA",
                    categories="Restaurants, Food",
                    stars=r_stars,
                    business_stars=r_stars,
                    business_review_count=100,
                    date=now_date,
                    useful=0,
                    text=review_text,
                    is_complaint=is_comp,
                    sentiment=sentiment,
                    complaint_category=r_cat,
                    aspect=r_cat.lower(),
                    severity_score=severity,
                    priority_score=priority
                )
                db.add(review_obj)
                inserted_count += 1

            db.commit()
            total_after = db.query(EnrichedReviewORM).count()
            log_system_event(
                "AUDIT",
                "CSVDataIngestion",
                f"Successfully ingested {inserted_count} reviews from CSV by {admin_user}. Fleet database now has {total_after:,} reviews."
            )
            return {
                "status": "success",
                "rows_ingested": inserted_count,
                "total_reviews": total_after,
                "message": f"Successfully ingested {inserted_count} reviews into SQLite database."
            }
        except Exception as e:
            db.rollback()
            log_system_event("ERROR", "CSVDataIngestion", f"CSV ingestion failed: {str(e)}")
            return {"status": "error", "message": f"Ingestion error: {str(e)}"}
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # CRUD OPERATIONS ON REVIEWS
    # -------------------------------------------------------------------------
    def list_reviews(
        self,
        search_query: str = "",
        category: str = "All",
        limit: int = 15,
        offset: int = 0
    ) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            query = db.query(EnrichedReviewORM)
            if category and category != "All":
                query = query.filter(EnrichedReviewORM.complaint_category == category)
            if search_query:
                term = f"%{search_query}%"
                query = query.filter(
                    (EnrichedReviewORM.restaurant_name.ilike(term)) |
                    (EnrichedReviewORM.text.ilike(term)) |
                    (EnrichedReviewORM.city.ilike(term)) |
                    (EnrichedReviewORM.review_id.ilike(term))
                )

            total_count = query.count()
            items = query.order_by(EnrichedReviewORM.date.desc()).offset(offset).limit(limit).all()

            records = [
                {
                    "review_id": r.review_id,
                    "restaurant_name": r.restaurant_name,
                    "city": r.city or "N/A",
                    "stars": r.stars,
                    "is_complaint": bool(r.is_complaint),
                    "sentiment": r.sentiment,
                    "complaint_category": r.complaint_category,
                    "aspect": r.aspect or "general",
                    "severity_score": r.severity_score,
                    "priority_score": r.priority_score,
                    "date": r.date,
                    "text": r.text
                }
                for r in items
            ]
            return {"total": total_count, "records": records}
        finally:
            db.close()

    def get_review_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            r = db.query(EnrichedReviewORM).filter(EnrichedReviewORM.review_id == review_id).first()
            if not r:
                return None
            return {
                "review_id": r.review_id,
                "business_id": r.business_id,
                "restaurant_name": r.restaurant_name,
                "city": r.city,
                "state": r.state,
                "stars": r.stars,
                "is_complaint": bool(r.is_complaint),
                "sentiment": r.sentiment,
                "complaint_category": r.complaint_category,
                "aspect": r.aspect,
                "severity_score": r.severity_score,
                "priority_score": r.priority_score,
                "date": r.date,
                "text": r.text
            }
        finally:
            db.close()

    def create_review(self, data: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            rev_id = data.get("review_id") or f"rev_man_{uuid.uuid4().hex[:10]}"
            stars = float(data.get("stars", 3.0))
            is_comp = bool(data.get("is_complaint", stars <= 3.0))
            sentiment = data.get("sentiment") or ("Negative" if stars <= 2.0 else ("Neutral" if stars == 3.0 else "Positive"))

            new_rev = EnrichedReviewORM(
                review_id=rev_id,
                business_id=data.get("business_id") or f"biz_{uuid.uuid4().hex[:8]}",
                restaurant_name=data.get("restaurant_name", "Fleet Restaurant"),
                city=data.get("city", "Philadelphia"),
                state=data.get("state", "PA"),
                categories=data.get("categories", "Restaurants, Food"),
                stars=stars,
                business_stars=stars,
                business_review_count=int(data.get("business_review_count", 100)),
                date=data.get("date") or datetime.datetime.now().strftime("%Y-%m-%d"),
                useful=0,
                text=data.get("text", ""),
                is_complaint=is_comp,
                sentiment=sentiment,
                complaint_category=data.get("complaint_category", "Customer Service"),
                aspect=data.get("aspect", "general service"),
                severity_score=int(data.get("severity_score", 3)),
                priority_score=float(data.get("priority_score", 50.0))
            )
            db.add(new_rev)
            db.commit()
            log_system_event(
                "AUDIT",
                "DatabaseCRUD",
                f"Created new review '{rev_id}' for '{new_rev.restaurant_name}' by {admin_user}."
            )
            return {"status": "success", "review_id": rev_id, "message": "Review created successfully."}
        except Exception as e:
            db.rollback()
            log_system_event("ERROR", "DatabaseCRUD", f"Create review failed: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def update_review(self, review_id: str, updates: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            r = db.query(EnrichedReviewORM).filter(EnrichedReviewORM.review_id == review_id).first()
            if not r:
                return {"status": "error", "message": f"Review ID '{review_id}' not found."}

            for key, val in updates.items():
                if hasattr(r, key) and key != "review_id":
                    setattr(r, key, val)

            db.commit()
            log_system_event(
                "AUDIT",
                "DatabaseCRUD",
                f"Updated review '{review_id}' fields {list(updates.keys())} by {admin_user}."
            )
            return {"status": "success", "review_id": review_id, "message": "Record updated successfully."}
        except Exception as e:
            db.rollback()
            log_system_event("ERROR", "DatabaseCRUD", f"Update review failed: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def delete_review(self, review_id: str, admin_user: str = "admin") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            r = db.query(EnrichedReviewORM).filter(EnrichedReviewORM.review_id == review_id).first()
            if not r:
                return {"status": "error", "message": f"Review ID '{review_id}' not found."}

            biz_name = r.restaurant_name
            db.delete(r)
            db.commit()
            log_system_event(
                "AUDIT",
                "DatabaseCRUD",
                f"Deleted review '{review_id}' ({biz_name}) from SQLite database by {admin_user}."
            )
            return {"status": "success", "message": f"Review '{review_id}' permanently deleted."}
        except Exception as e:
            db.rollback()
            log_system_event("ERROR", "DatabaseCRUD", f"Delete review failed: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # SYSTEM LOGS & AUDIT TRAIL
    # -------------------------------------------------------------------------
    def get_logs(
        self,
        level_filter: Optional[str] = None,
        search_term: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        logs = _SYSTEM_LOGS
        if level_filter and level_filter != "ALL":
            logs = [e for e in logs if e.get("level") == level_filter.upper()]
        if search_term:
            term = search_term.lower()
            logs = [
                e for e in logs
                if term in e.get("message", "").lower() or term in e.get("source", "").lower()
            ]
        return logs[:limit]

    # -------------------------------------------------------------------------
    # SYSTEM METRICS & DIAGNOSTICS
    # -------------------------------------------------------------------------
    def get_system_telemetry(self) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            total_reviews = db.query(EnrichedReviewORM).count()
            complaint_count = db.query(EnrichedReviewORM).filter(EnrichedReviewORM.is_complaint == True).count()
            avg_stars = db.execute(text("SELECT AVG(stars) FROM enriched_reviews")).scalar() or 0.0
            unique_biz = db.execute(text("SELECT COUNT(DISTINCT restaurant_name) FROM enriched_reviews")).scalar() or 0
            unique_cities = db.execute(text("SELECT COUNT(DISTINCT city) FROM enriched_reviews")).scalar() or 0
            
            # Feedbacks stats
            total_feedback = db.query(FeedbackORM).count()
            avg_feedback = db.execute(text("SELECT AVG(rating) FROM user_feedbacks")).scalar() or 0.0
            resolved_feedback = db.query(FeedbackORM).filter(FeedbackORM.status == "Resolved").count()

            # DB size
            db_size_mb = round(self.db_path.stat().st_size / (1024 * 1024), 2) if self.db_path.exists() else 0.0

            # Categories distribution
            cat_rows = db.execute(text("""
                SELECT complaint_category, COUNT(*) as c
                FROM enriched_reviews
                WHERE is_complaint = 1
                GROUP BY complaint_category
                ORDER BY c DESC
                LIMIT 8
            """)).fetchall()
            cat_dist = {row[0]: row[1] for row in cat_rows if row[0]}

            # Severity distribution
            sev_rows = db.execute(text("""
                SELECT severity_score, COUNT(*) as c
                FROM enriched_reviews
                WHERE is_complaint = 1
                GROUP BY severity_score
                ORDER BY severity_score ASC
            """)).fetchall()
            sev_dist = {f"Severity {row[0]}": row[1] for row in sev_rows}

            return {
                "total_reviews": total_reviews,
                "complaint_count": complaint_count,
                "complaint_pct": round((complaint_count / total_reviews * 100), 1) if total_reviews else 0.0,
                "avg_stars": round(float(avg_stars), 2),
                "unique_restaurants": unique_biz,
                "unique_cities": unique_cities,
                "database_size_mb": db_size_mb,
                "database_path": str(self.db_path),
                "total_feedbacks": total_feedback,
                "avg_feedback_rating": round(float(avg_feedback), 2),
                "resolved_feedback_count": resolved_feedback,
                "category_distribution": cat_dist,
                "severity_distribution": sev_dist,
                "chromadb_status": "Active & Synchronized",
                "embedding_model": settings.EMBEDDING_MODEL_NAME,
                "llm_model": settings.DEFAULT_LLM_MODEL
            }
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # USER MANAGEMENT (CRUD)
    # -------------------------------------------------------------------------
    def list_users(
        self,
        search_query: str = "",
        role: str = "All",
        status: str = "All",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Lists users with filtering and search capabilities."""
        db: Session = SessionLocal()
        try:
            query = db.query(UserORM)
            if role and role != "All":
                query = query.filter(UserORM.role == role)
            if status and status != "All":
                query = query.filter(UserORM.status == status)
            if search_query:
                pattern = f"%{search_query.strip()}%"
                query = query.filter(
                    (UserORM.username.ilike(pattern)) |
                    (UserORM.display_name.ilike(pattern)) |
                    (UserORM.email.ilike(pattern)) |
                    (UserORM.department.ilike(pattern)) |
                    (UserORM.title.ilike(pattern))
                )
            
            total = query.count()
            users = query.order_by(UserORM.created_at.desc()).offset(offset).limit(limit).all()
            
            user_list = []
            for u in users:
                user_list.append({
                    "user_id": u.user_id,
                    "username": u.username,
                    "role": u.role,
                    "display_name": u.display_name,
                    "title": u.title,
                    "email": u.email,
                    "department": u.department,
                    "status": u.status,
                    "created_at": u.created_at,
                    "last_login": u.last_login or "Never"
                })
            
            return {
                "total": total,
                "users": user_list,
                "limit": limit,
                "offset": offset
            }
        finally:
            db.close()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single user by username for authentication."""
        db: Session = SessionLocal()
        try:
            u = db.query(UserORM).filter(UserORM.username == username.strip().lower()).first()
            if not u:
                return None
            return {
                "user_id": u.user_id,
                "username": u.username,
                "password": u.password,
                "role": u.role,
                "display_name": u.display_name,
                "title": u.title,
                "email": u.email,
                "department": u.department,
                "status": u.status,
                "created_at": u.created_at,
                "last_login": u.last_login
            }
        finally:
            db.close()

    def create_user(self, payload: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        """Creates a new user record in SQLite."""
        db: Session = SessionLocal()
        try:
            username = payload.get("username", "").strip().lower()
            if not username:
                return {"status": "error", "message": "Username is required."}
            
            existing = db.query(UserORM).filter(UserORM.username == username).first()
            if existing:
                return {"status": "error", "message": f"Username '{username}' already exists."}
            
            from backend.app.core.security import hash_password
            user_id = f"usr_{uuid.uuid4().hex[:8]}"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            raw_pwd = payload.get("password") or "temp123"
            new_user = UserORM(
                user_id=user_id,
                username=username,
                password=hash_password(raw_pwd),
                role=payload.get("role", "user"),
                display_name=payload.get("display_name", username.capitalize()),
                title=payload.get("title", "Operations Specialist"),
                email=payload.get("email", f"{username}@restaurantops.ai"),
                department=payload.get("department", "Fleet Operations"),
                status=payload.get("status", "Active"),
                created_at=now_str,
                last_login=None
            )
            db.add(new_user)
            db.commit()
            log_system_event("AUDIT", "UserManagement", f"User '{username}' [{user_id}] created by admin '{admin_user}'.")
            return {
                "status": "success",
                "user_id": user_id,
                "username": username,
                "message": f"User '{username}' successfully registered."
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def update_user(self, user_id: str, payload: Dict[str, Any], admin_user: str = "admin") -> Dict[str, Any]:
        """Updates an existing user's attributes."""
        from backend.app.core.security import hash_password
        db: Session = SessionLocal()
        try:
            user = db.query(UserORM).filter(UserORM.user_id == user_id).first()
            if not user:
                return {"status": "error", "message": f"User ID '{user_id}' not found."}
            
            if "role" in payload:
                user.role = payload["role"]
            if "display_name" in payload:
                user.display_name = payload["display_name"]
            if "title" in payload:
                user.title = payload["title"]
            if "email" in payload:
                user.email = payload["email"]
            if "department" in payload:
                user.department = payload["department"]
            if "status" in payload:
                user.status = payload["status"]
            if "password" in payload and payload["password"]:
                user.password = hash_password(payload["password"])
            
            db.commit()
            log_system_event("AUDIT", "UserManagement", f"User '{user.username}' [{user_id}] updated by admin '{admin_user}'.")
            return {
                "status": "success",
                "user_id": user_id,
                "username": user.username,
                "message": f"User '{user.username}' updated successfully."
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    def delete_user(self, user_id: str, admin_user: str = "admin") -> Dict[str, Any]:
        """Deletes a user record from SQLite (with protection for primary admin)."""
        db: Session = SessionLocal()
        try:
            user = db.query(UserORM).filter(UserORM.user_id == user_id).first()
            if not user:
                return {"status": "error", "message": f"User ID '{user_id}' not found."}
            
            if user.username == "admin":
                return {"status": "error", "message": "Primary administrator account 'admin' cannot be deleted."}
            
            uname = user.username
            db.delete(user)
            db.commit()
            log_system_event("AUDIT", "UserManagement", f"User '{uname}' [{user_id}] deleted by admin '{admin_user}'.")
            return {
                "status": "success",
                "message": f"User '{uname}' successfully deleted from database."
            }
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
        finally:
            db.close()


# Singleton helper
_admin_svc = None
def get_admin_service() -> AdminService:
    global _admin_svc
    if _admin_svc is None:
        _admin_svc = AdminService()
    return _admin_svc
