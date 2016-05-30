# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, make_response
from flask_login import login_required, login_user, logout_user, current_user

from adoptarbol.extensions import login_manager, pages, api_manager
from adoptarbol.public.forms import LoginForm, SponsorshipForm
from adoptarbol.user.forms import RegisterForm
from adoptarbol.user.models import User
from adoptarbol.tree.models import Tree, Sponsorship
from adoptarbol.utils import flash_errors

from random import choice
import requests
from itertools import chain

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/page/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    template = page.meta.get('template', 'public/flatpages.html')
    return render_template(template, page=page)

@blueprint.route('/api/pages/<path:path>/_random')
def get_random_item(path):
    page = pages.get_or_404(path)
    lines =  [line for line in page.body.split('\n') if line.startswith('- ')]
    return choice(lines)[2:]

@blueprint.route('/api/pages/<path:path>')
def get_page(path):
    page = pages.get_or_404(path)
    result = page.meta
    result['body'] = page.body
    result['html'] = page.html
    result['path'] = page.path
    return jsonify(page.meta)


@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/selected/<int:tree_id>')
def home(tree_id=None):
    """Home page."""
    if not tree_id:
        tree = Tree.random()
    else:
        tree = Tree.get_by_id(tree_id)
    tree.comments = tree.comments or get_random_item('sobremi')

    nav = {}
    nav['before'] = tree.before.id
    nav['after'] = tree.after.id

    count = {}
    count['total'] = Tree.query.count()
    count['sponsored'] = Sponsorship.query.count() 
    # clever way to get next multiple of 5
    count['target'] = count['sponsored'] + (5 - count['sponsored'] % 5)
    if count['target'] > count['total']:
        count['target'] = count['total']

    banner = {}
    banner['a'] = get_random_item('frases')
    banner['c'] = get_random_item('sabiasque')
    banner['d'] = get_random_item('porqueadoptar')

    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash('You are logged in.', 'success')
            redirect_url = request.args.get('next') or url_for('user.members')
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('public/home.html', loginform=form, tree=tree, count=count, \
                            image=tree.image, banner=banner, nav=nav)

@blueprint.route('/pay/', methods=['POST'])
def pay():
    tree = Tree.get_by_id( request.form['tree_id'] )

    # Paypal
    if 'pp_submit' in request.form:
        return str(Sponsorship.create(
                       tree_id=tree.id,
                       user_id=current_user.get_id(),
                       amount=tree.cost,
                       currency=tree.currency,
                       reference=str(jsonify({'opcode':request.form['opcode'], \
                                          'name':request.form['name'], \
                                          'email':request.form['email']})),
                       status='pending'))

    flash(u'PROCESO DE PAGO: Operador desconocido.')
    return redirect(url_for('public.home'))

@blueprint.route('/cancel/')
def cancel():
    flash(u'PROCESO DE PAGO: Operacion cancelada.')
    return redirect(url_for('public.home'))

@blueprint.route('/confirm2/')
def confirm2():
    flash(u'QUERIDO AMIGO: Muchas gracias por tu aporte. Nos estaremos comunicando contigo a la brevedad.')
    return redirect(url_for('public.home'))

@blueprint.route('/confirm/')
def confirm():
    flash(u'QUERIDO AMIGO: Muchas gracias por tu aporte. Nos estaremos comunicando contigo a la brevedad.')
    return redirect(url_for('public.home'))

@blueprint.route('/adopt/')
@blueprint.route('/adopt/<int:tree_id>')
def adopt(tree_id=None):
    """adopt a tree."""
    if not tree_id:
        tree = Tree.random()
        return redirect(url_for('public.adopt', tree_id=tree.id))
    else:
        tree = Tree.get_by_id(tree_id)
    tree.comments = tree.comments or get_random_item('sobremi')

    terminos = pages.get('terminosadopcion')

    form = SponsorshipForm(request.form)

    explanation = { 'wood':u'Es maderable',
                    'bird':u'Es hogar de aves',
                    'mammal':u'Es hogar de mamíferos',
                    'soil':u'Es mejorador del suelo',
                    'community':u'Es importante para las comunidades nativas',
                    'medicine':u'Es medicinal' }

    functions = []
    for function in tree.function.split(","):
        functions.append ( { 'icon':"%s.png" % function,
                             'desc':explanation[function] } )


    return render_template('public/adopt.html', tree=tree, terminos=terminos, \
                            image=tree.image, form=form, functions=functions)


@blueprint.route('/adopt2/')
@blueprint.route('/adopt2/<int:tree_id>')
def adopt2(tree_id=None):
    """fake adopt a tree."""
    if not tree_id:
        tree = Tree.random()
        return redirect(url_for('public.adopt2', tree_id=tree.id))
    else:
        tree = Tree.get_by_id(tree_id)
    tree.comments = tree.comments or get_random_item('sobremi')

    terminos = pages.get('terminosadopcion')

    form = SponsorshipForm(request.form)

    explanation = { 'wood':u'Es maderable',
                    'bird':u'Es hogar de aves',
                    'mammal':u'Es hogar de mamíferos',
                    'soil':u'Es mejorador del suelo',
                    'community':u'Es importante para las comunidades nativas',
                    'medicine':u'Es medicinal' }

    functions = []
    for function in tree.function.split(","):
        functions.append ( { 'icon':"%s.png" % function,
                             'desc':explanation[function] } )


    return render_template('public/adopt2.html', tree=tree, terminos=terminos, \
                            image=tree.image, form=form, functions=functions)


@blueprint.route('/buscar/')
def pick(page=1):
    """pick a tree."""
    trees = Tree.query.all()
    return render_template('public/map.html', trees=trees)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(username=form.username.data, email=form.email.data, password=form.password.data, active=True)
        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)

@blueprint.route('/debug/')
def debug():
    raise Error

# https://gist.github.com/doobeh/1869698
# https://gist.github.com/cbsmith/5069769
#demonstration of hack to declaratively set param_storage_class declaratively using a decorator
#also demonstrates how to write an IPN handler with Flask

#Normally this parameter would come from a config
IPN_URLSTRING = 'https://www.sandbox.paypal.com/cgi-bin/webscr'
IPN_VERIFY_EXTRA_PARAMS = (('cmd', '_notify-validate'),)

def ordered_storage(f):
    import werkzeug.datastructures
    import flask
    def decorator(*args, **kwargs):
        flask.request.parameter_storage_class = werkzeug.datastructures.ImmutableOrderedMultiDict
        return f(*args, **kwargs)
    return decorator
    
@blueprint.route('/ipn', methods=['POST'])
@ordered_storage
def paypal_webhook():
    #probably should have a sanity check here on the size of the form data to guard against DoS attacks
    verify_args = chain(request.form.iteritems(), IPN_VERIFY_EXTRA_PARAMS)
    verify_string = '&'.join(('%s=%s' % (param, value) for param, value in verify_args))
    with closing(urlopen(IPN_URLSTRING, data=verify_string)) as paypal_verify_request:
        response_string = paypal_verify_request.read()
        if response_string != 'VERIFIED':
            raise ValueError('Did not receive expected IPN confirmation from PayPal')
    return make_response('')
