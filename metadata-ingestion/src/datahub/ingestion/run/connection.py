import logging

from datahub._version import __version__
from datahub.ingestion.api.source import TestableSource, TestConnectionReport
from datahub.ingestion.graph.config import ClientMode
from datahub.ingestion.run.pipeline_config import BasePipelineConfig
from datahub.ingestion.source.source_registry import source_registry

logger = logging.getLogger(__name__)


def test_source_connection(pipeline_config: dict) -> TestConnectionReport:
    try:
        # Check if source supports test connection functionality
        source_type = pipeline_config.get("source", {}).get("type")
        source_class = source_registry.get(source_type)
        if issubclass(source_class, TestableSource):
            return _run_test_connection(source_class, pipeline_config)
        else:
            return TestConnectionReport(
                internal_failure=True,
                internal_failure_reason=f"Source {source_type} in library version {__version__} does not support test connection functionality.",
            )
    except Exception as e:
        logger.error(e)
        raise e


def _run_test_connection(
    source_cls: type[TestableSource], pipeline_config: dict
) -> TestConnectionReport:
    config = BasePipelineConfig.model_validate(pipeline_config)
    graph = config.make_graph(ClientMode.INGESTION)
    ctx = config.make_pipeline_ctx(graph=graph, dry_run=True, preview_mode=True)
    return source_cls.test_connection_with_ctx(
        pipeline_config.get("source", {}).get("config", {}), ctx
    )
