from datetime import datetime


def seralize_dict(item: dict) -> dict:
    out = item.copy()

    if isinstance(out.get('created_at'), datetime):
        out['created_at'] = out['created_at'].isoformat()
    if isinstance(out.get('updated_at'), datetime):
        out['updated_at'] = out['updated_at'].isoformat()
    if isinstance(out.get('start_date'), datetime):
        out['start_date'] = out['start_date'].isoformat()
    if isinstance(out.get('end_date'), datetime):
        out['end_date'] = out['end_date'].isoformat()
    if isinstance(out.get('course_created_at'), datetime):
        out['course_created_at'] = out['course_created_at'].isoformat()
    return out
