from __future__ import annotations


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}


def _humanize_segment(segment: str) -> str:
    segment = (segment or "").strip().strip("/")
    if not segment:
        return "Default"

    normalized = segment.replace("_", "-").lower()

    special_cases = {
        "api-key": "API Keys",
        "unipile": "Unipile",
        "ai": "AI",
    }
    if normalized in special_cases:
        return special_cases[normalized]

    parts = [p for p in normalized.split("-") if p]
    return " ".join(p.upper() if p in {"ai", "id", "url"} else p.title() for p in parts)


def _tag_from_path(path: str) -> str | None:
    """
    Derive a tag from the OpenAPI path key.

    Strategy:
    - Prefer segment immediately after '/api/' (e.g. '/api/users/...' -> 'Users')
    - Otherwise, use the first non-empty segment.
    - Ignore non-API roots that would clutter docs.
    """
    segments = [s for s in (path or "").split("/") if s]
    if not segments:
        return None

    ignore_roots = {"admin", "health", "documents", "static", "media"}

    if segments[0] == "api":
        if len(segments) < 2:
            return "API"

        first = segments[1]

        # Some routes are grouped under a container prefix (e.g. /api/chats/teams/).
        # Prefer the resource segment when it is stable (not a path parameter).
        if first in {"chats"} and len(segments) >= 3:
            candidate = segments[2]
            if candidate.startswith("{") and candidate.endswith("}"):
                return _humanize_segment(first)
            return _humanize_segment(candidate)

        return _humanize_segment(first)

    if segments[0] in ignore_roots:
        return None

    return _humanize_segment(segments[0])


def auto_tag_by_path_segment(
    result: dict,
    generator,
    request,
    public: bool,
) -> dict:
    """
    drf-spectacular postprocessing hook to group operations in Swagger UI.

    This assigns `operation.tags` based on the URL path (Option C).
    It preserves explicit tags when set (anything other than the default tag).
    """
    paths: dict = result.get("paths") or {}
    discovered_tags: set[str] = set()

    def should_override_existing_tags(existing_tags: object) -> bool:
        if not isinstance(existing_tags, list) or not existing_tags:
            return True
        normalized = [str(t).strip().lower() for t in existing_tags if t]
        if not normalized:
            return True
        return all(t in {"default", "api"} for t in normalized)

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        auto_tag = _tag_from_path(path)
        if not auto_tag:
            continue

        for method, operation in path_item.items():
            if method not in HTTP_METHODS or not isinstance(operation, dict):
                continue

            existing_tags = operation.get("tags")
            if not should_override_existing_tags(existing_tags):
                discovered_tags.update(str(t) for t in existing_tags if t)
                continue

            operation["tags"] = [auto_tag]
            discovered_tags.add(auto_tag)

    existing_top_tags = result.get("tags")
    if not isinstance(existing_top_tags, list):
        existing_top_tags = []

    existing_names = {
        t.get("name")
        for t in existing_top_tags
        if isinstance(t, dict) and isinstance(t.get("name"), str)
    }

    for name in sorted(discovered_tags):
        if name not in existing_names:
            existing_top_tags.append({"name": name})

    preferred_order = [
        "Auth",
        "Impersonation",
        "Users",
        "User",
        "Teams",
        "Chats",
        "Leads",
        "Email",
        "API Keys",
        "Unipile",
    ]

    def sort_key(tag_obj: dict) -> tuple[int, str]:
        name = (tag_obj.get("name") or "").strip()
        try:
            return (preferred_order.index(name), "")
        except ValueError:
            return (len(preferred_order), name.lower())

    result["tags"] = sorted(
        [t for t in existing_top_tags if isinstance(t, dict) and t.get("name")],
        key=sort_key,
    )
    return result

