import tempfile
from datetime import date
from distutils.util import strtobool
from io import StringIO
from typing import Optional
from unittest import mock

import ldap
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect
from jinja2 import TemplateNotFound

from clocky.forms.contract import ContractForm
from clocky.forms.import_time import ImportFileForm
from clocky.forms.login import LoginForm
from clocky.forms.reporting import (
    ContractCommitForm,
    ContractReportingForm,
    ReportingForm,
)
from clocky.forms.subject import SubjectForm
from clocky.forms.timesheet import TimesheetFiltersForm, TimesheetForm
from clocky.models import Contract, ContractLine, Subject, User
from clocky.models.timesheet import Timesheet

bp = Blueprint("clocky", __name__, template_folder="templates", static_folder="static")

login_manager = LoginManager()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id) -> Optional[User]:
    return User(user_id)


def page_not_found(error):
    return render_template("404.html"), 404


@bp.route("/", defaults={"page": "index"})
@login_required
def show(page):
    """Later we may use this route to serve pre generated CRA"""
    try:
        return render_template(f"{page}.html")
    except TemplateNotFound:
        abort(404)


@bp.route("/login", defaults={"page": "login"}, methods=["GET", "POST"])
def login(page):
    """Login page"""
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if current_app.config.get("LDAP_PROVIDER_URL"):
            conn = ldap.initialize(current_app.config["LDAP_PROVIDER_URL"])
            bind = current_app.config["LDAP_BIND_FORMAT"].format(username=username)
            try:
                conn.simple_bind_s(bind, password)
                user = User(username=username)
                login_user(user)

                return redirect(url_for("clocky.show"))
            except ldap.INVALID_CREDENTIALS:
                flash("Invalid username or password")
        else:
            flash("Invalid username or password")
    try:
        return render_template(f"{page}.html", form=form)
    except TemplateNotFound:
        abort(404)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("clocky.login"))


@bp.route("/reporting", methods=["POST", "GET"])
@login_required
def reporting_form():
    """
    Generation of MonthlyReports
    """
    form = ReportingForm()

    if request.method == "POST" and form.validate_on_submit():
        if form.all_subjects.data:
            form.subjects.data = False

        return reporting(
            form.year.data, form.month.data, form.months.data, form.subjects.data,
        )
    return render_template("reporting_form.html", form=form)


@bp.route("/reporting/<int:year>/<int:month>/<int:months>")
@login_required
def reporting(year, month, months, subjects=[]):
    """
    Generate monthly report
    """
    report = Subject.monthly_report(year, month, months, subjects)

    return report.render(layout="multi_subject_report_page.html")


