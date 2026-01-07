"""
Supabase Database Client
Provides database connection and query methods for the loan approval system
"""

import os
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Singleton Supabase client"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client with environment variables"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for backend
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables"
            )
        
        try:
            self._client = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Get the Supabase client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    # ============================================
    # USER METHODS
    # ============================================
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            response = self.client.table("users").select("*").eq("email", email).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            response = self.client.table("users").insert(user_data).execute()
            logger.info(f"✅ User created: {user_data['email']}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    # ============================================
    # APPLICANT METHODS
    # ============================================
    
    def get_applicants(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Get paginated applicants list"""
        try:
            query = self.client.table("applicants").select(
                "*", count="exact"
            )
            
            # Filter by status if provided
            if status:
                query = query.eq("status", status)
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size - 1
            query = query.range(start, end).order("created_at", desc=True)
            
            response = query.execute()
            
            return {
                "data": response.data,
                "total": response.count,
                "page": page,
                "page_size": page_size,
                "total_pages": (response.count + page_size - 1) // page_size if response.count else 0
            }
        except Exception as e:
            logger.error(f"Error getting applicants: {e}")
            return {"data": [], "total": 0, "page": page, "page_size": page_size, "total_pages": 0}
    
    def get_applicant_by_id(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """Get applicant by ID"""
        try:
            response = self.client.table("applicants").select("*").eq("id", applicant_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting applicant: {e}")
            return None
    
    def create_applicant(self, applicant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new applicant"""
        try:
            response = self.client.table("applicants").insert(applicant_data).execute()
            logger.info(f"✅ Applicant created: {applicant_data.get('name')}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating applicant: {e}")
            return None
    
    def update_applicant(self, applicant_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update applicant"""
        try:
            response = self.client.table("applicants").update(update_data).eq("id", applicant_id).execute()
            logger.info(f"✅ Applicant updated: {applicant_id}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating applicant: {e}")
            return None
    
    def approve_applicant(
        self,
        applicant_id: str,
        approved_by: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Approve an applicant"""
        update_data = {
            "status": "approved",
            "approved_by": approved_by,
            "approved_at": "now()",
            "notes": notes
        }
        return self.update_applicant(applicant_id, update_data)
    
    def reject_applicant(
        self,
        applicant_id: str,
        rejected_by: str,
        reason: str
    ) -> Optional[Dict[str, Any]]:
        """Reject an applicant"""
        update_data = {
            "status": "rejected",
            "rejected_by": rejected_by,
            "rejected_at": "now()",
            "rejection_reason": reason
        }
        return self.update_applicant(applicant_id, update_data)
    
    # ============================================
    # PREDICTION METHODS
    # ============================================
    
    def create_prediction(self, prediction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new prediction"""
        try:
            response = self.client.table("predictions").insert(prediction_data).execute()
            logger.info(f"✅ Prediction created for applicant: {prediction_data['applicant_id']}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            return None
    
    def get_prediction_by_applicant(self, applicant_id: str) -> Optional[Dict[str, Any]]:
        """Get latest prediction for an applicant"""
        try:
            response = (
                self.client.table("predictions")
                .select("*")
                .eq("applicant_id", applicant_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting prediction: {e}")
            return None
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent predictions"""
        try:
            response = (
                self.client.from_("recent_predictions")  # Using view
                .select("*")
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting recent predictions: {e}")
            return []
    
    # ============================================
    # DASHBOARD METHODS
    # ============================================
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        try:
            response = self.client.from_("dashboard_stats").select("*").single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {}
    
    # ============================================
    # AUDIT LOG METHODS
    # ============================================
    
    def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log an action to audit logs"""
        try:
            log_data = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details,
                "ip_address": ip_address,
                "user_agent": user_agent
            }
            self.client.table("audit_logs").insert(log_data).execute()
        except Exception as e:
            logger.error(f"Error logging action: {e}")
    
    # ============================================
    # MODEL PERFORMANCE METHODS
    # ============================================
    
    def save_model_performance(
        self,
        model_version: str,
        metrics: Dict[str, float]
    ) -> None:
        """Save model performance metrics"""
        try:
            for metric_name, metric_value in metrics.items():
                metric_data = {
                    "model_version": model_version,
                    "metric_name": metric_name,
                    "metric_value": metric_value
                }
                self.client.table("model_performance").insert(metric_data).execute()
            logger.info(f"✅ Model performance saved: {model_version}")
        except Exception as e:
            logger.error(f"Error saving model performance: {e}")
    
    def get_model_performance(
        self,
        model_version: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get model performance over time"""
        try:
            response = (
                self.client.table("model_performance")
                .select("*")
                .eq("model_version", model_version)
                .gte("date", f"now() - interval '{days} days'")
                .order("date", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting model performance: {e}")
            return []


# Create singleton instance
db = SupabaseClient()
