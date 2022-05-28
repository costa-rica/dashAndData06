# from time import strftime
from flask import Blueprint
from flask import render_template, url_for, redirect, flash, request,current_app
import os
from datetime import datetime
import time
from sqlalchemy import func
import json
from flask_login import login_user, current_user, logout_user, login_required
from app_package.blog.forms import BlogPostForm
from app_package.blog.utils import last_first_list_util, wordToJson
from app_package.models import Users, Posts, Postshtml, Postshtmltagchars
from app_package import db
from sqlalchemy import func 
import logging
from app_package.utils import logs_dir
from logging.handlers import RotatingFileHandler


#Setting up Logger
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')
formatter_terminal = logging.Formatter('%(asctime)s:%(filename)s:%(name)s:%(message)s')

logger_blog = logging.getLogger(__name__)
logger_blog.setLevel(logging.DEBUG)
logger_terminal = logging.getLogger('terminal logger')
logger_terminal.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(os.path.join(logs_dir,'blog.log'), mode='a', maxBytes=5*1024*1024,backupCount=2)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter_terminal)

logger_terminal.handlers.clear()
logger_blog.addHandler(file_handler)
logger_terminal.addHandler(stream_handler)

#End set up logger


# blog = Blueprint('blog', __name__, __name__,url_prefix='/blog')
blog = Blueprint('blog', __name__)
    
@blog.route("/blog", methods=["GET"])
def blog_index():
    logger_terminal.info(f'****Blog Index Accessed*****')

    #sorted list of published dates
    date_pub_list=[i.date_published for i in Posts.query.all()]
    # create new list of sorted datetimes into increasing order
    sorted_date_pub_list = sorted(date_pub_list)
    #reverse new list
    sorted_date_pub_list.sort(reverse=True)

    #make dict of title, date_published, description
    items=['blog_title', 'blog_description','date_published']
    posts_list = Posts.query.all()
    blog_dict_for_index_sorted={}
    for i in sorted_date_pub_list:
        for post in posts_list:
            if post.date_published == i:
                temp_dict={key: (getattr(post,key) if key!='date_published' else getattr(post,key).strftime("%m/%d/%Y") ) for key in items}
                temp_dict['blog_name']='blog'+str(post.id).zfill(4)
                # temp_dict={key: (getattr(post,key) if key=='date_published' else getattr(post,key)[:9] ) for key in items}
                blog_dict_for_index_sorted[post.id]=temp_dict
                posts_list.remove(post)

    return render_template('blog/index.html', blog_dicts_for_index=blog_dict_for_index_sorted)
    
@blog.route("/blog/<blog_name>", methods=["GET"])
def blog_template(blog_name):
    logger_blog.info(f'**Accessed:: {blog_name}')
    blog_dict={}
    post_id=int(blog_name[4:])
    post=Postshtml.query.filter_by(post_id=post_id).all()
    blog_dict={i.word_row_id: [i.row_tag,i.row_going_into_html] for i in post}

    return render_template('blog/template.html', blog_dict=blog_dict)


@blog.route("/post", methods=["GET","POST"])
@login_required
def blog_post():
    blog_word_docs_folder=os.path.join(current_app.static_folder, 'blog_word_docs')
    form = BlogPostForm()

    if request.method == 'POST' and 'word_doc_name' in request.files:
        formDict = request.form.to_dict()
        filesDict = request.files.to_dict()

        uploaded_file = request.files['word_doc_name']
        word_doc_file_name = uploaded_file.filename
        
        # if /static/blog_word_docs don't exist      
        try:
            os.makedirs(blog_word_docs_folder)
        except:
            logger_terminal.info(f'folder exists')
            
        uploaded_file.save(os.path.join(blog_word_docs_folder,word_doc_file_name))

        if len(Posts.query.all())>0:
            blog_name = 'blog'+str(db.session.query(func.max(Posts.id)).first()[0]+1).zfill(4)
        else:
            blog_name = 'blog0001'


        post_id = wordToJson(word_doc_file_name, blog_word_docs_folder, blog_name,
            formDict.get('date_published'), description=formDict.get('blog_description'),
            link=formDict.get('link_to_app'))
        
        # TODO: fix consecutive_row_util
        # consecutive_row_util(post_id)

        flash(f'Post added successfully!', 'success')
        return redirect(url_for('blog.blog_post'))
    return render_template('blog/post.html', form=form)


@blog.route("/blog_user_home", methods=["GET","POST"])
@login_required
def blog_user_home():
    logger_terminal.info(f'**Accessed:: blog_user_home')
    all_posts=Posts.query.all()
    posts_details_list=[]
    for i in all_posts:
        posts_details_list.append([i.id, i.blog_title, i.date_published.strftime("%m/%d/%Y"),
            i.blog_description, i.word_doc])

    column_names=['id', 'blog_title','date_published',
         'blog_description','word_doc', 'edit']

    if request.method == 'POST':
        formDict=request.form.to_dict()
        print('formDict::', formDict)
        if formDict.get('delete_record_id')!='':
            post_id=formDict.get('delete_record_id')
            return redirect(url_for('blog.blog_delete', post_id=post_id))
        elif formDict.get('edit_post_button')!='':
            print('post to delte:::', formDict.get('edit_post_button')[9:],'length:::', len(formDict.get('edit_post_button')[9:]))
            post_id=int(formDict.get('edit_post_button')[10:])
            return redirect(url_for('blog.blog_edit', post_id=post_id))
    return render_template('blog/user_home.html', posts_details_list=posts_details_list, len=len,
        column_names=column_names)


