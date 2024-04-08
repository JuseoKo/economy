import pytest
from airflow.models import DagBag
from loguru import logger


@pytest.mark.unit
def test_no_import_errors():
    dag_bag = DagBag(dag_folder="./", include_examples=False)
    logger.info(f"!!! Import errors: {len(dag_bag.import_errors)}")
    logger.info(f"DAGs : {dag_bag.size()}")
    assert len(dag_bag.import_errors) == 0, "No Import Failures"
