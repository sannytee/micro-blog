from flask import render_template

from app.general import general_bp


@general_bp.route('/')
def main():
    return render_template('test.html', title='Explore')
