#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import logging

from flask import request
from api import settings
from api.db import StatusEnum
from api.db.services.dialog_service import DialogService
from api.db.services.recommend_question_service import RecommendQuestionService
from api.db.services.llm_service import TenantLLMService
from api.db.services.user_service import TenantService
from api.utils import get_uuid
from api.utils.api_utils import server_error_response, get_data_error_result, token_required, get_json_result, validate_request
from api.utils.api_utils import get_result

@manager.route('/questions', methods=['GET'])
@token_required
def get_recommendquestions(tenant_id):
    req = request.json
    try:
        user_code = request.args.get("user_code")
        recommendquestion_id = request.args.get("recommendquestion_id")
        app_code = request.args.get("app_code")
        sys_code = request.args.get("sys_code")
        page_number = int(request.args.get("page", 1))
        items_per_page = int(request.args.get("page_size", 150))
        parser_id = request.args.get("parser_id")
        orderby = request.args.get("orderby", "create_time")
        desc = request.args.get("desc", type=bool)


        recommendations = RecommendQuestionService.get_list(
            tenant_id=tenant_id,
            sys_code=sys_code,
            app_code=app_code,
            user_code=user_code,
            recommendquestion_id=recommendquestion_id,
            page_number=page_number,
            items_per_page=items_per_page,
            orderby=orderby,
            desc=desc
        )
        return get_json_result(data=recommendations)
    except Exception as e:
        return server_error_response(e)
    
@manager.route('/question/create', methods=['POST'])
@token_required
@validate_request("question")
def create_recommendquestion(tenant_id):
    req = request.json
    try:
        question = req["question"]
        app_code = req["app_code"]
        sys_code = req["sys_code"]
        user_code = req["user_code"]

        recommendations = RecommendQuestionService.insert(
            tenant_id=tenant_id,
            question=question,
            app_code=app_code,
            sys_code=sys_code,
            user_code=user_code
        )
        return get_json_result(data=recommendations)
    except Exception as e:
        return server_error_response(e)

