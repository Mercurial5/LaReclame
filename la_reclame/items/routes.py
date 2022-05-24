from flask import render_template, session, request, flash
from flask import redirect, url_for
from la_reclame.items import items
from la_reclame.models import Items, Users, Categories, PriceTypes, Reviews, Ratings
from la_reclame import db
from utils import auth_required, picturesDB


@items.route('/')
@auth_required
def items_home():
    search = request.values.get('search', '')
    if search != '':
        title_like = Items.title.like("%{}%".format(search))
        description_like = Items.description.like("%{}%".format(search))
        items_list = Items.query.filter(title_like | description_like)
    else:
        items_list = Items.query

    filter_by = request.values.get('filter_by', '')
    if filter_by != '':
        items_list = items_list.filter_by(category_id=filter_by).all()
    else:
        items_list = items_list.all()

    return render_template('items.html', user=session['user'], items=items_list, filter_by=filter_by, search=search)


@items.route('/<item_id>')
@auth_required
def item_page(item_id: int):
    item = Items.query.get(item_id)
    if item is None:
        return '404\nItem not found'

    pictures = [item.main_picture] if item.main_picture else []
    pictures.extend(item.pictures.split(',') if item.pictures else [])
    item.all_pictures = pictures

    user = Users.query.get(item.user_id)

    return render_template('item-page.html', user=user, item=item, reviews=Reviews.query.filter_by(item_id=item_id).all())


@items.route('/add-item', methods=['GET', 'POST'])
@auth_required
def add_item():
    categories = Categories.query.order_by(Categories.id.asc()).all()
    if request.method == 'GET':
        return render_template('add-item.html', user=session['user'], categories=categories)

    main_picture = request.files.get('item-main-picture')
    main_picture = picturesDB.add_picture('item-pictures', main_picture) if main_picture.filename != '' else None

    image_paths = [picturesDB.add_picture('item-pictures', file)
                   for file in request.files.getlist('item-pictures') if file.filename != '']

    category_type = request.form.get('category-type')
    category_id = Categories.query.with_entities(Categories.id).filter_by(category_name=category_type).first()[0]

    title = request.form.get('item-title')
    description = request.form.get('item-description')

    price_type = PriceTypes[request.form.get('price-type').lower()]
    price = request.form.get('item-price', None)
    if price_type == PriceTypes.fixed and price is None:
        flash('At fixed price type you must fill price as well', 'danger')
        return render_template('add-item.html', user=session['user'], categories=categories)
    elif price_type == PriceTypes.fixed and price is not None and int(price) < 1:
        flash('You should write appropriate price for the item', 'danger')
        return render_template('add-item.html', user=session['user'], categories=categories)

    item = Items(user_id=session['user'].id, title=title, description=description,
                 pictures=','.join(image_paths), main_picture=main_picture, category_id=category_id,
                 price_type=price_type, price=price if price else 0)

    db.session.add(item)
    db.session.commit()

    flash('Item is added!', 'success')
    return redirect(url_for('items.add_item'))


@items.route('/<item_id>/add/review', methods=['GET', 'POST'])
@auth_required
def add_review(item_id: int):

    user_id = session['user'].id
    title = request.form.get('title')
    description = request.form.get('description')
    rating_score = int(request.form.get('rating'))

    if Items.query.get(item_id) is None:
        flash('Item with such ID was not found!', 'danger')

    review = Reviews(item_id=item_id, user_id=user_id, title=title, description=description, rating=rating_score)

    item = Items.query.get(item_id)
    rating = Ratings.query.filter_by(user_id=item.user_id).first()

    if rating is None:
        rating = Ratings(user_id=item.user_id, rating=rating_score, review_count=1)
        db.session.add(rating)
    else:
        rating.rating += rating_score
        rating.review_count += 1

    db.session.add(review)
    db.session.commit()

    flash('Review is added!', 'success')
    return redirect(url_for('items.item_page', item_id=item_id))