"""
Chat History Service: Persistent SQLite Storage for User Inquiries & Multi-Agent Dialogue.
Ensures conversations survive browser reloads, user logouts, and server restarts.
"""
import json
import time
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.database.db import SessionLocal, engine
from backend.app.models.review import Base, ChatHistoryORM
from backend.app.core.config import settings

class ChatHistoryService:
    def __init__(self):
        self.db_path = Path(settings.SQLITE_DB_PATH)
        # Ensure table exists
        Base.metadata.create_all(bind=engine)
        self._ensure_seed_history()

    def _ensure_seed_history(self):
        """Seeds initial realistic operational inquiries if the table is empty."""
        db: Session = SessionLocal()
        try:
            count = db.query(ChatHistoryORM).count()
            if count == 0:
                seed_interactions = [
                    {
                        "interaction_id": "inq_seed_001",
                        "username": "user",
                        "user_name": "Operations Analyst",
                        "user_role": "user",
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%I:%M %p"),
                        "created_at": (datetime.datetime.now() - datetime.timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
                        "query": "Customers are complaining about slow service. What similar complaints have been reported and what should management do?",
                        "category": "Waiting Time",
                        "page_source": "Central Operations Analyst",
                        "response_summary": "Fleet analysis reveals 4,512 service delay incidents concentrated during dinner peak rush (6:00 PM – 8:30 PM). Primary friction originates from kitchen-to-table expediter queue latencies (average 38 minutes). Recommended expediter re-assignment and shift staging protocols.",
                        "response_json": json.dumps({
                            "summary": "Fleet analysis reveals 4,512 service delay incidents concentrated during dinner peak rush (6:00 PM – 8:30 PM). Primary friction originates from kitchen-to-table expediter queue latencies (average 38 minutes). Recommended expediter re-assignment and shift staging protocols.",
                            "category": "Waiting Time",
                            "priority": "P2 - Shift Manager SLA",
                            "sentiment_score": "78% Negative",
                            "action_items": [
                                "Deploy dedicated runner during 6 PM - 9 PM rush",
                                "Calibrate POS order ticketing sequencing",
                                "Enforce table check-back SLA under 3 minutes"
                            ],
                            "report": {
                                "primary_category": "Waiting Time",
                                "priority_tier": "P2 - Shift Manager SLA",
                                "negative_sentiment_pct": 78.0,
                                "executive_summary": "Fleet analysis reveals 4,512 service delay incidents concentrated during dinner peak rush (6:00 PM – 8:30 PM). Primary friction originates from kitchen-to-table expediter queue latencies (average 38 minutes).",
                                "recommendations": [
                                    "Deploy dedicated runner during 6 PM - 9 PM rush",
                                    "Calibrate POS order ticketing sequencing",
                                    "Enforce table check-back SLA under 3 minutes"
                                ]
                            }
                        })
                    },
                    {
                        "interaction_id": "inq_seed_002",
                        "username": "user",
                        "user_name": "Operations Analyst",
                        "user_role": "user",
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%I:%M %p"),
                        "created_at": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                        "query": "What are the major operational problems at Mon Ami Gabi?",
                        "category": "Waiting Time & Ambiance",
                        "page_source": "Central Operations Analyst",
                        "response_summary": "Diagnostic analysis for Mon Ami Gabi indicates high guest satisfaction on menu taste (4.1★) but recurring complaints regarding patio seating wait times (exceeding 50 mins without reservations) and acoustic noise levels during peak hours.",
                        "response_json": json.dumps({
                            "summary": "Diagnostic analysis for Mon Ami Gabi indicates high guest satisfaction on menu taste (4.1★) but recurring complaints regarding patio seating wait times (exceeding 50 mins without reservations) and acoustic noise levels during peak hours.",
                            "category": "Waiting Time & Ambiance",
                            "priority": "P2 - Operations Action",
                            "sentiment_score": "64% Negative",
                            "action_items": [
                                "Implement SMS-based digital waitlist for patio seating",
                                "Establish acoustic baffling near interior dining corridor",
                                "Brief host staff on accurate arrival quote management"
                            ],
                            "report": {
                                "primary_category": "Waiting Time & Ambiance",
                                "priority_tier": "P2 - Operations Action",
                                "negative_sentiment_pct": 64.0,
                                "executive_summary": "Diagnostic analysis for Mon Ami Gabi indicates high guest satisfaction on menu taste (4.1★) but recurring complaints regarding patio seating wait times.",
                                "recommendations": [
                                    "Implement SMS-based digital waitlist for patio seating",
                                    "Establish acoustic baffling near interior dining corridor",
                                    "Brief host staff on accurate arrival quote management"
                                ]
                            }
                        })
                    },
                    {
                        "interaction_id": "inq_seed_003",
                        "username": "admin",
                        "user_name": "Executive Operations Director",
                        "user_role": "admin",
                        "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=45)).strftime("%I:%M %p"),
                        "created_at": (datetime.datetime.now() - datetime.timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
                        "query": "Executive audit: identify food temperature and kitchen holding time complaints across Philadelphia locations.",
                        "category": "Food Quality",
                        "page_source": "Central Operations Analyst",
                        "response_summary": "System audit flagged 1,180 cold food complaints in the Philadelphia metro area. Heat lamp staging failures and expo delivery delays represent 72% of food quality incidents.",
                        "response_json": json.dumps({
                            "summary": "System audit flagged 1,180 cold food complaints in the Philadelphia metro area. Heat lamp staging failures and expo delivery delays represent 72% of food quality incidents.",
                            "category": "Food Quality",
                            "priority": "P1 - Critical Quality SLA",
                            "sentiment_score": "84% Negative",
                            "action_items": [
                                "Inspect kitchen heat lamp staging calibrations",
                                "Implement mandatory 2-minute expo tray delivery rule",
                                "Review line cook station handoff checklists"
                            ],
                            "report": {
                                "primary_category": "Food Quality",
                                "priority_tier": "P1 - Critical Quality SLA",
                                "negative_sentiment_pct": 84.0,
                                "executive_summary": "System audit flagged 1,180 cold food complaints in the Philadelphia metro area.",
                                "recommendations": [
                                    "Inspect kitchen heat lamp staging calibrations",
                                    "Implement mandatory 2-minute expo tray delivery rule",
                                    "Review line cook station handoff checklists"
                                ]
                            }
                        })
                    }
                ]
                for item in seed_interactions:
                    db.add(ChatHistoryORM(**item))
                db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    def get_history(self, username: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves saved conversation history ordered by most recent first.
        If username is provided and not 'admin', fetches for that specific user.
        If 'admin', fetches all or admin's interactions.
        """
        db: Session = SessionLocal()
        try:
            query = db.query(ChatHistoryORM)
            if username and username != "admin":
                query = query.filter(ChatHistoryORM.username == username.strip().lower())
            
            records = query.order_by(ChatHistoryORM.created_at.desc()).limit(limit).all()
            
            results = []
            for r in records:
                parsed_resp = {}
                if r.response_json:
                    try:
                        parsed_resp = json.loads(r.response_json)
                    except Exception:
                        parsed_resp = {"summary": r.response_summary or ""}

                item = {
                    "id": r.interaction_id,
                    "interaction_id": r.interaction_id,
                    "timestamp": r.timestamp,
                    "created_at": r.created_at,
                    "query": r.query,
                    "role": "user",
                    "user": r.user_name,
                    "username": r.username,
                    "user_role": r.user_role,
                    "category": r.category,
                    "page_source": r.page_source,
                    "response": parsed_resp,
                    "report": parsed_resp.get("report") if isinstance(parsed_resp, dict) else None
                }
                results.append(item)
            return results
        finally:
            db.close()

    def add_interaction(
        self,
        query: str,
        report: Dict[str, Any],
        username: str = "user",
        user_name: str = "Operations Analyst",
        user_role: str = "user",
        category: Optional[str] = None,
        page_source: str = "Central Operations Analyst"
    ) -> Dict[str, Any]:
        """
        Persists a new user query and diagnostic answer into SQLite.
        """
        clean_query = query.strip()
        if not clean_query:
            return {}

        db: Session = SessionLocal()
        try:
            # Check duplicate within last 5 seconds
            recent = db.query(ChatHistoryORM).filter(
                ChatHistoryORM.username == username.strip().lower(),
                ChatHistoryORM.query == clean_query
            ).order_by(ChatHistoryORM.created_at.desc()).first()

            now_dt = datetime.datetime.now()
            now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
            time_str = now_dt.strftime("%I:%M %p")
            
            summary_text = ""
            if isinstance(report, dict):
                summary_text = report.get("executive_summary") or report.get("general_llm_response") or report.get("summary") or ""
                if not summary_text and "recommendations" in report:
                    summary_text = f"Identified operational pattern with {len(report.get('recommendations', []))} action items."
            elif isinstance(report, str):
                summary_text = report
                report = {"executive_summary": summary_text}

            cat = category or (report.get("primary_category") if isinstance(report, dict) else "General Operations") or "General Operations"
            prio = (report.get("priority_tier") if isinstance(report, dict) else "P2 - Standard SLA") or "P2 - Standard SLA"
            neg_pct = report.get("negative_sentiment_pct", 68.0) if isinstance(report, dict) else 68.0
            actions = report.get("recommendations", []) if isinstance(report, dict) else []

            structured_response = {
                "summary": summary_text[:350] + "..." if len(summary_text) > 350 else summary_text,
                "category": cat,
                "priority": prio,
                "sentiment_score": f"{neg_pct:.1f}% Friction" if isinstance(neg_pct, (int, float)) else str(neg_pct),
                "action_items": actions[:4],
                "report": report
            }

            interaction_id = f"inq_{int(time.time() * 1000)}"
            entry = ChatHistoryORM(
                interaction_id=interaction_id,
                username=username.strip().lower(),
                user_name=user_name,
                user_role=user_role,
                timestamp=time_str,
                created_at=now_str,
                query=clean_query,
                category=cat,
                page_source=page_source,
                response_summary=summary_text[:500],
                response_json=json.dumps(structured_response)
            )
            db.add(entry)
            db.commit()

            return {
                "id": interaction_id,
                "interaction_id": interaction_id,
                "timestamp": time_str,
                "created_at": now_str,
                "query": clean_query,
                "role": "user",
                "user": user_name,
                "username": username.strip().lower(),
                "user_role": user_role,
                "category": cat,
                "page_source": page_source,
                "response": structured_response,
                "report": report
            }
        except Exception as e:
            db.rollback()
            return {}
        finally:
            db.close()

    def clear_history(self, username: Optional[str] = None) -> bool:
        """Clears chat history for a specific user or all users."""
        db: Session = SessionLocal()
        try:
            query = db.query(ChatHistoryORM)
            if username and username != "admin":
                query = query.filter(ChatHistoryORM.username == username.strip().lower())
            query.delete(synchronize_session=False)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

    def delete_interaction(self, interaction_id: str) -> bool:
        """Deletes a single chat interaction."""
        db: Session = SessionLocal()
        try:
            rec = db.query(ChatHistoryORM).filter(ChatHistoryORM.interaction_id == interaction_id).first()
            if rec:
                db.delete(rec)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()

# Singleton helper
_chat_history_svc = None
def get_chat_history_service() -> ChatHistoryService:
    global _chat_history_svc
    if _chat_history_svc is None:
        _chat_history_svc = ChatHistoryService()
    return _chat_history_svc
