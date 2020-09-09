from flask import Blueprint, render_template

general_bp = Blueprint('general', __name__)

from app.general import routes