@bp.route("/reporting/subject/<subject>/<int:year>/<int:month>/<int:months>")
@login_required
def pdf_report(subject: str, year: int, month: int, months: int):
    """
    Generate CRA for a given subject as attachement (triggers download)
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        cra = Subject.query.get(subject).cra(year, month, months)

        return send_file(
            cra.generate_pdf(tmpdirname),
            as_attachment=True,
            attachment_filename=cra.filename_pdf,
        )


@bp.route("/reporting/subject", methods=["GET", "POST"])
@login_required
def generate_subject_monthly_report():
    """
    Generates monthly report for given subjects.
    If none given, all actives for give peridf
    """
    commit_form = ContractCommitForm()
    if request.method == "POST":
        form = commit_form
    else:
        form = ContractReportingForm(formdata=request.args)
        # fake commit result to get the same behaviours has ContractCommitForm
        # but force to zero to avoir csrf attack to commit/close a month
        form.commit = mock.Mock(data=0)

    if not form.validate():
        return render_template("subject_report_page.html", message=str(form.errors))

    def f(var):
        return getattr(form, var).data

    return (
        Subject.query.get(f("contract"))
        .cra(*map(f, ["year", "month", "months"]))
        .render(
            form=form,
            commit_form=commit_form,
            date=date,
            layout="subject_report_page.html",
        )
    )


@bp.route("/time/import", methods=["GET"])
@login_required
def import_form():
    """Get import time form."""
    try:
        return render_template("import_form.html", import_form=ImportFileForm())
    except TemplateNotFound:
        abort(404)


@bp.route("/time/import-tasks", methods=["POST"])
@login_required
def import_task():
    """Dry run time file or import file tasks."""
    form = ImportFileForm()
    response = {}

    if form.validate_on_submit():
        response = Timesheet.import_tasks(
            current_user.username,
            form.get_file_content(),
            file_format=form.file_format.data,
            dry_run=form.dry_run.data,
        )

    if form.time_file.errors:
        response = {"errors": ["File error: " + ", ".join(form.time_file.errors)]}
    if form.file_format.errors:
        response = {"errors": ["Format error: " + ", ".join(form.file_format.errors)]}

    return response


@bp.route("/api/time/import-tasks", methods=["POST"])
@csrf.exempt
def api_import_tasks():
    """Import tasks without login and crsf token.

    This can be called with `curl` or `request` to import your tasks using CLI

    $ curl -i -X POST -H "Content-Type: multipart/form-data" \
           -F username='test' \
           -F password='myP455w0rd' \
           -F file_format='csv'
           -F dry_run=true
           -F time_file='@/my/path/to/my/tasks.csv \
           https://myclocky.instance.cloud/api/time/import-tasks
    """
    data = {
        "username": request.form.get("username"),
        "password": request.form.get("password"),
        "time_file": request.files.get("time_file"),
        "file_format": request.form.get("file_format"),
    }

    if None in data.values():
        return (
            {
                "errors": [
                    f"{key} is a mandatory field"
                    for key in data.keys()
                    if not data.get(key)
                ]
            },
            400,
        )

    try:
        data["dry_run"] = (
            strtobool(request.form.get("dry_run"))
            if request.form.get("dry_run")
            else False
        )
    except ValueError as err:
        return {"errors": f"dry_run: { str(err)}"}

    conn = ldap.initialize(current_app.config["LDAP_PROVIDER_URL"])
    bind = current_app.config["LDAP_BIND_FORMAT"].format(username=data["username"])
    try:
        conn.simple_bind_s(bind, data["password"])
        user = User(username=data["username"])
        file_content = StringIO(data["time_file"].read().decode("UTF8"))
        return Timesheet.import_tasks(
            user_code=user.username,
            file_content=file_content,
            file_format=data["file_format"],
            dry_run=bool(data["dry_run"]),
        )

    except ldap.INVALID_CREDENTIALS:
        abort(403)


@bp.route("/time/view/", defaults={"page": 1}, methods=["GET"])
@bp.route("/time/view/<int:page>", methods=["GET"])
@login_required
def view_timesheet(page):
    filters = TimesheetFiltersForm(request.args)
    pagination, items = Timesheet.get_all_at(page=page, filters=request.args.to_dict(),)
    try:
        return render_template(
            "timesheet.html", subjects=items, pagination=pagination, form=filters,
        )
    except TemplateNotFound:
        abort(404)


@bp.route("/time/add/", defaults={"subject_code": None}, methods=["GET"])
@bp.route("/time/add/<string:subject_code>", methods=["GET"])
@login_required
def timesheet_form(subject_code):
    """Get add time form."""
    form = TimesheetForm()
    if subject_code:
        form.subject.data = subject_code
    try:
        return render_template("timesheet_form.html", add_form=form)
    except TemplateNotFound:
        abort(404)


@bp.route("/time/add", methods=["POST"])
@login_required
def add_timesheet():
    form = TimesheetForm()

    if not form.validate_on_submit():
        for key in form.errors:
            flash(f"{ key }: { ','.join(form.errors[key]) }", "error")
        return render_template("timesheet_form.html", add_form=form), 400

    timesheet = Timesheet(
        user_code=form.user_code.data,
        subject_code=form.subject.data,
        date=form.date.data,
        description=form.description.data,
        spent_hours=form.hours_spent.data,
    )
    try:
        timesheet.save()
    except ValueError as error:
        flash(str(error), "error")
        return render_template("timesheet_form.html", add_form=form), 409

    form.reset()
    flash("Temps ajouté avec succès.", "info")
    return render_template("timesheet_form.html", add_form=form), 201


@bp.route("/contracts/view/", defaults={"page": 1}, methods=["GET"])
@bp.route("/contracts/view/<int:page>", methods=["GET"])
@login_required
def view_contracts(page):
    try:
        return render_template(
            "contracts.html", pagination=Subject.get_all_at(page=page),
        )
    except TemplateNotFound:
        abort(404)


@bp.route("/contracts/add/", defaults={"subject_code": None}, methods=["GET"])
@bp.route("/contracts/add/<string:subject_code>", methods=["GET"])
@login_required
def contract_form(subject_code):
    form = ContractForm()
    if subject_code:
        form.subject.data = subject_code
    try:
        return render_template("contract_form.html", form=form)
    except TemplateNotFound:
        abort(404)


@bp.route("/contracts/add", methods=["POST"])
@login_required
def add_contract():
    form = ContractForm()
    status_code = 201

    if form.validate_on_submit():
        subject = Subject.query.get(form.subject.data)
        if not subject.contracts:
            subject.contracts.append(Contract())
        subject.contracts[0].lines.append(
            ContractLine(
                bought_days=form.bought_days.data,
                ceiling_days=form.ceiling_days.data,
                start_date=form.start_date.data,
                type=form.contract_type.data,
                active=form.active.data,
            )
        )
        try:
            subject.save()
            form.reset()
            flash("Le contrat a été ajouté avec succès.", "info")
        except ValueError as error:
            status_code = 409
            flash(str(error), "error")
    else:
        status_code = 400
        for key in form.errors:
            flash(f"{ key }: { ','.join(form.errors[key]) }", "error")
    try:
        return render_template("contract_form.html", form=form), status_code
    except TemplateNotFound:
        abort(404)


@bp.route("/subjects/add", methods=["GET"])
@login_required
def subject_form():
    try:
        return render_template("subject_form.html", form=SubjectForm())
    except TemplateNotFound:
        abort(404)


@bp.route("/subjects/add", methods=["POST"])
@login_required
def add_subject():
    form = SubjectForm()

    if not form.validate_on_submit():
        for key in form.errors:
            flash(f"{ key }: { ','.join(form.errors[key]) }", "error")
        return render_template("subject_form.html", form=form), 400

    subject = Subject(
        code=form.code.data,
        odoo_analytic_code=form.odoo_code.data or None,
        description=form.description.data,
    )
    try:
        subject.save()
    except ValueError as error:
        flash(str(error), "error")
        return render_template("subject_form.html", form=form), 409

    form.reset()
    flash("Le sujet a été ajouté avec succès.", "info")

    try:
        return render_template("subject_form.html", form=form), 201
    except TemplateNotFound:
        abort(404)
