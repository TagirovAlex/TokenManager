from flask import request

def paginate(query, page=1, per_page=20, max_per_page=100):
    try:
        page = int(page)
        per_page = int(per_page)
    except (ValueError, TypeError):
        page = 1
        per_page = 20
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {'items': pagination.items, 'total': pagination.total, 'page': page, 'per_page': per_page, 'pages': pagination.pages, 'has_prev': pagination.has_prev, 'has_next': pagination.has_next, 'prev_num': pagination.prev_num if pagination.has_prev else None, 'next_num': pagination.next_num if pagination.has_next else None}

def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return page, per_page

def search_filter(query, model, search_fields, search_term):
    if not search_term:
        return query
    from app import db
    conditions = []
    for field in search_fields:
        if hasattr(model, field):
            conditions.append(getattr(model, field).ilike(f'%{search_term}%'))
    if conditions:
        return query.filter(db.or_(*conditions))
    return query