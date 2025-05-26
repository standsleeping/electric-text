from electric_text.providers.logging.data.http_log_entry import HttpLogEntry


def http_log_entry_to_dict(entry: HttpLogEntry) -> dict[str, object]:
    """Convert HttpLogEntry to dictionary for serialization.

    Args:
        entry: The HttpLogEntry to convert

    Returns:
        Dictionary representation of the log entry
    """
    return {
        "timestamp": entry.timestamp,
        "method": entry.method,
        "url": entry.url,
        "request": {
            "headers": entry.request_headers,
            "body": entry.request_body,
        },
        "response": {
            "status": entry.response_status,
            "headers": entry.response_headers,
            "body": entry.response_body,
        },
        "duration_ms": entry.duration_ms,
        "provider": entry.provider,
        "model": entry.model,
        "error": entry.error,
    }
