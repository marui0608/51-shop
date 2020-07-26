import functools

from flask import request, render_template, redirect, url_for, jsonify
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.security import generate_password_hash, check_password_hash

from app.admin import admin
from app.admin.forms import *
from app.models import *
from config import IMG_URL


# 登录装饰器
def ifs_login(func):
    @functools.wraps(func)
    def a(*args, **kwargs):
        cookie = request.cookies.get('manager')
        if not cookie:
            return redirect(url_for('admin.login'))
        else:
            return func(*args, **kwargs)

    return a


'''-------------------------------登录登出注册---------------------------'''


# 注册管理员账号
@admin.route('/register')
def register():
    pwd = generate_password_hash('123456')
    adminuser = Admin(manager='twogroup', password=pwd)
    db.session.add(adminuser)
    # db.session.commit()
    return redirect(url_for('admin.login'))


# 管理员登录
@admin.route('/login', endpoint='login', methods=['GET', 'POST'])
def login():
    con = {}
    # 获取cookie值判断是否已登录
    cookie = request.cookies.get('manager')
    if cookie:
        return redirect(url_for('admin.index'))
    forms = AdminLoginForm(request.form)
    if request.method == 'POST':
        if forms.validate():
            manager = forms.manager.data
            password = forms.password.data
            adminuser = Admin.query.filter(Admin.manager == manager).all()
            if adminuser:
                if check_password_hash(adminuser[0].password, password):
                    # 存入cookie值
                    c = redirect(url_for('admin.index'))
                    c.set_cookie('manager', manager)
                    return c
                else:
                    con = {'msg': '密码错误'}
            else:
                con = {'msg': '您不是管理员，无法登陆'}
        else:
            con = {'msg': '账号密码格式错误'}
    return render_template('admin/login.html', **con)


# 管理员退出
@admin.route('/logout')
@ifs_login
def logout():
    out = redirect(url_for('admin.login'))
    out.delete_cookie('manager')
    return out


'''-------------------------------商品管理---------------------------'''


# 后台首页--商品管理/列表
@admin.route('/', endpoint='index')
@ifs_login
def index():
    gl = 'goods'
    page = request.args.get('page', 1, type=int)
    page_datas = Goods.query.filter().paginate(page=page, per_page=15)
    return render_template('admin/index.html', page_data=page_datas, gl=gl)


# 商品详情
@admin.route('/goods/detail/')
@ifs_login
def goods_detail():
    id = request.args.get('goods_id')
    good = Goods.query.get(id)
    return render_template('admin/goods_detail.html', goods=good)


# 添加商品
@admin.route('/goods/add/', methods=['GET', 'POST'])
@ifs_login
def goods_add():
    forms = AdminGoodsForm(CombinedMultiDict([request.form, request.files]))
    supercat = SuperCat.query.all()  # 大分类
    # 大分类选择
    forms.supercat.choices = [(i.id, i.cat_name) for i in supercat]

    subcat = SubCat.query.filter_by(super_cat_id=forms.supercat.choices[0][0]).all()  # 小分类
    # 小分类选择
    forms.subcat.choices = [(i.id, i.cat_name) for i in subcat]
    if forms.validate_on_submit():
        name = forms.name.data
        supercat = forms.supercat.data
        subcat = forms.subcat.data
        picture = forms.picture.data
        old_price = float(forms.old_price.data)
        new_price = float(forms.old_price.data)
        is_new = int(forms.is_new.data)
        is_sale = int(forms.is_sale.data)
        intro = forms.intro.data
        good = Goods(name=name, supercat_id=supercat, subcat_id=subcat, picture=picture,
                     original_price=old_price, current_price=new_price, is_new=is_new,
                     is_sale=is_sale, introduction=intro)
        db.session.add(good)
        db.session.commit()
        picture.save(IMG_URL + picture.filename)
        return redirect(url_for('admin.index'))
    return render_template("admin/goods_add.html", form=forms)