@blog.route("/delete/<post_id>", methods=['GET','POST'])
@login_required
def blog_delete(post_id):
    print('****In delete route****')
    print('post_id:::::', post_id)

    post_to_delete = Posts.query.get(int(post_id))
    blog_name = 'blog'+post_id.zfill(4)
    print(post_to_delete)
    
    #delete word document
    word_doc_path = os.path.join(current_app.static_folder,'blog_word_docs')
    try:
        os.remove(os.path.join(word_doc_path, post_to_delete.word_doc))
    except:
        logger_blog.info(f'no word document file exists')
    
    #delete images folder
    images_folder = os.path.join(current_app.static_folder, 'images')
    try:
        os.rmdir(os.path.join(images_folder, blog_name)) 
    except:
        logger_blog.info(f'no images folder for this blog exists')

    db.session.query(Posts).filter(Posts.id==post_id).delete()
    db.session.query(Postshtml).filter(Postshtml.post_id==post_id).delete()
    db.session.query(  Postshtmltagchars).filter(  Postshtmltagchars.post_id==post_id).delete()
    db.session.commit()

    logger_blog.info(f'blog post deleted for: {post_id}')
    return redirect(url_for('blog.blog_user_home'))


@blog.route("/edit", methods=['GET','POST'])
@login_required
def blog_edit():

    post_id = int(request.args.get('post_id'))
    post = db.session.query(Posts).filter_by(id = post_id).first()
    postHtml_list = db.session.query(Postshtml).filter_by(post_id = post_id).all()[1:]
    published_date = post.date_published.strftime("%Y-%m-%d")
    print('published_date::', type(published_date), published_date)


    # get list of word_row_id for post_id
    # put last object in first object's place
    merge_row_id_list = last_first_list_util(post_id)[1:]

    column_names = ['word_row_id', 'row_tag', 'row_going_into_html','merge_with_bottom']
    if request.method == 'POST':
        formDict=request.form.to_dict()
        
        post.blog_title = formDict.get('blog_title')
        post.blog_description = formDict.get('blog_description')
        post.date_published = datetime.strptime(formDict.get('blog_pub_date'), '%Y-%m-%d')
        db.session.commit()

        #update row_tag and row_going_into_html in Postshtml
        postHtml_update = db.session.query(Postshtml).filter_by(post_id = post_id)
        
        #if title changed update first row psotHtml
        postHtml_title = postHtml_update.filter_by(word_row_id = 1).first()
        if post.blog_title != postHtml_title.row_going_into_html:
            postHtml_title.row_going_into_html = post.blog_title
            db.session.commit()

        for i,j in formDict.items():
            
            if i.find('row_tag:'+str(post_id))>-1:
                word_row_id_temp = int(i[len('row_tag:'+str(post_id))+1:])
                update_row_temp=postHtml_update.filter_by(word_row_id = word_row_id_temp).first()
                update_row_temp.row_tag = j
                db.session.commit()
            if i.find('row_html:'+str(post_id))>-1:
                word_row_id_temp = int(i[len('row_html:'+str(post_id))+1:])
                update_row_temp=postHtml_update.filter_by(word_row_id = word_row_id_temp).first()
                update_row_temp.row_going_into_html = j
                db.session.commit()
        
        if formDict.get('delete_word_row'):
            row_to_delete = int(formDict.get('delete_word_row'))
            db.session.query(Postshtml).filter_by(post_id = post_id,word_row_id = row_to_delete).delete()
            db.session.query(Postshtmltagchars).filter_by(post_id = post_id,word_row_id = row_to_delete).delete()
            db.session.commit()

        else:

            for i in formDict.keys():
                if i[:1]=='_':
                    formDict_key = i
                    row_to_move = int(i[6:])
            
            row_to_keep=int(formDict.get(formDict_key)[8:])
            row_to_keep_obj=db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id=row_to_keep).first()
            row_to_move_obj=db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id=row_to_move).first()
            row_to_keep_obj.row_going_into_html=row_to_keep_obj.row_going_into_html+'<br>'+row_to_move_obj.row_going_into_html
            
            db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id=row_to_move).delete()
            db.session.query(Postshtmltagchars).filter_by(post_id=post_id, word_row_id=row_to_move).delete()
            db.session.commit()

        return redirect(url_for('blog.blog_edit',post_id=post_id ))

    return render_template('blog/edit_template.html',post_id=post_id, post=post,
        postHtml_list=zip(postHtml_list,merge_row_id_list) , column_names=column_names, published_date=published_date )


