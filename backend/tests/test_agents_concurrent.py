import concurrent.futures
from backend.app.agents.registry import AgentRegistry
from backend.app.agents.context import SharedContext
from backend.app.agents.persistent_context import SQLPersistentContext
from backend.app.agents.detective import DetectiveAgent
from backend.app.agents.timeline import TimelineAgent
from backend.app.agents.correlation import CorrelationAgent
from backend.app.agents.report import ReportAgent
from backend.app.agents.async_supervisor import AsyncSupervisor


def worker_submit(sup, payload):
    # run sync wrapper to allow thread-based concurrency
    return sup.submit_sync(payload)


def test_concurrent_submissions_and_persistence():
    registry = AgentRegistry()
    registry.register(DetectiveAgent())
    registry.register(TimelineAgent())
    registry.register(CorrelationAgent())
    registry.register(ReportAgent())

    # use SQL persistent context to verify persistence across concurrent workers
    ctx = SQLPersistentContext()
    sup = AsyncSupervisor(registry, ctx, route_map={'investigate': 'detective', 'timeline': 'timeline', 'correlate': 'correlation', 'report': 'report'})

    tasks = [
        {'type': 'investigate', 'text': f'Alice met Bob on 2022-01-0{i}'} for i in range(1, 6)
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(worker_submit, sup, t) for t in tasks]
        results = [f.result() for f in futs]

    # ensure results stored in persistent context
    snap = ctx.snapshot()
    assert 'tasks' in snap
    assert len(snap['tasks']) >= 5
