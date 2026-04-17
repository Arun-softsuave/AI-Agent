

def route_after_understand(state):
    if state.get("csv_relevant"):
        return "related"
    return "not_related"


def route_after_validation(state):
    if state.get("error"):
        return "retry"
    return "success"


def route_after_retry(state):
    if state.get("retry_count", 0) >= state.get("max_retry", 3):
        return "fail"
    return "retry_again"