import unittest
from __init__ import app, db
from flask import Flask, json
import requests


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        with app.test_request_context():
            db.create_all()
            user = {
                "tipo":'admin',
                "email":"admin@a.com",
                "password":'a'
            }
            headers = {"Content-Type": 'application/json'}

            login = requests.post('https://choutuve-app-server.herokuapp.com/login',headers=headers,data=json.dumps(user))
            self.token = login.text

    def tearDown(self):
        with app.test_request_context():
            db.drop_all()

    def test_ping(self):
        responce = self.app.get('/ping',follow_redirects=True)
        self.assertEqual(responce.status_code,200)

    def test_post_video(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":False
        }
        headers = {"Content-Type": 'application/json','token':self.token}
        responce = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responce.status_code,200)

    def test_get_video_inalid_token(self):
        headers = {"Content-Type": 'application/json','token':''}
        responceGet = self.app.get('/videos',headers=headers,follow_redirects=True)
        self.assertEqual(responceGet.status_code,400)

    def test_get_video_as_admin(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        responceGet = self.app.get('/videos',headers=headers,follow_redirects=True)
        videoGet = responceGet.json[0]
        self.assertEqual(videoGet['user'],video['user'])
        self.assertEqual(videoGet['title'],video['title'])
        self.assertEqual(videoGet['size'],video['size'])
        self.assertEqual(videoGet['url'],video['url'])
        self.assertEqual(videoGet['thumbnail'],video['thumbnail'])
        self.assertEqual(videoGet['date'],video['date'])
        self.assertEqual(videoGet['description'],video['description'])
        self.assertEqual(videoGet['private'],video['private'])

    def test_get_video_individual(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        responceGet = self.app.get('/videos/1',headers=headers,follow_redirects=True)
        videoGet = responceGet.json
        self.assertEqual(videoGet['user'],video['user'])
        self.assertEqual(videoGet['title'],video['title'])
        self.assertEqual(videoGet['size'],video['size'])
        self.assertEqual(videoGet['url'],video['url'])
        self.assertEqual(videoGet['thumbnail'],video['thumbnail'])
        self.assertEqual(videoGet['date'],video['date'])
        self.assertEqual(videoGet['description'],video['description'])
        self.assertEqual(videoGet['private'],video['private'])

    def test_delete_video(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        responceGet = self.app.delete('/videos/1',headers=headers,follow_redirects=True)
        self.assertEqual(responceGet.status_code,200)

        responceGet = self.app.get('/videos/1',headers=headers,follow_redirects=True)
        videoGet = responceGet.json
        self.assertEqual(videoGet,None)

    def test_post_like(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        like = {
            'user':'1',
            'value':True
        }
        postLike = self.app.post('/videos/1/likes',headers=headers,data=json.dumps(like))
        self.assertEqual(postLike.status_code,200)

    def test_post_like_invalid_video(self):
        headers = {"Content-Type": 'application/json', 'token':self.token}
        like = {
            'user':'1',
            'value':True
        }
        postLike = self.app.post('/videos/1/likes',headers=headers,data=json.dumps(like))
        self.assertEqual(postLike.status_code,404)

    def test_get_like_ratio_of_a_video(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        like = {
            'user':'1',
            'value':True
        }
        postLike = self.app.post('/videos/1/likes',headers=headers,data=json.dumps(like))
        self.assertEqual(postLike.status_code,200)

        getLike = self.app.get('/videos/1/likes',headers=headers)
        reactions = getLike.json['reactions']
        self.assertEqual(reactions['dislike'],0)
        self.assertEqual(reactions['likes'],1)

    def test_post_comment_invalid_video(self):
        headers = {"Content-Type": 'application/json', 'token':self.token}
        like = {
            'user':'1',
            'text':'Good video'
        }
        postLike = self.app.post('/videos/1/comments',headers=headers,data=json.dumps(like))
        self.assertEqual(postLike.status_code,404)

    def test_post_comment(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        like = {
            'user':'1',
            'text':'Good video'
        }
        postComment = self.app.post('/videos/1/comments',headers=headers,data=json.dumps(like))
        self.assertEqual(postComment.status_code,200)

    def test_get_comment(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        self.assertEqual(responcePost.status_code,200)

        comment = {
            'user':'1',
            'text':'Good video'
        }
        postComment = self.app.post('/videos/1/comments',headers=headers,data=json.dumps(comment))
        self.assertEqual(postComment.status_code,200)
        getLike = self.app.get('/videos/1/comments',headers=headers)
        comments = getLike.json['comments'][0]
        self.assertEqual(comments['text'],comment['text'])
        self.assertEqual(comments['user'],comment['user'])
        self.assertEqual(comments['user'],'1')

    def test_metrics_user_activity(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))

        activityGet = self.app.get('/metrics/users/activity',headers=headers)
        activity = activityGet.json[0]

        self.assertEqual(activity['user'],video['user'])
        self.assertEqual(activity['activity'],1)

    def test_metrics_videos_most_liked(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))

        like = {
            'user':'1',
            'value':True
        }
        postLike = self.app.post('/videos/1/likes',headers=headers,data=json.dumps(like))

        activityGet = self.app.get('/metrics/videos/likes',headers=headers)
        mostLiked = activityGet.json[0]

        self.assertEqual(mostLiked['title'],video['title'])
        self.assertEqual(mostLiked['likes'],1)

    def test_metrics_videos_most_disliked(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))

        like = {
            'user':'1',
            'value':False
        }
        postLike = self.app.post('/videos/1/likes',headers=headers,data=json.dumps(like))

        activityGet = self.app.get('/metrics/videos/dislikes',headers=headers)
        mostDisliked = activityGet.json[0]

        self.assertEqual(mostDisliked['title'],video['title'])
        self.assertEqual(mostDisliked['dislikes'],1)

    def test_metrics_videos_most_comented(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        comment = {
            'user':'1',
            'text':'Good video'
        }
        postComment = self.app.post('/videos/1/comments',headers=headers,data=json.dumps(comment))
        postComment = self.app.post('/videos/1/comments',headers=headers,data=json.dumps(comment))

        metric = self.app.get('/metrics/videos/comments',headers=headers)
        comments = metric.json[0]

        self.assertEqual(comments['title'],video['title'])
        self.assertEqual(comments['cantComments'],2)

    def test_metrics_videos_per_day(self):
        video = {
            "user":"SGB",
            "title": "otro video",
            "size": 15500,
            "url": "dfsdfdg",
            "thumbnail": "hhsgfhgfhs",
            "date": "2019-07-21",
            "description": "una descripcion breve.",
            "private":True
        }
        headers = {"Content-Type": 'application/json', 'token':self.token}
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))
        responcePost = self.app.post('/videos',headers=headers,data=json.dumps(video))

        metric = self.app.get('/metrics/videos/day',headers=headers)
        comments = metric.json[0]

        self.assertEqual(comments['date'],video['date'])
        self.assertEqual(comments['cant'],3)


if __name__ == '__main__':
    unittest.main()