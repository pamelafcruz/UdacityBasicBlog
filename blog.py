import os, jinja2, webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
index_template = 'index.html'
newpost_template = 'newpost.html'

def render_template(self, posts):
    self.render(index_template, posts = posts)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **params):
        self.write(self.render_str(template, **params))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

class MainHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render(index_template, posts = posts)

class NewPostHandler(Handler):
    def render_template(self, subject = "", content = "", error = ""):
        self.render(newpost_template,
                    subject = subject,
                    content = content,
                    error = error)
    def get(self):
        self.render_template()
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(subject = subject, content = content)
            post.put()
            self.redirect('/blog/%s' % post.key().id())
        else:
            error = "subject and content, please!"
            self.render_template(subject, content, error)

class PermalinkHandler(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        self.render(index_template, posts = [post])


app = webapp2.WSGIApplication([('/blog', MainHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/(\d+)', PermalinkHandler)], debug = True)
