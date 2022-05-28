from docx2python import docx2python
import os
import json
from flask import current_app
from flask_login import current_user
import datetime
from app_package.models import Posts, Postshtml, Postshtmltagchars
from app_package import db


def last_first_list_util(post_id):
    posts_html_list = Postshtml.query.filter_by(post_id = post_id).all()
    word_row_id_list = [i.word_row_id for i in posts_html_list]
    last_item = word_row_id_list[-1:]
    merge_row_id_list = last_item+word_row_id_list[:-1]
    return merge_row_id_list

#this def is used for going back previous 2 html_rows
def last_first_list_util_2():
    merge_row_id_list = last_first_list_util()
    # word_row_id_list = [i.word_row_id for i in posts_html_list]
    last_item = merge_row_id_list[-1:]
    merge_row_id_list_2 = last_item+merge_row_id_list[:-1]
    return merge_row_id_list_2


def wordToJson(word_doc_file_name, word_doc_path, blog_name, date_published, description='',link=''):
    
    # print('word_doc_path:::', word_doc_path)
    # print('word_doc_file_name:::', word_doc_file_name)

    doc_result_html = docx2python(os.path.join(word_doc_path,word_doc_file_name),html=True)
    
    #all images saved
    images_folder = os.path.join(current_app.static_folder, 'images')
    #Save pictures to 
    docx2python(os.path.join(word_doc_path,word_doc_file_name), os.path.join(images_folder,blog_name))

    new_post = Posts()
    new_post.user_id = current_user.id
    new_post.date_published = datetime.datetime.strptime(date_published,'%Y-%m-%d')
    new_post.word_doc = word_doc_file_name
    if description!='':
        new_post.blog_description=description
    if link!='':
        new_post.link_to_app=link
    db.session.add(new_post)
    db.session.commit()

    #get post just updated
    new_post = db.session.query(Posts).filter(
        Posts.date_published == datetime.datetime.strptime(date_published,'%Y-%m-%d'),
        Posts.word_doc == word_doc_file_name).first()
    post_id = new_post.id


    count=1

    print('***doc_result_html.document[0] (in wordToJson)*** ')
    # print(doc_result_html.document[0])

    for i in doc_result_html.document[0][0][0]:

        if count ==1:
            row_tag_characters = ['']
            row_tag = 'h1'
            row_going_into_html = i
        elif count>1 and i[:4]=='<h1>':
            row_tag_characters = ['<h1>']
            row_tag = 'h3'
            row_going_into_html = i[4:-5] 
        elif i[:3]=='--\t':
            if i.find('font-size:20pt')!=-1:
                row_tag_characters = ['--\t','font-size:20pt']
                row_tag = 'ul and indent'
                #this means font is 10 point in word, and indent
                row_going_into_html = i[len('--\t<span style="font-size:20pt">'):-len('</span>')]
    #             blog_dict[count]=['ul and indent',line]
            else:
                #no indent
                row_tag_characters = ['--\t']
                row_tag = 'ul'
                row_going_into_html = i[2:]
    #             blog_dict[count]=['ul',i[2:]]
        elif i[:4]=='Gif ' or i[:4]=='Figu' or i[:4]=='Code':
            row_tag_characters = [i[:4]]
            row_tag = 'image_title'
            row_going_into_html = i
    #         blog_dict[count]=['image_title',i]
        elif i[:10]=='----media/':
            row_tag_characters = ['----media/']
            row_tag = 'image'
            row_going_into_html = f"../static/images/{'blog'+str(post_id).zfill(4)}/{i[10:-4]}"
    #         image_name= i[10:-4]
    #         html_image_path=f"../static/images/{blog_name}/{image_name}"
    #         blog_dict[count]=['image',html_image_path]
        elif i[:3]=='<u>' or i[:3]=='<a ':
            row_tag_characters = [i[:3]]
            row_tag = 'html'
            row_going_into_html = i
    #         blog_dict[count]=['html',i]
        elif i[:3]=='<h1':
            row_tag_characters = [i[:3]]
            row_tag = 'html'
            row_going_into_html = i
    #         blog_dict[count]=['h2',i[4:-5]]
        elif i[:29]=='<span style="font-size:20pt">':
            row_tag_characters = [i[:29]]
            row_tag = 'indent'
            row_going_into_html = i[29:-len('</span>')]
    #         blog_dict[count]=['indent',i[29:-len('</span>')]]
        #code snippet
        elif i[:41]=='<span style="background-color:lightGray">':
            row_tag_characters = [i[:41]]
            row_tag = 'codeblock_type00'
            row_going_into_html = i[41:-len('</span>')]
    #         blog_dict[count]=['codeblock',i[41:-len('</span>')]]
        #codeblock_type1
        elif i.find(r'<span style="color:FFFFFF;font-size:22pt">')>-1:
            string='<span style="color:FFFFFF;font-size:22pt">'
            # adj=i.find(string)
            # print('codeblock_type1 - adjustment worked?:::',adj )
            len_string=len(string)
            row_tag_characters = [string]
            row_tag = 'codeblock_type01'
            row_going_into_html = i[len_string:-len('</span>')]
    #         blog_dict[count]=['codeblock_type1',i[27+adj:-len('</span>')]]
        elif i=='':
            row_tag_characters = ['']
            row_tag = 'new lines'
            row_going_into_html = i
    #         blog_dict[count]=['new lines',i]
        else:
            row_tag_characters = ['everything else']
            row_tag = 'everything else'
            row_going_into_html = i
        
    #Start build post to HTML breakdown
        new_PostsToHtml = Postshtml()
        new_PostsToHtml.word_row_id=count
        
        new_PostsToHtml.row_tag= row_tag
        new_PostsToHtml.row_going_into_html = row_going_into_html
        new_PostsToHtml.user_id=current_user.id
        new_PostsToHtml.post_id=post_id
        db.session.add(new_PostsToHtml)
        db.session.commit()
        #get id of the post html row
        word_row_id = new_PostsToHtml.id
        
        #Tag Characgters
        for i in row_tag_characters:
            post_tag_chars =Postshtmltagchars()
            post_tag_chars.post_tag_characters=i
            post_tag_chars.word_row_id = word_row_id
            post_tag_chars.post_id = post_id
            db.session.add(post_tag_chars)
            db.session.commit()
        
        count+=1


    #Update new_post title, description
    new_post.blog_title=db.session.query(Postshtml).filter_by(word_row_id=1, post_id=post_id).first().row_going_into_html
    db.session.commit()

    # return blog_dict
    return post_id



