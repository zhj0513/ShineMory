import os
import time

from flask import Blueprint, request, current_app, abort
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource

from app import pics, db
from app.models import User, Article, Zan, Comment

bp = Blueprint('article', __name__)
api = Api(bp)


@api.resource('/')
class ArticleList(Resource):
    @jwt_required
    def get(self):  # 获取推文列表 is_self参数决定获取所有人还是自己的推文
        user = User.get_current_user()
        is_self = request.args.get('is_self')
        if not is_self:
            follow_ids = [user.id for user in user.follows.all()] if user.follows.all() else []  # 所有关注者的id
            follow_ids.append(user.id)  # 自己和关注着的id
        else:
            follow_ids = [user.id]
        articles = Article.query.filter(Article.user_id.in_(follow_ids)).all()
        articles_list = [article.to_dict() for article in articles]
        return articles_list

    @jwt_required
    def patch(self):  # 上传一张图片
        pic = request.files['pic']
        try:
            filename = pics.save(pic, name=str(post_time) + user.username + '.')
            pic_src = os.path.join(request.url_root, 'static', 'article_pic', filename)
        except Exception:
            abort(400, '文件格式错误或文件名全为中文字符')
        return {"pic_src": pic_src}

    @jwt_required
    def post(self):  # 发送推文 还差图片上传
        user = User.get_current_user()
        data = request.form
        body = data.get('body')
        pic_src = data.get('pic_src')
        post_time = int(time.time() * 1000)

        # pic = request.files['pic']
        # try:
        #     filename = pics.save(pic, name=str(post_time)+user.username+'.')
        #     pic_src = os.path.join(request.url_root, 'static', 'article_pic', filename)
        # except Exception:
        #     abort(400, '文件格式错误或文件名全为中文字符')
        article = Article(body=body, time=post_time, user_id=user.id, pic_src=pic_src, video_src='')
        article.save_to_db()
        return 200

    @jwt_required
    def delete(self):  # 删除推文
        id = request.args.get('article_id')
        article = Article.query.get(id)
        if article.pic_src:
            filename = article.pic_src.rsplit('/', 1)[1]
            pic_path = os.path.join(current_app.config['UPLOADED_PICS_DEST'], filename)
            if os.path.exists(pic_path):
                os.remove(pic_path)
        db.session.delete(article)
        db.session.commit()
        return 200


@api.resource('/zan')
class ArticleZan(Resource):
    @jwt_required
    def put(self):  # 点赞
        current_user = User.get_current_user()
        article_id = request.json.get('article_id')
        comment_id = request.json.get('comment_id')
        zan_time = int(time.time() * 1000)
        if article_id:
            zan = Zan(user_id=current_user.id, article_id=article_id, time=zan_time)
            zan.save_to_db()
            article = Article.query.get(article_id)
            return {'article_id': article.id, 'zan_num': article.zans.count()}
        elif comment_id:
            zan = Zan(user_id=current_user.id, comment_id=comment_id, time=zan_time)
            zan.save_to_db()
            comment = Comment.query.get(comment_id)
            return {'comment_id': comment.id, 'zan_num': comment.zans.count()}
        else:
            abort(400, '操作失败')

    @jwt_required
    def delete(self):  # 取消点赞
        current_user = User.get_current_user()
        article_id = request.args.get('article_id')
        comment_id = request.args.get('comment_id')
        if article_id:
            zan = Zan.query.filter_by(user_id=current_user.id, article_id=article_id).first()
            db.session.delete(zan)
            db.session.commit()
            article = Article.query.get(article_id)
            return {'article_id': article.id, 'zan_num': article.zans.count()}
        elif comment_id:
            zan = Zan.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()
            db.session.delete(zan)
            db.session.commit()
            comment = Comment.query.get(comment_id)
            return {'comment_id': comment.id, 'zan_num': comment.zans.count()}
        else:
            abort(400, '操作失败')


@api.resource('/comment')
class ArticleComment(Resource):
    @jwt_required
    def get(self):  # 获取评论列表
        article_id = request.args.get('article_id')
        comments = Comment.query.filter_by(article_id=article_id).all()
        comments_list = [comment.to_dict() for comment in comments]
        return comments_list

    @jwt_required
    def post(self):  # 发送评论
        current_user = User.get_current_user()
        article_id = request.json.get('article_id')
        body = request.json.get('body')
        comment_time = int(time.time() * 1000)
        comment = Comment(body=body, user_id=current_user.id, article_id=article_id, time=comment_time)
        comment.save_to_db()
        return 200

    @jwt_required
    def delete(self):  # 删除评论
        comment_id = request.args.get('comment_id')
        comment = Comment.query.get(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return 200