# 商品修改
@admin.route('/goods/edit/<id>', methods=['GET', 'POST'])
@ifs_login
def goods_edit(id):
    good = Goods.query.get(id)  # 当前商品
    supercat = SuperCat.query.all()  # 大分类
    subcat = SubCat.query.filter_by(super_cat_id=good.supercat_id).all()  # 当前大分类下的小分类
    forms = AdminGoodsForm(CombinedMultiDict([request.form, request.files]))
    # 大分类选择
    forms.supercat.choices = [(i.id, i.cat_name) for i in supercat]
    # 小分类选择
    forms.subcat.choices = [(i.id, i.cat_name) for i in subcat]

    if request.method == 'GET':
        forms.name.data = good.name
        forms.supercat.data = good.supercat_id
        forms.subcat.data = good.subcat_id
        forms.picture.data = good.picture
        forms.old_price.data = good.original_price
        forms.new_price.data = good.current_price
        forms.is_new.data = good.is_new
        forms.is_sale.data = good.is_sale
        forms.intro.data = good.introduction
    elif request.method == 'POST':
        if forms.validate_on_submit():
            good.name = forms.name.data
            good.supercat_id = int(forms.supercat.data)
            good.subcat_id = int(forms.subcat.data)
            good.picture = forms.picture.data
            good.original_price = float(forms.old_price.data)
            good.current_price = float(forms.new_price.data)
            good.is_new = int(forms.is_new.data)
            good.is_sale = int(forms.is_sale.data)
            good.introduction = forms.intro.data
            db.session.commit()
            forms.picture.data.save(IMG_URL + forms.picture.data.filename)
            return redirect(url_for('admin.index'))
        return render_template('admin/goods_edit.html', form=forms, err='验证失败，请重新修改')
    return render_template('admin/goods_edit.html', form=forms)


# 查找子分类
@admin.route('/goods/select_sub_cat', methods=['GET'])
@ifs_login
def select_sub_cat():
    result = {}
    id = request.args.get('super_id', '')
    subcat = SubCat.query.filter(SubCat.super_cat_id == id).all()
    if subcat:
        data = []
        for i in subcat:
            data.append({'id': i.id, 'cat_name': i.cat_name})
        result['status'] = 1
        result['message'] = 'ok'
        result['data'] = data
    else:
        result['status'] = 0
        result['message'] = 'error'
    return jsonify(result)


# 删除商品确认页面
@admin.route('/goods/del_confirm')
@ifs_login
def goods_del_confirm():
    id = request.args.get('goods_id')
    good = Goods.query.get(id)
    return render_template('admin/goods_del_confirm.html', goods=good)


# 商品删除
@admin.route('/goods/del/<id>')
@ifs_login
def goods_del(id):
    good = Goods.query.get(id)
    db.session.delete(good)
    db.session.commit()
    return redirect(url_for('admin.index', page=1))


'''-------------------------------大分类---------------------------'''


# 大分类信息管理
@admin.route('/supercat/list')
@ifs_login
def supercat_list():
    supercats = SuperCat.query.all()
    return render_template('admin/supercat.html', data=supercats)


# 添加大分类
@admin.route('/supercat/add', methods=['GET', 'POST'])
@ifs_login
def supercat_add():
    if request.method == 'POST':
        name = request.form.get('cat_name')
        is_exists = SuperCat.query.filter(SuperCat.cat_name == name).all()
        if not is_exists:
            supercat = SuperCat(cat_name=name)
            db.session.add(supercat)
            db.session.commit()
            return redirect(url_for('admin.supercat_list'))
        return render_template('admin/supercat_add.html', err='已有该大分类！')
    return render_template('admin/supercat_add.html')


# 删除大分类
@admin.route('/supercat/del', methods=['GET', 'POST'])
@ifs_login
def supercat_del():
    if request.method == 'POST':
        # 获取列表式的删除按钮
        ids = request.form.getlist('delid')
        is_exists = [SubCat.query.filter(SubCat.super_cat_id == i).all() for i in ids]
        if is_exists:
            supercats = SuperCat.query.all()
            return render_template('admin/supercat.html', data=supercats, err='请先删除该大分类下的小分类再操作')
        for i in ids:
            SuperCat.query.get(id).delete()
        db.session.commit()
        return redirect(url_for('admin.supercat_list'))


