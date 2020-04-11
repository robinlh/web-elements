from flask import Flask, url_for, redirect, request, render_template

app = Flask(__name__)


@app.route('/')
def student():
    return render_template('student.html')


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        res = request.form
        return render_template('result.html', result=res)


if __name__ == '__main__':
    app.run()
