from tasks.stock import dart


def dart_performance_list_run():
    dart.DartPerformanceList().run("DART 재무 데이터 수집 목록 수집")


def dart_performance_run():
    dart.DartPerFormance().run("DART 재무 데이터 수집")
