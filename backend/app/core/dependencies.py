from app.services.interfaces.ai_provider import AIProvider
from app.services.impl.gemini_provider import GeminiProvider
from app.services.interfaces.jsearch_service import JSearchService
from app.services.impl.jsearch_service_impl import JSearchServiceImpl
from app.services.interfaces.storage_service import StorageService
from app.services.impl.r2_storage_service import R2StorageService

# Singletons or instantiation functions
_ai_provider = GeminiProvider()
_jsearch_service = JSearchServiceImpl()
_storage_service = R2StorageService()

def get_ai_provider() -> AIProvider:
    return _ai_provider

def get_jsearch_service() -> JSearchService:
    return _jsearch_service

def get_storage_service() -> StorageService:
    return _storage_service
