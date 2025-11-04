from flask import Blueprint, render_template, request, redirect, url_for

main = Blueprint('main', __name__)

urls = {}

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        # Aquí iría la lógica para acortar la URL
    return render_template('index.html')

@main.route('/shorten', methods=['POST'])
def redirect_short(short_id):
    if short_id in urls:
        return redirect(urls[short_id])
    return "URL no encontrada", 404