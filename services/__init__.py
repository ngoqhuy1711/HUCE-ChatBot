"""
Services Package - Các dịch vụ xử lý nghiệp vụ cho backend

Package này chứa:
- nlp_service: Xử lý NLP và quản lý context hội thoại
- csv_service: Xử lý dữ liệu từ các file CSV
"""

from .nlp_service import get_nlp_service, NLPService
from . import csv_service

__all__ = [
    'get_nlp_service',
    'NLPService',
    'csv_service',
]

