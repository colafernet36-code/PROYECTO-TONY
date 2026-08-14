import uuid
from datetime import datetime, timedelta, timezone

from contracts.action import Action, ActionStatus, RiskLevel
from contracts.authorization import AuthorizationGrant


def test_action_defaults_to_created_and_normal_risk():
    action = Action(source="voice", intent="turn_on_light")

    assert action.status == ActionStatus.CREATED
    assert action.risk_level == RiskLevel.NORMAL


def test_action_with_status_is_immutable_and_updates_timestamp():
    action = Action(source="voice", intent="turn_on_light")
    updated = action.with_status(ActionStatus.EXECUTING)

    assert action.status == ActionStatus.CREATED
    assert updated.status == ActionStatus.EXECUTING
    assert updated.updated_at >= action.updated_at


def test_authorization_grant_valid_until_expiry_or_consumption():
    now = datetime.now(timezone.utc)
    grant = AuthorizationGrant(
        action_id=uuid.uuid4(),
        device_id=uuid.uuid4(),
        nonce="abc",
        expires_at=now + timedelta(minutes=1),
        signature="sig",
    )
    assert grant.is_valid(now=now)

    expired = grant.model_copy(update={"expires_at": now - timedelta(seconds=1)})
    assert not expired.is_valid(now=now)

    consumed = grant.model_copy(update={"consumed": True})
    assert not consumed.is_valid(now=now)