'''-------------------------------小分类---------------------------'''


# 小分类信息管理
@admin.route('/subcat/list')
@ifs_login
def subcat_list():
    subcats = SubCat.query.all()
    return render_template('admin/subcat.html', data=subcats)


# 添加小分类
@admin.route('/subcat/add', methods=['GET', 'POST'])
@ifs_login
def subcat_add():
    supercats = SuperCat.query.all()
    if request.method == 'POST':
        id = request.form.get('super_cat_id')
        name = request.form.get('cat_name')
        is_exists = SubCat.query.filter(SubCat.cat_name == name).all()
        if not is_exists:
            subcat = SubCat(super_cat_id=id, cat_name=name)
            db.session.add(subcat)
            db.session.commit()
            return redirect(url_for('admin.subcat_list'))
        return render_template('admin/subcat_add.html', err='已有该小分类')
    return render_template('admin/subcat_add.html', supercat=supercats)


# 删除小分类
@admin.route('/subcat/del', methods=['GET', 'POST'])
@ifs_login
def subcat_del():
    if request.method == 'POST':
        ids = request.form.get('delid')
        is_exists = [Goods.query.filter(Goods.cat_id == i).all() for i in ids]
        if is_exists:
            subcats = SubCat.query.all()
            return render_template('admin/subcat.html', data=subcats, err='请先删除该小分类下的商品再操作')
        for i in ids:
            SubCat.query.get(id).delete()
        db.session.commit()
        return redirect(url_for('admin.subcat_list'))


'''-------------------------------销量---------------------------'''


# 销量排行
@admin.route('/topgoods')
@ifs_login
def topgoods():
    gl = 'xl'
    goods_order = OrdersDetail.query.order_by(OrdersDetail.number.desc()).limit(10).all()
    return render_template('admin/topgoods.html', data=goods_order, gl=gl)


'''-------------------------------会员---------------------------'''


# 会员管理
@admin.route('/user/list')
@ifs_login
def user_list():
    gl = 'user'
    page = request.args.get('page', 1)
    users_page = User.query.filter().paginate(page=page, per_page=10)
    return render_template('admin/user_list.html', page_data=users_page, gl=gl)


'''-------------------------------订单---------------------------'''


# 订单管理
@admin.route('/orders/list')
@ifs_login
def orders_list():
    gl = 'order'
    page = request.args.get('page', 1)
    search = request.args.get('keywords', '')
    if search:
        orders_page = Orders.query.filter(Orders.id == search).paginate(page=page, per_page=10)
    else:
        orders_page = Orders.query.filter().paginate(page=page, per_page=10)
    return render_template('admin/orders_list.html', page_data=orders_page, gl=gl)


# 订单详情
@admin.route('/orders/detail')
@ifs_login
def orders_detail():
    gl = 'order'
    id = request.args.get('order_id')
    order = OrdersDetail.query.filter(OrdersDetail.order_id == 21).all()
    return render_template('admin/orders_detail.html', data=order, gl=gl)

#  自定义命令：生成管理员账号
# @app.cli.command()
# @click.option('--username',prompt=True,help='管理员账号：')
# @click.option('--password',prompt=True,help='密码：',confirmation_prompt=True,hide_input=True)
# def admin(username,password):
#     user = Admin.query.filter(Admin.manager=username)
#     if user is not None:
#         click.echo('更新管理员用户')
#         user.manager= username
#         user.set_password = password
#     else:
#         click.echo('创建管理员用户')
#         user = Admin(manager=username,name='admin')
#         user.set_password(password)
#         db.session.add(user)
#     db.session.commit()
#     click.echo('管理员账号跟新/创建完成')
