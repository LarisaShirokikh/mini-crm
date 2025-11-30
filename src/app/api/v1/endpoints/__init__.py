
from app.api.v1.endpoints.activities import router as activities_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.contacts import router as contacts_router
from app.api.v1.endpoints.deals import router as deals_router
from app.api.v1.endpoints.organizations import router as organizations_router
from app.api.v1.endpoints.tasks import router as tasks_router

__all__ = [
    "activities_router",
    "analytics_router",
    "auth_router",
    "contacts_router",
    "deals_router",
    "organizations_router",
    "tasks_router",
]