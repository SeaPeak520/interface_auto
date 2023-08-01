#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MyBaseFailure(Exception):
    pass


class JsonpathExtractionFailed(MyBaseFailure):
    pass

#找不到
class NotFoundError(MyBaseFailure):
    pass


class FileNotFound(FileNotFoundError, NotFoundError):
    pass


class SqlNotFound(NotFoundError):
    pass


class AssertTypeError(MyBaseFailure):
    pass


class DataAcquisitionFailed(MyBaseFailure):
    pass


class ValueTypeError(MyBaseFailure):
    pass


class SendMessageError(MyBaseFailure):
    pass

#值找不到
class ValueNotFoundError(MyBaseFailure):
    pass
#值为空判断
class ValueNullError(MyBaseFailure):
    pass
