from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('capture', __name__)


@bp.route('/')
def index():
    db = get_db()
    captures = db.execute(
        'SELECT e.id, section, data, created, emp_id, username'
        ' FROM entry e JOIN user u ON e.emp_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('capture/index.html', captures=captures)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        section = request.form['section']
        data = request.form['data']
        error = None

        if not section:
            error = 'Section is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO entry (section, data, emp_id)'
                ' VALUES (?, ?, ?)',
                (section, data, g.user['id'])
            )
            db.commit()
            return redirect(url_for('capture.index'))

    return render_template('capture/create.html')


def get_entry(id, check_emp=True):
    entry = get_db().execute(
        'SELECT e.id, section, data, created, emp_id, username'
        ' FROM entry e JOIN user u ON e.emp_id = u.id'
        ' WHERE e.id = ?',
        (id,)
    ).fetchone()

    if entry is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_emp and entry['emp_id'] != g.user['id']:
        abort(403)

    return entry


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    entry = get_entry(id)

    if request.method == 'POST':
        section = request.form['section']
        data = request.form['data']
        error = None

        if not section:
            error = 'Section is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE entry SET section = ?, data = ?'
                ' WHERE id = ?',
                (section, data, id)
            )
            db.commit()
            return redirect(url_for('capture.index'))

    return render_template('capture/update.html', entry=entry)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_entry(id)
    db = get_db()
    db.execute('DELETE FROM entry WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('capture.index'))
