from typing import Union

from fastapi import HTTPException
from starlette.requests import Request

import web.constant.biz_constant as biz_const
import web.util.str as str_util
from web.model.base import standard_error_response
from web.model.huixiangdou import HxdToken
from web.model.qalib import QalibInfo
from web.service.qalib import QaLibCache
from web.util.log import log

logger = log(__name__)


def _get_hxd_token_by_cookie(cookies) -> Union[HxdToken, None]:
    return HxdToken(**(
        str_util.parse_jwt(
            cookies.get(biz_const.HXD_COOKIE_KEY)
        )
    )) if cookies and cookies.get(biz_const.HXD_COOKIE_KEY) else None


def check_hxd_token(request: Request) -> QalibInfo:
    hxd_token = _get_hxd_token_by_cookie(request.cookies)
    if not hxd_token or not hxd_token.jti:
        logger.error("[access] invalid request, need login to feature store first")
        err_body = standard_error_response(biz_const.ERR_QALIB_API_NO_ACCESS)
        raise HTTPException(status_code=200, detail=err_body.model_dump())

    info = QaLibCache().get_qalib_info(hxd_token.jti)
    if not info:
        logger.error(f"[access] invalid login, feature_store_id: {hxd_token.jti} not exists")
        err_body = standard_error_response(biz_const.ERR_QALIB_INFO_NOT_FOUND)
        raise HTTPException(status_code=200, detail=err_body.model_dump())

    return info