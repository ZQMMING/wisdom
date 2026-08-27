"""Assertion Observatory - 断言观测台.

9层管理员后台链路:
Case Explorer -> Engine Observatory -> Evidence Explorer
-> Semantic Atom Manager -> Assertion Debugger -> Mapping Manager
-> Guidance Preview -> Trace Explorer -> Rule Impact -> Version Manager

核心API:
- GET  /admin/cases
- POST /admin/cases
- GET  /admin/cases/{case_id}
- GET  /admin/cases/{case_id}/evidence
- GET  /admin/cases/{case_id}/atoms
- GET  /admin/cases/{case_id}/assertions
- GET  /admin/assertions/{assertion_id}/trace
- GET  /admin/semantic-atoms
- GET  /admin/concepts
- POST /admin/playground/run
- GET  /admin/rules/{rule_id}/impact
- GET  /admin/versions
- GET  /admin/validate
"""

from .router import router as admin_router

__all__ = ["admin_router"]
