from hashlib import md5
from flask import Blueprint, render_template, redirect, abort, request, make_response, url_for
from flask_login import login_required, current_user
from database import session
from models.user import User
from forms.payment import PaymentForm

blueprint = Blueprint('gateway', __name__, url_prefix='/gateway')
HOST = 'https://www.free-kassa.ru/merchant/cash.php'
SHOP_ID = 64860
SECRET_ONE = '8gdj75mb'
SECRET_TWO = 'p1hhfqfs'


@blueprint.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    form = PaymentForm()
    if form.validate_on_submit():
        print(form.test.data)
        if int(form.test.data) == 1:
            current_user.money += form.money_amount.data
            connect = session.create_session()
            connect.merge(current_user)
            connect.commit()
            return redirect(url_for('gateway.success'))
        sign = md5(f'{SHOP_ID}:{form.money_amount.data}:{SECRET_ONE}:{current_user.id}'.encode('utf-8'))
        return redirect(f'{HOST}?m={SHOP_ID}&oa={form.money_amount.data}&o={current_user.id}&s={sign}')
    return render_template('gateway/payment.html', title='Пополнение баланса', form=form)


@blueprint.route('/response', methods=['POST'])
def response():
    params = {
        'shop_id': request.form.get('MERCHANT_ID'),
        'money_amount': request.form.get('AMOUNT'),
        'user_id': request.form.get('MERCHANT_ORDER_ID'),
        'sign': request.form.get('SIGN'),
        'operation_id': request.form.get('intid'),
    }
    if None in params:
        return abort(403)
    if request.environ.get('HTTP_X_REAL_IP', request.remote_addr) not in [
        '136.243.38.147',
        '136.243.38.149',
        '136.243.38.150',
        '136.243.38.151',
        '136.243.38.189',
        '136.243.38.108'
    ]:
        return abort(403)
    sign = md5(f"{SHOP_ID}:{params['money_amount']}:{SECRET_TWO}:{params['user_id']}".encode('utf-8'))
    if sign != params['sign']:
        return abort(403)
    connect = session.create_session()
    user = connect.query(User).filter(User.id == params['user_id']).fisrt()
    user.money += params['money_amount']
    connect.commit()
    return make_response(('YES', 200))


@blueprint.route('/success')
@login_required
def success():
    return render_template('gateway/success.html', title='Успешно')


@blueprint.route('/fail')
@login_required
def fail():
    return render_template('gateway/fail.html', title='Неудачно')