####This would be nice but there are not word(i.e. docx) tags to identify code

# def consecutive_row_util(post_id):
#     #merge_row_id_list is basically Postshtml.id - 1 (i.e the row above)
#     merge_row_id_list=last_first_list_util(post_id)
#     merge_row_id_list_2=last_first_list_util_2()
#     post_html_row_list = db.session.query(Postshtml).filter_by(post_id=post_id).all()
    
#     for post_html_row,i_m1,i_m2 in zip(post_html_row_list, merge_row_id_list,merge_row_id_list_2):
#         if post_html_row.word_row_id==2:
#             previous_row_obj = db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id=i_m1).first()
#             if post_html_row.row_tag == previous_row_obj.row_tag and 'codeblock' in post_html_row.row_tag:
#                 #add current row to previous row
#                 previous_row_obj.row_going_into_html = previous_row_obj.row_going_into_html + '<br>' +\
#                     post_html_row.row_going_into_html
#                 #change current row postshtmltagchars.word_row_id to previous_row.word_row_id
#                 postshtmltagchars_list = db.session.query(Postshtmltagchars).filter_by(
#                     post_id=post_id,word_row_id = post_html_row.word_row_id).all()
#                 for x in postshtmltagchars_list:
#                     x.word_row_id = i_m1

#                 #delete post_html_row object
#                 db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id = post_html_row.word_row_id).delete()
#                 db.session.commit()

#         if post_html_row.word_row_id>2:
#             previous_row_obj = db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id=i_m1).first()
#             previous_row_obj_2 = db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id=i_m2).first()
#             if post_html_row.row_tag == previous_row_obj_2.row_tag and \
#                 'codeblock' in post_html_row.row_tag and \
#                 'new lines' in previous_row_obj.row_tag:
#                 #add current and previous row to previous row 2
#                 previous_row_obj_2.row_going_into_html = previous_row_obj_2.row_going_into_html + '<br>' + \
#                     previous_row_obj.row_going_into_html + '<br>' + post_html_row.row_going_into_html
#                 #change current row postshtmltagchars.word_row_id to previous_row.word_row_id
#                 postshtmltagchars_list = db.session.query(Postshtmltagchars).filter_by(
#                     post_id=post_id,word_row_id = post_html_row.word_row_id).all()
#                 for x in postshtmltagchars_list:
#                     x.word_row_id = i_m2
#                 postshtmltagchars_list_1 = db.session.query(Postshtmltagchars).filter_by(
#                     post_id=post_id,word_row_id = previous_row_obj.word_row_id).all()
#                 for x in postshtmltagchars_list_1:
#                     x.word_row_id = i_m2
#                 #delete post_html_row and previous_row_obj object
#                 db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id = post_html_row.word_row_id).delete()
#                 db.session.query(Postshtml).filter_by(post_id=post_id, word_row_id = previous_row_obj.word_row_id).delete()
#                 db.session.commit()


#     newPostRows=db.session.query(Postshtml).filter_by(post_id=post_id).all()

#     return newPostRows

