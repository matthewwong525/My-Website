from google.appengine.ext import ndb
from google.appengine.api import memcache
import re
import logging
import utils

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

#TODO: Make a cache for everything

class Users(ndb.Model):
    username = ndb.StringProperty(required = True)
    password = ndb.StringProperty(required = True)
    email = ndb.StringProperty(required = True)
    fullname = ndb.StringProperty(required = True)
    datecreate = ndb.DateTimeProperty(auto_now_add=True)

def user_cache(update=False,ancestor=None):
    key = "users"
    memGet = memcache.get(key)
    if update:
        #logging.info(ancestor)
        queryUser = ndb.gql("SELECT * FROM Users WHERE ANCESTOR IS :1 ",ancestor)
        queryUser = list(queryUser)
        if queryUser:
            content = queryUser
        else:
            content = None
        memcache.set(key,content)
    else:
        content = memGet
    return content


def get_user_error_signup(new_user,errors):
    #TODO: check same email and same user in database
    u_user,u_pass,u_verify,u_email,u_fname = new_user
    err_user,err_pass,err_verify,err_email,err_fname = errors

    queryUser = check_user_in_cache(u_user)


    if not USER_RE.match(u_user) and not queryUser:
        err_user = "Incorrect Username"
    else:
        err_user = "Username already exists"
    if not PASS_RE.match(u_pass):
        err_pass = "Incorrect Password"
    if not u_pass == u_verify:
        err_verify = "Passwords do not match"
    if not (EMAIL_RE.match(u_email) or u_email == ""):
        err_email = "Incorrect Email Address"
    if u_fname == "":
        err_fname = "A name is required"

    return err_user,err_pass,err_verify,err_email,err_fname

def signup_user_check(self,new_user,errors):
    u_user,u_pass,u_verify,u_email,u_fname = new_user
    err_user,err_pass,err_verify,err_email,err_fname = errors

    if err_user == "" and err_pass == "" and err_email=="" and err_verify == "" and err_fname == "":
        self.response.headers.add("Set-Cookie","user_id=%s; Path=/" % utils.make_secret_hash(str(u_user)))
        update_userdata(new_user)
        self.redirect("/")
    else:
        self.render_signup(u_user,u_email,err_user,err_pass,err_verify,err_email,err_fname)

#add transaction
def update_userdata(new_user):
    u_user,u_pass,u_verify,u_email,u_fname = new_user
    parent_key = ndb.Key('user_parent','parent')
    user = Users(parent=parent_key,username=u_user,password=utils.make_pw_hash(str(u_pass)),email=u_email,fullname=u_fname)
    #user.key = ndb.Key(Users,u_user)
    user.put()
    user_cache(update=True,ancestor=parent_key)

def check_creds(u_user,u_pass):
    queryUser = check_user_in_cache(u_user)

    if queryUser and utils.verify_pw_hash(u_pass,str(content.Users.password)):
        return True
    else:
        return False

def check_user_in_cache(u_user):
    content = user_cache()
    queryUser = True
    for uesrs in content:
        if u_user in uesrs.username:
            queryUser = False
            break