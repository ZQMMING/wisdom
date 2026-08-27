"""Test Event Ontology V1"""
import pytest
from tongshu.v_validation.ontology import (
    EventOntology, EventMatcher, EventValidator,
    EventHierarchy, SeverityScoring,
)
from tongshu.v_validation.schema.case import Event, EventCategory, EventSeverity, EvidenceGrade
from datetime import date


class TestEventOntology:
    """测试事件本体类。"""
    
    def test_classify_child_birth(self):
        onto = EventOntology()
        cat = onto.classify_event("出生")
        assert cat == EventCategory.CHILD_BIRTH
    
    def test_classify_death(self):
        onto = EventOntology()
        cat = onto.classify_event("去世")
        assert cat == EventCategory.PARENT_DEATH
    
    def test_classify_exam(self):
        onto = EventOntology()
        cat = onto.classify_event("中进士")
        assert cat == EventCategory.EXAM
    
    def test_classify_job_change(self):
        onto = EventOntology()
        cat = onto.classify_event("迁侍读学士")
        assert cat == EventCategory.JOB_CHANGE
    
    def test_default_severity_critical(self):
        onto = EventOntology()
        sev = onto.get_default_severity(EventCategory.PARENT_DEATH, "去世")
        assert sev == EventSeverity.CRITICAL
    
    def test_default_severity_major(self):
        onto = EventOntology()
        sev = onto.get_default_severity(EventCategory.EXAM, "中举人")
        assert sev == EventSeverity.MAJOR
    
    def test_generate_event(self):
        onto = EventOntology()
        event = onto.generate_event("中进士", date(1754, 6, 20), EvidenceGrade.A)
        assert event.category == EventCategory.EXAM
        assert event.severity == EventSeverity.MAJOR
        assert event.evidence_grade == EvidenceGrade.A


class TestEventMatcher:
    """测试事件匹配规则。"""
    
    def test_matches_exact(self):
        e1 = Event(date(1754, 6, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        e2 = Event(date(1754, 6, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        assert EventMatcher.matches(e1, e2)
    
    def test_matches_within_tolerance(self):
        e1 = Event(date(1754, 6, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        e2 = Event(date(1754, 7, 10), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        # MAJOR severity tolerance = 30 days
        assert EventMatcher.matches(e1, e2)
    
    def test_matches_outside_tolerance(self):
        e1 = Event(date(1754, 6, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        e2 = Event(date(1754, 10, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        # 超过30天容忍度
        assert not EventMatcher.matches(e1, e2)
    
    def test_no_match_different_categories(self):
        e1 = Event(date(1754, 6, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        e2 = Event(date(1754, 6, 20), EventCategory.JOB_CHANGE, EventSeverity.MAJOR, "入翰林院", EvidenceGrade.B)
        assert not EventMatcher.matches(e1, e2)


class TestEventValidator:
    """测试事件验证规则。"""
    
    def test_valid_event(self):
        event = Event(date(1754, 6, 20), EventCategory.EXAM, EventSeverity.MAJOR, "中进士", EvidenceGrade.A)
        valid, errors = EventValidator.validate(event)
        assert valid
        assert errors == []
    
    def test_future_date_invalid(self):
        event = Event(date(2030, 1, 1), EventCategory.EXAM, EventSeverity.MAJOR, "未来考试", EvidenceGrade.A)
        valid, errors = EventValidator.validate(event)
        assert not valid
        assert any("future" in e.lower() for e in errors)
    
    def test_logic_conflict(self):
        # 同一天既出生又去世
        events = [
            Event(date(1754, 1, 1), EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "出生", EvidenceGrade.A),
            Event(date(1754, 1, 1), EventCategory.PARENT_DEATH, EventSeverity.CRITICAL, "去世", EvidenceGrade.A),
        ]
        valid, errors = EventValidator.validate(Event(
            date(1754, 1, 1), EventCategory.CHILD_BIRTH, EventSeverity.MAJOR, "test", EvidenceGrade.A
        ))
        # 单个事件应该验证通过
        assert valid


class TestSeverityScoring:
    """测试严重程度评分。"""
    
    def test_weight_trivial(self):
        assert SeverityScoring.get_weight(EventSeverity.TRIVIAL) == 0.1
    
    def test_weight_critical(self):
        assert SeverityScoring.get_weight(EventSeverity.CRITICAL) == 1.0
    
    def test_tolerance_critical(self):
        tol = SeverityScoring.get_tolerance(EventSeverity.CRITICAL)
        assert tol.days == 7
    
    def test_tolerance_trivial(self):
        tol = SeverityScoring.get_tolerance(EventSeverity.TRIVIAL)
        assert tol.days == 365


class TestEventHierarchy:
    """测试事件层级。"""
    
    def test_lifespan_events(self):
        assert EventCategory.CHILD_BIRTH in EventHierarchy.LIFE_EVENTS
        assert EventCategory.PARENT_DEATH in EventHierarchy.LIFE_EVENTS
    
    def test_career_events(self):
        assert EventCategory.JOB_CHANGE in EventHierarchy.CAREER_EVENTS
        assert EventCategory.PROMOTION in EventHierarchy.CAREER_EVENTS
    
    def test_get_category_group(self):
        assert EventHierarchy.get_category_group(EventCategory.CHILD_BIRTH) == "life"
        assert EventHierarchy.get_category_group(EventCategory.EXAM) == "education"
        assert EventHierarchy.get_category_group(EventCategory.FINANCIAL_LOSS) == "finance"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
