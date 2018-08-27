import os
import traceback
from ee.profile.xobj import XObject
from ee.common import logger
from ee.tinyrpc.dispatch import RPCDispatcher
from ee.tinyrpc.exc import ServerError
from ee.tinyrpc.exc import MethodNotFoundError

class EEDispatcher(RPCDispatcher):

    _methods = []
    def __init__(self, publisher):
        super(EEDispatcher, self).__init__()

    @classmethod
    def register_method(cls, method):
        cls._methods.append(method)

    def eval(self, name, method, *args, **kwargs):
        try:
            obj = XObject.get_object(name)
            func = getattr(obj, method)
            if args:
                result = func(*args)
            elif kwargs:
                result =func(**kwargs)
            else:
                result = func()
        except Exception:
            logger.warning("%s"%(traceback.format_exc()))

        return result

    def register_public_methods(self):
        for method in self._methods:
            logger.boot("register method: %r" %(method))
            self.add_method(method)
            
        self.add_method(self.eval)

    def _dispatch(self, request):
        try:
            try:
                method = self.get_method(request.method)
            except MethodNotFoundError as e:
                return request.error_respond(e)

            # we found the method
            # Does not support args and kwargs at the same time
            try:
                if request.args:
                        result = method(*request.args)
                elif request.kwargs:
                        result = method(**request.kwargs)
                else:
                        result = method()

            except Exception as e:
                # an error occured within the method, return it
                return request.error_respond(e)

            # respond with result
            return request.respond(result)
        except Exception as e:
            # unexpected error, do not let client know what happened
            logger.error(e.message, os.linesep)
            return request.error_respond(ServerError(e.message + os.linesep))
        