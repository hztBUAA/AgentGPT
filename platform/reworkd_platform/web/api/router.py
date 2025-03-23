from fastapi.routing import APIRouter

from reworkd_platform.web.api import agent, auth, metadata, models, monitoring
from reworkd_platform.web.api import anonymous_agent

api_router = APIRouter()
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(anonymous_agent.router, prefix="/anonymous-agent", tags=["anonymous-agent"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
