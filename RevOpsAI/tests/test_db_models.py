from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pytest

from RevOpsAI.src.db.models import Base, ProspectORM, AuditLogORM
from RevOpsAI.src.db.session import get_engine, init_db, get_session_factory
from RevOpsAI.src.core.models import ProspectState


def test_create_and_query_prospect_orm():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        lead = ProspectORM(
            id="lead_test_01",
            tenant_id="tenant_dental",
            name="Clinica Dental Norte",
            url="https://dentalnorte.es",
            state=ProspectState.INGESTED.value,
            score=75,
            research_summary="Clinica moderna",
            draft_message="Hola Clinica Dental",
            is_blacklisted=False,
        )
        session.add(lead)
        session.commit()

        queried = session.query(ProspectORM).filter_by(id="lead_test_01").first()
        assert queried is not None
        assert queried.tenant_id == "tenant_dental"
        assert queried.name == "Clinica Dental Norte"
        assert queried.url == "https://dentalnorte.es"
        assert queried.state == ProspectState.INGESTED.value
        assert queried.score == 75
        assert queried.research_summary == "Clinica moderna"
        assert queried.draft_message == "Hola Clinica Dental"
        assert queried.is_blacklisted is False
        assert isinstance(queried.created_at, datetime)
        assert isinstance(queried.updated_at, datetime)


def test_create_and_query_audit_log_orm():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        log = AuditLogORM(
            id="audit_test_01",
            tenant_id="tenant_dental",
            lead_id="lead_test_01",
            actor="ScoringAgent",
            action="SCORE_CALCULATED",
            reason="Score updated to 75",
        )
        session.add(log)
        session.commit()

        queried = session.query(AuditLogORM).filter_by(id="audit_test_01").first()
        assert queried is not None
        assert queried.tenant_id == "tenant_dental"
        assert queried.lead_id == "lead_test_01"
        assert queried.actor == "ScoringAgent"
        assert queried.action == "SCORE_CALCULATED"
        assert queried.reason == "Score updated to 75"
        assert isinstance(queried.created_at, datetime)


def test_session_factory_and_init_db(tmp_path):
    db_file = tmp_path / "subdir" / "test.db"
    db_url = f"sqlite:///{db_file}"
    engine = get_engine(db_url)
    init_db(engine)

    session_factory = get_session_factory(engine)
    with session_factory() as session:
        lead = ProspectORM(
            id="lead_test_02",
            tenant_id="tenant_dental",
            name="Clinica Sur",
            url="https://clinicasur.es",
            state=ProspectState.QUALIFIED.value,
            score=80,
        )
        session.add(lead)
        session.commit()

        queried = session.query(ProspectORM).filter_by(id="lead_test_02").first()
        assert queried is not None
        assert queried.name == "Clinica Sur"
