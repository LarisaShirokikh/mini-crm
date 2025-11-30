from fastapi import APIRouter

from app.api.v1.endpoints import (
    activities_router,
    analytics_router,
    auth_router,
    contacts_router,
    deals_router,
    organizations_router,
    tasks_router,
)

api_router = APIRouter()

# Auth routes (no org context required)
api_router.include_router(auth_router)

# Organization routes
api_router.include_router(organizations_router)

# Resource routes (require org context via X-Organization-Id header)
api_router.include_router(contacts_router)
api_router.include_router(deals_router)
api_router.include_router(tasks_router)
api_router.include_router(activities_router)

# Analytics routes
api_router.include_router(analytics_router)