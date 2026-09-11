from backend.app.agents.registry import AgentRegistry
from backend.app.agents.context import SharedContext
from backend.app.agents.supervisor import Supervisor
from backend.app.agents.detective import DetectiveAgent
from backend.app.agents.timeline import TimelineAgent
from backend.app.agents.correlation import CorrelationAgent
from backend.app.agents.report import ReportAgent


def test_agent_orchestration_basic_flow():
    registry = AgentRegistry()
    registry.register(DetectiveAgent())
    registry.register(TimelineAgent())
    registry.register(CorrelationAgent())
    registry.register(ReportAgent())

    ctx = SharedContext()
    sup = Supervisor(registry, ctx)

    text = 'Alice saw Bob on 2022-01-02 and later Alice met Carol on 2022-02-03.'

    # investigative task discovers entities and dates
    res1 = sup.submit({'type': 'investigate', 'text': text})
    assert 'entities' in res1['result']

    # timeline extraction
    res2 = sup.submit({'type': 'timeline', 'text': text})
    assert 'events' in res2['result']

    # correlation
    res3 = sup.submit({'type': 'correlate'})
    assert isinstance(res3['result'].get('correlations'), dict)

    # final report
    res4 = sup.submit({'type': 'report'})
    assert res4['result']['entities_count'] >= 1
    assert 'summary' in res4['result']
