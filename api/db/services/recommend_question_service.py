from api.db.db_models import RecommendQuestion
from datetime import datetime

from peewee import fn

from api.db import StatusEnum, TenantPermission
from api.db.db_models import DB, Document, Knowledgebase, Tenant, User, UserTenant, RecommendQuestion
from api.db.services.common_service import CommonService
from api.utils import current_timestamp, datetime_format

class RecommendQuestionService(CommonService):
    model = RecommendQuestion

    @classmethod
    @DB.connection_context()
    def get_list(cls, page_number, items_per_page,
                 orderby, desc, tenant_id, sys_code, app_code, user_code,recommendquestion_id ):
                       
        recommendquestions = cls.model.select()
        if recommendquestion_id:
            recommendquestions = recommendquestions.where(
                cls.model.id == recommendquestion_id)
        if app_code:
            recommendquestions = recommendquestions.where(
                cls.model.app_code == app_code
            )
        if user_code:
            recommendquestions = recommendquestions.where(
                cls.model.user_code == user_code 
            )
        if sys_code:
            recommendquestions = recommendquestions.where(
                cls.model.sys_code == sys_code  
            )
        if tenant_id:
            recommendquestions = recommendquestions.where(
                cls.model.tenant_id == tenant_id  
            )
        if desc:
            recommendquestions = recommendquestions.order_by(cls.model.getter_by(orderby).desc())
        else:
            recommendquestions = recommendquestions.order_by(cls.model.getter_by(orderby).asc())

        count = recommendquestions.count()
        recommendquestions = recommendquestions.paginate(page_number, items_per_page)
        return list(recommendquestions.dicts()), count

    @classmethod
    @DB.connection_context()
    def get_recommendquestion_ids(cls, tenant_id):
        # Get all knowledge base IDs for a tenant
        # Args:
        #     tenant_id: Tenant ID
        # Returns:
        #     List of knowledge base IDs
        fields = [
            cls.model.id,
        ]
        recommendquestions = cls.model.select(*fields).where(cls.model.tenant_id == tenant_id)
        recommendquestion_ids = [recommendquestion.id for recommendquestion in recommendquestions]
        return recommendquestion_ids

    @classmethod
    @DB.connection_context()
    def get_detail(cls, recommendquestion_id):
        # Get detailed information about a knowledge base
        # Args:
        #     recommendquestion_id: Knowledge base ID
        # Returns:
        #     Dictionary containing knowledge base details
        fields = [
            cls.model.id,
            cls.model.question,
            cls.model.sys_code,
            cls.model.app_code,
            cls.model.user_code,
            cls.model.tenant_id,
            cls.model.valid
            ]
        recommendquestions = cls.model.select(*fields).join(Tenant, on=(
            (Tenant.id == cls.model.tenant_id) & (Tenant.status == StatusEnum.VALID.value))).where(
            (cls.model.id == recommendquestion_id),
            (cls.model.status == StatusEnum.VALID.value)
        )
        if not recommendquestions:
            return
        d = recommendquestions[0].to_dict()
        return d
