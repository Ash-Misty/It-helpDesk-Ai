from app.schemas.state import WorkflowStage, StateStatus, VALID_TRANSITIONS, STAGE_TO_STATUS


def is_valid_transition(current: WorkflowStage, target: WorkflowStage) -> bool:
    if target == current:
        return True
    allowed = VALID_TRANSITIONS.get(current, set())
    return target in allowed


def get_status_for_stage(stage: WorkflowStage) -> StateStatus:
    return STAGE_TO_STATUS.get(stage, StateStatus.ACTIVE)


def get_valid_next_stages(current: WorkflowStage) -> list[WorkflowStage]:
    return list(VALID_TRANSITIONS.get(current, set()))
