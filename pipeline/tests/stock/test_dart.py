from pipeline.tasks.stock import dart
import pytest
from pipeline.utils import utils

pf_run = dart.DartPerFormance()

class TestPerFormance:
    @pytest.mark.integration
    def test_run(self):
        # 1. 사전 데이터 수집
        # fetch_list = pf_run.fetch_list()

        # 2. 수집할 데이터 목록 추출
        # extract = pf_run.extract(data=fetch_list)

        # 3. 필요한 데이터 수집
        extract = utils.load_pickle()
        fetch = pf_run.fetch(extract)

        # 4. 필요한 데이터 변환
        transform = pf_run.transform(fetch)

        # 5. 필요한 데이터 저장
        load = pf_run.load(data=transform)