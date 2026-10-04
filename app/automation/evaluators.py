from app.enum.condition_operator import ConditionOperator


def evaluate_condition(operator, actual_value, expected_value) -> bool:
    if operator == ConditionOperator.GT:
        return actual_value > expected_value
    if operator == ConditionOperator.GTE:
        return actual_value >= expected_value
    if operator == ConditionOperator.LT:
        return actual_value < expected_value
    if operator == ConditionOperator.LTE:
        return actual_value <= expected_value
    if operator == ConditionOperator.EQ:
        return actual_value == expected_value

    return False
