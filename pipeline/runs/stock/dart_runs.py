from pipeline.tasks.stock import dart
import pytest
from pipeline.utils import utils


def test_dart_performance_list_run():
    dart.DartPerformanceList().run("DART 재무 데이터 수집 목록 수집")

def test_dart_performance_run():
    dart.DartPerFormance().run("DART 재무 데이터 수집")
