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
from flask import Blueprint, request, Response
from flask_login import login_required, current_user
from api.db.services.user_service import UserTenantService
from api.db.services.recommend_question_service import RecommendQuestionService
from api import settings
from api.utils import get_uuid, current_timestamp, datetime_format
from api.utils.api_utils import server_error_response, get_data_error_result, get_json_result, validate_request


@manager.route('/get', methods=['GET'])
@login_required
def get_recommendquestions():
    req = request.json
    try:
        tenants = UserTenantService.query(user_id=current_user.id)
        if not tenants:
            return get_data_error_result(message="Tenant not found!")

        tenant_id = tenants[0].tenant_id
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
    
@manager.route('/create', methods=['POST'])
@login_required
@validate_request("question")
def create_recommendquestion():
    req = request.json
    try:
        tenants = UserTenantService.query(user_id=current_user.id)
        if not tenants:
            return get_data_error_result(message="Tenant not found!")

        tenant_id = tenants[0].tenant_id
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

