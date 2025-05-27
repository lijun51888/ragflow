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

import flask
import re
from flask import request
from api import settings
from api.db import StatusEnum
from api.db.services.dialog_service import DialogService
from api.db.services.file_service import FileService
from api.db.services.file2document_service import File2DocumentService
from api.db.services.llm_service import TenantLLMService
from api.db.services.user_service import TenantService
from api.utils import get_uuid
from api.utils.api_utils import server_error_response, get_data_error_result, token_required, get_json_result, validate_request
from api.utils.api_utils import get_result
from rag.utils.storage_factory import STORAGE_IMPL
from api.db import FileType, FileSource


@manager.route('/bulletin/list', methods=['GET'])  # noqa: F821
@token_required
def list_files(tenant_id):

    pf_id = request.args.get("parent_id")
    keywords = request.args.get("keywords", "")
    app_code = request.args.get("app_code")
    sys_code = request.args.get("sys_code")
    
    page_number = int(request.args.get("page", 1))
    items_per_page = int(request.args.get("page_size", 15))
    orderby = request.args.get("orderby", "create_time")
    desc = request.args.get("desc", type=bool)
    if not pf_id:
        root_folder = FileService.get_root_folder(tenant_id)
        pf_id = root_folder["id"]
        FileService.init_knowledgebase_docs(pf_id, tenant_id)
    try:
        e, file = FileService.get_by_id(pf_id)
        if not e:
            return get_data_error_result(message="Folder not found!")
        files, total = FileService.get_by_pf_id(
            tenant_id, pf_id, page_number, items_per_page, orderby, desc, keywords)
        parent_folder = FileService.get_parent_folder(pf_id)
        if not parent_folder:
            return get_json_result(message="File not found!")
        return get_json_result(data={"total": total, "files": files, "parent_folder": parent_folder.to_json()})
    except Exception as e:
        return server_error_response(e)
    
    
@manager.route('/bulletin/get/<file_id>', methods=['GET'])  # noqa: F821
@token_required
def get(tenant_id,file_id):
    try:
        e, file = FileService.get_by_id(file_id)
        if not e:
            return get_data_error_result(message="Document not found!")

        blob = STORAGE_IMPL.get(file.parent_id, file.location)
        if not blob:
            b, n = File2DocumentService.get_storage_address(file_id=file_id)
            blob = STORAGE_IMPL.get(b, n)

        response = flask.make_response(blob)
        ext = re.search(r"\.([^.]+)$", file.name)
        if ext:
            if file.type == FileType.VISUAL.value:
                response.headers.set('Content-Type', 'image/%s' % ext.group(1))
            else:
                response.headers.set(
                    'Content-Type',
                    'application/%s' %
                    ext.group(1))
        return response
    except Exception as e:
        return server_error_response(e)