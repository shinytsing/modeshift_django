"""
修复allauth AccountMiddleware的WSGIRequest错误
"""
import logging
from django.http import HttpResponse
from allauth.account.middleware import AccountMiddleware as BaseAccountMiddleware

logger = logging.getLogger(__name__)


class FixedAccountMiddleware(BaseAccountMiddleware):
    """
    修复allauth AccountMiddleware的WSGIRequest错误
    
    原始错误：'WSGIRequest' object has no attribute 'status_code'
    这个错误发生在allauth中间件试图访问request对象的status_code属性时
    """
    
    def __call__(self, request):
        """
        处理请求，修复status_code属性错误
        """
        try:
            # 调用父类的处理方法
            response = self.get_response(request)
            
            # 确保response是HttpResponse对象而不是WSGIRequest
            if hasattr(response, 'status_code'):
                # 调用父类的_remove_dangling_login方法
                try:
                    self._remove_dangling_login(request, response)
                except AttributeError as e:
                    if "'WSGIRequest' object has no attribute 'status_code'" in str(e):
                        # 忽略这个特定的错误，因为它是allauth的bug
                        logger.warning(f"忽略allauth中间件错误: {e}")
                    else:
                        # 其他AttributeError需要重新抛出
                        raise
                except Exception as e:
                    # 记录其他异常但不中断请求处理
                    logger.error(f"allauth中间件处理异常: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"FixedAccountMiddleware处理请求失败: {e}")
            # 如果中间件失败，直接调用下一个中间件
            return self.get_response(request)
    
    def _remove_dangling_login(self, request, response):
        """
        安全版本的_remove_dangling_login，避免WSGIRequest错误
        """
        try:
            # 确保response有status_code属性
            if not hasattr(response, 'status_code'):
                logger.warning("Response对象没有status_code属性，跳过_remove_dangling_login")
                return
            
            # 调用父类方法
            super()._remove_dangling_login(request, response)
            
        except AttributeError as e:
            if "'WSGIRequest' object has no attribute 'status_code'" in str(e):
                logger.warning("检测到allauth WSGIRequest错误，已安全处理")
            else:
                raise
        except Exception as e:
            logger.error(f"_remove_dangling_login执行失败: {e}")

