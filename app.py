from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
import bcrypt
from bson import ObjectId
from flask_apscheduler import APScheduler
from datetime import timedelta, date, datetime
import os # for Env Heroku
from graph import *
from toptradingcycle import *
from authlib.integrations.flask_client import OAuth
# from algorithm import graph #algorithm
# from algorithm import *
# from algorithm.toptradingcycle import toptradingcycle

# aric and tal

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")
app.config['MONGO_DBNAME'] = 'multiTrade'
app.config['SECRET_KEY'] = 'mySecret'
# app.secret_key = "mySecret"
mongo = PyMongo(app)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME"),
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME"),
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
))

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='1028413226216-2ivlgf73ho77h09de0js4mur4kos4gr6.apps.googleusercontent.com',
    client_secret='TZD2-5wPZI_UBmXAtmuzxI5d',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www..google.com/oauth2/v1/',
    server_metadata_url=CONF_URL,
    client_kwargs={'scope': 'openid email profile'}
)

users = mongo.db.users
items = mongo.db.items
tenders = mongo.db.tenders
fsFiles = mongo.db.fs.files
fsChunks = mongo.db.fs.chunks

scheduler = APScheduler()
mail = Mail(app)

@app.route('/gmailLogin/')
def gmailLogin():

    google = oauth.create_client('google')
    redirect_url = url_for('auth', _external=True)
    return google.authorize_redirect(redirect_url)

@app.route('/auth/')
def auth():

    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get("https://www.googleapis.com/oauth2/v2/userinfo")
    user_info = resp.json()
    email = user_info["email"].lower()
    firstName = user_info["given_name"]
    lastName = user_info["family_name"]

    existing_user = users.find_one({'email': email})

    if existing_user is None:
        users.insert({'email': email, 'password': None, 'firstName': firstName, 'lastName': lastName, 'state': "",
                      'phoneNum': "", 'favoritesTenders': [], 'confirmed': None})
        session["email"] = email
    else: # user exists
        if existing_user["confirmed"] is None: # already registered via Gmail at least once
            session["email"] = email
        else: # the user already registered in the regular way so cannot login with gmail
            session["need_login_with_pwd"] = True
    return redirect(url_for("home"))


def checkMessages():

    if "personal_details" in session:
        flash("Personal details updated",'success')
        session.pop("personal_details",None)

    if "edit_tender" in session:
        flash("Tender's details updated",'success')
        session.pop("edit_tender",None)

    if "edit_item" in session:
        flash("Item details updated successfully",'success')
        session.pop("edit_item",None)

    if "delete_item" in session:
        flash("Item deleted successfully",'success')
        session.pop("delete_item",None)

    if "rank_items" in session:
        flash("Your preferences were saved",'success')
        session.pop("rank_items",None)

    if "add_favorite" in session:
        if session["add_favorite"]:
            flash("Tender added to favorites",'success')
            session.pop("add_favorite",None)
        else:
            flash("Tender deleted from favorites",'success')
            session.pop("add_favorite",None)

    if "blocked" in session:
        flash("You are not allowed to enter this tender",'error')
        session.pop("blocked",None)

    if "need_confirm" in session:
        flash("Please confirm your account",'error')
        session.pop("need_confirm",None)

    if "confirmSucceed" in session:
        flash("Confirm succeed, welcome to MultiTrade site",'success')
        session.pop("confirmSucceed",None)

    if "please_confirm" in session:
        flash("Check your mailbox for confirm link",'success')
        session.pop("please_confirm",None)

    if "need_login_with_pwd" in session:
        flash("Please login with email and password",'error')
        session.pop("need_login_with_pwd",None)


@app.route('/', methods=["POST", "GET"])
def home():

    checkMessages()
    all_tenders = tenders.find({'isPrivate': False})
    if request.method == "POST":  # for search
        search_input = request.form["search"]
        tenders_id = sorted(tenders.find({'name': {'$regex': search_input, "$options" : "i"}}), key=lambda tender: tender["joining_time"]) # show results if
        # tender exist which contains the search_input string, "i" flag make it case-insensitivity
    else:
        tenders_id = sorted(tenders.find({'results': {} }), key=lambda tender: tender["joining_time"]) # show all tenders

    for t in tenders_id : # design the joining_time field
        t["joining_time"] = str(t["joining_time"])[0:11]

    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})
        return render_template("welcome_logged_in.html", login_user=login_user, tenders_id=tenders_id, all_tenders=all_tenders)

    return render_template("welcome.html", tenders_id=tenders_id, all_tenders=all_tenders)


@app.route("/login/", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        email = request.form["email"].lower()
        login_user = users.find_one({'email': email})

        if login_user:  # the user exist in DB
            if not login_user["password"]: # if the user connected with google, he doesn't have a password
                return "Invalid username/password combination"

            if bcrypt.hashpw(request.form["pass"].encode('utf-8'), login_user["password"]) == login_user["password"]:
                if login_user["confirmed"]:
                    session["email"] = email
                else:
                    session["need_confirm"] = True
                return redirect(url_for("home"))

        return "Wrong password"

    else:
        if "email" in session: # the user is already logged in and try to get to login
            return redirect(url_for("home"))

    allEmails=[]
    allUsers = users.find()
    for u in allUsers:
        allEmails.append(u["email"])
    return render_template("login.html",allEmails=allEmails)


@app.route("/register/", methods=["POST", "GET"])
def register():

    if request.method == "POST":
        firstName = request.form["fn"]
        lastName = request.form["ln"]
        email = request.form["email"].lower()
        state = request.form["myState"]
        prefix = request.form["phone1Prefix"]
        phoneNum = request.form["phoneNum"]

        if phoneNum:
            phoneNum = prefix + phoneNum

        existing_user = users.find_one({'email': email})

        if existing_user is None: # check if the user is already registered by email
            hashPass = bcrypt.hashpw(request.form["pass"].encode('utf-8'), bcrypt.gensalt())
            userId = users.insert({'email': email, 'password': hashPass, 'firstName': firstName,
                          'lastName': lastName, 'state': state, 'phoneNum': phoneNum, 'favoritesTenders': [], 'confirmed': False})

            # session["email"] = email
            with app.app_context(): # for sending emails need to use app context
                sendEmail("Confirm your account in MultiTrade","Click https://multitrade.herokuapp.com/confirm/"+str(userId)+" for confirm your account \n MultiTrade", [email])
                session["please_confirm"] = True
            return redirect(url_for("home"))

        return "your email is already exist in DB"  # the user is already exsit Js will avoid this case

    else:  # GET request
        if "email" in session:
            return redirect(url_for("home"))

    allEmails = []
    allUsers = users.find()
    for u in allUsers:
        allEmails.append(u["email"])
    return render_template("register.html",allEmails=allEmails)


@app.route("/confirm/<userId>/")
def confirmUser(userId):

    existing_user = users.find_one({'_id': ObjectId(userId)})
    if not existing_user is None:
        email = existing_user["email"]
        if not existing_user["confirmed"]: # need to confirm the account
            session["email"] = email
            users.update({
                '_id': ObjectId(userId)},
                {
                '$set': {
                    'confirmed': True}
            }, upsert=False)
            session["confirmSucceed"] = True
    return redirect(url_for("home"))


@app.route("/collection/", methods=["POST", "GET"])
def myCollection():

    checkMessages()
    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})

        if request.method == "POST": # add item
            itemName = request.form["itemName"]
            itemDetails = request.form["itemDetails"]
            itemImage = request.files["image"]
            id = mongo.save_file(itemImage.filename, itemImage)

            fsFiles.update({
                '_id': ObjectId(id)},
                {
                '$set': {
                    'filename': str(id)
                }
            }, upsert=False)

            items.insert({'owner': email, 'name': itemName, 'details': itemDetails,
                          'image': str(id), 'inUse': False, 'itemReceived': None})
            return redirect(url_for("myCollection"))
        # GET
        return render_template("my_collection.html", login_user=login_user, items=items)
    return redirect(url_for("home"))


@app.route("/edit_item/<itemId>/", methods=['GET', 'POST'])
def edit_item(itemId):

    current_item = items.find_one({'_id': ObjectId(itemId)})
    if "email" in session and not current_item["inUse"]:
        email = session["email"]
        login_user = users.find_one({'email': email})

        if email == current_item["owner"]:
            imageId = current_item["image"]

            if request.method == "POST":

                itemName = request.form["itemName"]
                itemDetails = request.form["itemDetails"]
                itemImage = request.files["image"]

                if itemImage:  # if user chose image file
                    imageId = mongo.save_file(itemImage.filename, itemImage)

                    fsFiles.update({
                        '_id': ObjectId(imageId)},
                        {
                        '$set': {
                            'filename': str(imageId)
                        }
                    }, upsert=False)

                    fsFiles.delete_one(
                        {'_id': ObjectId(current_item["image"])})

                    fsChunks.delete_one(
                        {'files_id': ObjectId(current_item["image"])})

                items.update({
                    '_id': ObjectId(itemId)},
                    {
                    '$set': {
                        'name': itemName,
                        'details': itemDetails,
                        'image': str(imageId)
                    }
                }, upsert=False)

                session["edit_item"] = True
                return redirect(url_for("myCollection"))

            return render_template("edit_item.html", fn=login_user["firstName"], current_item=current_item)

    return redirect(url_for("home"))


@app.route("/delete_item/<itemId>")
def delete_item(itemId):

    if "email" in session:
        email = session["email"]
        current_item = items.find_one({'_id': ObjectId(itemId)})
        if email == current_item["owner"]:
            if not current_item["inUse"]:

                fsFiles.delete_one(
                    {'_id': ObjectId(current_item["image"])})

                fsChunks.delete_one(
                    {'files_id': ObjectId(current_item["image"])})

                items.remove({'_id': ObjectId(itemId)})

                session["delete_item"] = True
            return redirect(url_for("myCollection"))
    return redirect(url_for("home"))


@app.route("/personal_details/", methods=['GET', 'POST'])
def edit_user():

    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})
        id = login_user["_id"]

        if request.method == "POST":
            state = request.form["myState"]
            prefix = request.form["phone1Prefix"]
            phoneNum = request.form["phoneNum"]

            if phoneNum:
                phoneNum = prefix + phoneNum

            users.update({
                '_id': ObjectId(id)},
                {
                '$set': {
                    'phoneNum': phoneNum,
                    'state': state,
                }
            }, upsert=False)

            session["personal_details"] = True
            return redirect(url_for("home"))

        # for GET request to know which prefix to show
        prefixToHtml = "050"
        if login_user["phoneNum"]:
            prefixToHtml = login_user["phoneNum"][0:3]
        return render_template("personal_details.html", login_user=login_user, pref=prefixToHtml)

    return redirect(url_for("home"))


@app.route("/create_tender/", methods=["POST", "GET"])
def create_tender():

    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})

        if request.method == "POST":
            name = request.form["tenderName"]
            desc = request.form["tenderDetails"]
            days_for_ranking = int(request.form["daysForRanking"])
            date = request.form["datepicker"]

            d = int(date[:2])
            m = int(date[3:5])
            y = int(date[6:])
            joining_time = datetime(y, m, d)

            current_tender = {'name': name, 'description': desc,
                              'items': {}, 'participants': [], 'owner': email, 'joining_time': joining_time,
                              'daysForRanking': days_for_ranking, 'isActive': True, 'blocked': [], 'results': {}}

            if request.form["tender's privacy"] == "private":
                isPrivate = True
                hashPass = bcrypt.hashpw(request.form["pass"].encode('utf-8'), bcrypt.gensalt())
                current_tender["password"] = hashPass
            else:
                isPrivate = False

            current_tender["isPrivate"] = isPrivate

            tenderId = tenders.insert(current_tender)
            session[str(tenderId)] = True
            return redirect(url_for("out_of_tender", tenderId=tenderId))

        # GET
        return render_template("create_tender.html", fn=login_user["firstName"])

    return redirect(url_for("home"))


@app.route("/out_of_tender/<tenderId>/")
def out_of_tender(tenderId):

    checkMessages()
    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if current_tender["isActive"]:
        if "email" in session:
            email = session["email"]
            login_user = users.find_one({'email': email})
            if email in current_tender["blocked"]: # if user is not allowed to enter to this tender
                session["blocked"] = True
                return redirect(url_for("home"))

            # if user already joined but wrote this address(wrong address)
            if email in current_tender["participants"]:
                session[str(tenderId)] = True # if the user already participates in this tender give him permission no matter privacy
                return redirect(url_for("inside_of_tender", tenderId=tenderId))

            # need to send to password page in order to enter the tender of its private instead of line 256!
            if current_tender["isPrivate"]:
                if str(tenderId) in session: # user got permission
                    return render_template("out_of_tender.html", login_user=login_user, current_tender=current_tender, items=items)

                # the user is not the owner and does not has permission
                if email != current_tender["owner"]:
                    return redirect(url_for("enter_password", tenderId=tenderId))

            # public, connected and not participate
            return render_template("out_of_tender.html", login_user=login_user, current_tender=current_tender, items=items)

        if current_tender["isPrivate"]:  # not connected and tender is private
            if str(tenderId) in session:
                return render_template("out_of_tender_disconnected.html", current_tender=current_tender, items=items)

            # the user didnt put password and not connected
            return redirect(url_for("enter_password", tenderId=tenderId))

        return render_template("out_of_tender_disconnected.html", current_tender=current_tender, items=items)

    # not isActive and no results = need to rank
    elif not current_tender["results"]:
        return redirect(url_for("rank_items", tenderId=tenderId))

    else:  # not isActive and have results so the tender is over!
        return redirect(url_for("results", tenderId=tenderId))



# if the user join to tender and chose item
@app.route("/item_added_to_tender/<tenderId>/<itemId>/")
def item_added_to_tender(tenderId, itemId):

    if "email" in session:
        email = session["email"]
        current_tender = tenders.find_one({'_id': ObjectId(tenderId)})

        if current_tender["isActive"]:
            current_item = items.find_one({'_id': ObjectId(itemId)})

            # if the user not in the tender and this item is mine
            if email not in current_tender["participants"] and email == current_item["owner"]:

                # if the item not in use in other tender
                if not current_item["inUse"]:
                    # add the item with empty array of preferences
                    current_tender["items"][itemId] = []
                    current_tender["participants"].append(email)
                    # update DB
                    tenders.update({  # update the tender in DB
                        '_id': ObjectId(tenderId)},
                        {
                        '$set': {
                            'items': current_tender["items"],
                            'participants': current_tender["participants"]}}, upsert=False)

                    items.update({  # update the user in DB
                        '_id': ObjectId(itemId)},
                        {
                        '$set': {
                            'inUse': True,
                            'inTender': ObjectId(tenderId)
                        }}, upsert=False)

                    return redirect(url_for("inside_of_tender", tenderId=tenderId))

    return redirect(url_for("home"))


# if the user already participate in tender and changeing his item
@app.route("/change_item_in_tender/<tenderId>/<newItemId>/")
def change_item_in_tender(tenderId, newItemId):

    if "email" in session:
        email = session["email"]
        current_tender = tenders.find_one({'_id': ObjectId(tenderId)})

        if current_tender["isActive"]:
            old_item = items.find_one({'inTender': ObjectId(tenderId), 'owner': email})
            new_item = items.find_one({'_id': ObjectId(newItemId)})

            # check if the user already in the tender and the items belong to him
            if old_item["owner"] == email and new_item["owner"] == email and email in current_tender["participants"]:

                if not new_item["inUse"]:  # if the new item not in use in other tender

                    # add email to the end of array because the item will added to the end of the items list
                    current_tender["participants"].remove(email)
                    current_tender["participants"].append(email)
                    current_tender["items"][newItemId] = current_tender["items"].pop(str(old_item["_id"]))
                    # now its ordered participant[i] and items[i]

                    tenders.update_one({  # update the tender in DB
                        '_id': ObjectId(tenderId)},
                        {
                        '$set': {
                            'items': current_tender["items"],
                            'participants': current_tender["participants"]
                        }}, upsert=False)

                    items.update_one({  # update the old item!
                        '_id': old_item["_id"]},
                        {
                        '$set': {
                            'inUse': False,
                            'inTender': None
                        }}, upsert=False)

                    items.update_one({  # update the new item
                        '_id': ObjectId(newItemId)},
                        {
                        '$set': {
                            'inUse': True,
                            'inTender': ObjectId(tenderId)
                        }}, upsert=False)

                    return redirect(url_for("inside_of_tender", tenderId=tenderId))

    return redirect(url_for("home"))


@app.route("/my_own_tenders/")
def my_own_tenders():

    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})
        return render_template("my_own_tenders.html", login_user=login_user, tenders=tenders)

    return redirect(url_for("home"))


@app.route("/my_deals/")
def my_deals():

    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})
        return render_template("my_deals.html", login_user=login_user, items=items, tenders=tenders)

    return redirect(url_for("home"))


@app.route("/inside_of_tender/<tenderId>/", methods=["POST", "GET"])
def inside_of_tender(tenderId):

    checkMessages()
    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if current_tender["isActive"]:
        if "email" in session:
            email = session["email"]
            login_user = users.find_one({'email': email})
            # this user not taking part in this
            if email not in current_tender["participants"]:
                # of POST REQUEST
                return redirect(url_for("out_of_tender", tenderId=tenderId))

            if request.method == "POST":  # leave tender!

                current_tender["participants"].remove(email)
                current_item = items.find_one({'inTender': ObjectId(tenderId), 'owner': email})
                current_tender["items"].pop(str(current_item["_id"]), None)

                tenders.update({  # update the tender in DB
                    '_id': ObjectId(tenderId)},
                    {
                    '$set': {
                        'items': current_tender["items"],
                        'participants': current_tender["participants"]}}, upsert=False)

                items.update({  # item not in use anymore
                    '_id': current_item["_id"]},
                    {
                    '$set': {
                        'inUse': False,
                        'inTender': None}}, upsert=False)

                session[str(tenderId)] = True
                # POST REQUEST
                return redirect(url_for("out_of_tender", tenderId=tenderId))
            # GET
            return render_template("inside_of_tender.html", login_user=login_user, current_tender=current_tender, items=items)

        # not connected
        return redirect(url_for("out_of_tender", tenderId=tenderId))

    # not isActive and no results = need to rank
    elif not current_tender["results"]:
        return redirect(url_for("rank_items", tenderId=tenderId))

    else:  # not isActive and have results so the tender is over!
        return redirect(url_for("results", tenderId=tenderId))


@app.route("/enter_password/<tenderId>/", methods=["POST", "GET"])
def enter_password(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if current_tender["isActive"]:
        if not current_tender["isPrivate"]:  # this tender is public
            return redirect(url_for("out_of_tender", tenderId=tenderId))

        if "email" in session:
            email = session["email"]
            if email in current_tender["participants"]: # if user already joined with password he doesnt need enter password again
                return redirect(url_for("inside_of_tender", tenderId=tenderId))

        if request.method == "POST":  # if user didnt join to this tender and the pass is correct
            if bcrypt.hashpw(request.form["pass"].encode('utf-8'), current_tender["password"]) == current_tender["password"]:
                session[str(tenderId)] = True
                return redirect(url_for("out_of_tender", tenderId=tenderId))

        # GET
        if str(tenderId) in session:
            return redirect(url_for("out_of_tender", tenderId=tenderId))
        # user is connected but not participate in this tender
        return render_template("enter_password_private.html", current_tender=current_tender)

    return redirect(url_for("home"))


@app.route("/rank_items/<tenderId>/", methods=["POST", "GET"])
def rank_items(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    tenderPref = "pref " + tenderId # store the num of preferences for each user

    if current_tender["results"]:
        return redirect(url_for("results", tenderId=tenderId))

    if "email" in session:
        email = session["email"]

        login_user = users.find_one({'email': email})
        if email in current_tender["participants"]:

            if not current_tender["isActive"]:  # rank items!

                if request.method == "POST":  # click submit after rank
                    try:  # first post request -> the amount of prefered items
                        numOfPrefs = request.form["preferedCount"]
                        session[tenderPref] = numOfPrefs

                    except:  # second post request -> create list of preferred items accordingly to numOfPrefs value
                        if tenderPref in session:  # we clicked apply and then submit
                            numOfPrefs = session[tenderPref]
                            sortedItems = request.form.getlist("handles[]")

                            currentItem = items.find_one({'inTender': ObjectId(tenderId), 'owner': email})
                            itemId = str(currentItem["_id"])

                            if(int(numOfPrefs) == 0):  # prefer his item
                                # clear his prev preferences
                                current_tender["items"][itemId] = []
                                # add his item as first preferenc.
                                current_tender["items"][itemId].append(itemId)

                                # add the rest of the items

                            else:  # prefer at least one item of the list
                                current_tender["items"][itemId] = sortedItems[-int(numOfPrefs):]
                                # add his item after the items he prefer
                                current_tender["items"][itemId].append(itemId)

                            print(current_tender["items"])
                            tenders.update_one({  # update the tender with items preferences in DB
                                '_id': ObjectId(tenderId)},
                                {
                                '$set': {
                                    'items': current_tender["items"]}}, upsert=False)

                            session.pop(tenderPref, None)
                            session["rank_items"] = True
                            return redirect(url_for("home"))

                # GET
                else:
                    if email in current_tender["participants"]:
                        # clear the preferences before get request
                        session.pop(tenderPref, None)
                        return render_template("rank_items.html", current_tender=current_tender, login_user=login_user, items=items)

            else:  # if the tender is active
                return redirect(url_for("out_of_tender", tenderId=tenderId))

    return redirect(url_for("home"))


@app.route("/results/<tenderId>/", methods=["POST", "GET"])
def results(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    size = len(current_tender["participants"])

    if request.method == "POST":  # click submit for send email to all participants
        emailSubject = request.form["email subject"]
        emailContent = request.form["email content"]
        with app.app_context():  # for sending emails need to use app context
            sendEmail(emailSubject, emailContent, current_tender["participants"])
        return redirect(url_for("results", tenderId=tenderId))

    login_user = None
    email = None
    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})

    if (current_tender["results"] or (email == current_tender["owner"])):

        participants = current_tender["participants"]

        items_arr1 = []  # list of items
        items_list_id1 = list(current_tender["items"].keys())  # list of items id
        for i in items_list_id1:
            # add the item element by id
            items_arr1.append(items.find_one({'_id': ObjectId(i)}))

        items_arr2 = []  # list of results items

        # list of the results items id
        items_list_id2 = list(current_tender["results"].values())
        for i in range(size):
            # participant by same order as items keys
            user_email = participants[i]
            # return the result for participant[i]
            user_result = current_tender["results"][user_email]
            # return the result for participant[i]
            items_arr2.append(items.find_one({'_id': ObjectId(user_result)}))

        return render_template("results.html", current_tender=current_tender, login_user=login_user,
                               items_arr1=items_arr1, items_arr2=items_arr2)
    return redirect(url_for("home"))


@app.route('/delete_tender/<tenderId>/')
def delete_tender(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if current_tender["isActive"]:  # the tender is still open for sign
        if "email" in session:
            email = session["email"]
            # if this user is the owner of the tender
            if email == current_tender["owner"]:

                tenders.delete_one({  # update the tender in DB
                    '_id': ObjectId(tenderId)})

                items.update_many({  # items not in use anymore
                    'inTender': ObjectId(tenderId)},
                    {
                    '$set': {
                        'inUse': False,
                        'inTender': None}}, upsert=False)

                users.update_many({  # if user liked this tender, remove it
                    'favoritesTenders': (tenderId)},
                    {
                    '$pull': {'favoritesTenders': tenderId}}, upsert=False)

                return redirect(url_for("my_own_tenders"))

    return redirect(url_for("home"))


@app.route('/add_favorite/<tenderId>/')
def add_favorite(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if current_tender["isActive"]:  # the tender is still open for sign
        if "email" in session:
            email = session["email"]
            login_user = users.find_one({'email': email})
            # if this user is the owner of the tender
            # if i already liked this tender remove from favorites
            if tenderId in login_user["favoritesTenders"]:
                users.update({  # item not in use anymore
                    '_id': login_user["_id"]},
                    {
                    '$pull': {'favoritesTenders': tenderId}}, upsert=False)
                session["add_favorite"] = False
            else:  # i want to add to favorite tenders
                users.update({  # item not in use anymore
                    '_id': login_user["_id"]},
                    {
                    '$push': {'favoritesTenders': tenderId}}, upsert=False)
                session["add_favorite"] = True

        return redirect(url_for("out_of_tender", tenderId=tenderId))

    else:
        return redirect(url_for("home"))


@app.route('/FQA/')
def FQA():
    login_user = None
    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})

    return render_template("FQA.html",login_user=login_user)

@app.route('/AboutUs/')
def AboutUs():
    login_user = None
    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})

    return render_template("about_us.html",login_user=login_user)

@app.route('/contact/', methods=["POST", "GET"])
def contact():
    login_user = None
    if "email" in session:
        email = session["email"]
        login_user = users.find_one({'email': email})

    if request.method == "POST":
        mail =  request.form["email"]
        emailSubject = request.form["subject"]
        emailContent = request.form["message"]
        emailContent = emailContent + "\n his mail: " + mail
        with app.app_context(): # for sending emails need to use app context
            sendEmail(emailSubject, emailContent, ["finalprojmultitrade@gmail.com"])
        return redirect(url_for("home"))

    return render_template("contact.html",login_user=login_user)


@app.route('/edit_tender/<tenderId>/', methods=["POST", "GET"])
def edit_tender(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if current_tender["isActive"]:
        if "email" in session:
            email = session["email"]
            login_user = users.find_one({'email': email})
            # the current user is the owner
            if email in current_tender["owner"]:
                if request.method == "POST":  # clicked update
                    blockedList = request.form.getlist("check[]")
                    current_tender["blocked"] = blockedList # get the updated blockedList from the page
                    for user in blockedList: # delete every user that participate in the tender and get blocked
                        if user in current_tender["participants"]:
                            current_tender["participants"].remove(user)
                            current_item = items.find_one({'inTender': ObjectId(tenderId), 'owner': user})
                            current_tender["items"].pop(str(current_item["_id"]), None)

                    name = request.form["tenderName"]
                    desc = request.form["tenderDetails"]
                    days_for_ranking = int(request.form["daysForRanking"])
                    date = request.form["datepicker"]

                    d = int(date[:2])
                    m = int(date[3:5])
                    y = int(date[6:])
                    joining_time = datetime(y, m, d)

                    if (name != current_tender["name"] or days_for_ranking != current_tender["daysForRanking"]
                        or joining_time != current_tender["joining_time"]):
                            sendEmail(current_tender["name"]+" has changed","Some details were changed in tender "+current_tender["name"]+
                                ", to see the changes: https://multitrade.herokuapp.com/out_of_tender/"+str(current_tender["_id"])+"\n MultiTrade",
                                current_tender["participants"])


                    tenders.update_one({  # update the tender in DB
                        '_id': ObjectId(current_tender["_id"])},
                        {
                        '$set': {
                            'name': name,
                            'description': desc,
                            'daysForRanking': days_for_ranking,
                            'joining_time': joining_time,
                            'blocked': current_tender["blocked"],
                            'items': current_tender["items"],
                            'participants': current_tender["participants"]}}, upsert=False)

                    items.update_many({ # update any item that in the blockList and also participate
                        'inUse': True, 'inTender': current_tender["_id"], 'owner': {"$in": current_tender["blocked"]} },
                        {
                        '$set': {
                            'inUse': False,
                            'inTender': None}}, upsert=False)

                    session["edit_tender"] = True
                else: # GET
                    return render_template("edit_tender.html", current_tender=current_tender, login_user=login_user)

    return redirect(url_for("home"))


@app.route('/return-file/<fileId>/')
def return_file(fileId):

    current_file = fsFiles.find_one({'_id': ObjectId(fileId)})
    file_name = current_file["filename"]
    return mongo.send_file(file_name)


@app.route("/logout/")
def logout():

    session.clear()
    return redirect(url_for("home"))


def allJobs():

    print("alljobs")
    d = (datetime.now()+timedelta(hours=3)).date()
    current_date = datetime(d.year, d.month, d.day)
    waiting_tenders = tenders.find({'results': {}}) # find all tenders without results

    for current_tender in waiting_tenders:
        last_joining_day = current_tender["joining_time"]

        if current_tender["isActive"]:  # if is active check if the time for join is over
            if last_joining_day < current_date:  # not equal because we didnt want open for ranking in the opening day
                tenders.update_one({  # update the tender in DB
                    '_id': ObjectId(current_tender["_id"])},
                    {
                    '$set': {
                        'isActive': False}}, upsert=False)
                # if only 1 participant and joining time over - change item status to be not in use
                if len(current_tender["participants"]) == 1:
                    itemToResume = list(current_tender["items"].keys())[0]
                    items.update_one({  # update the tender in DB
                        '_id': ObjectId(itemToResume)},
                        {
                        '$set': {
                            'inUse': False, 'inTender': None}},
                             upsert=False)
                else: # more than 1 participant
                    with app.app_context(): # for sending emails need to use app context
                        sendEmail("It's time to rank items in tender "+current_tender["name"],
                        "Click here to rank items: https://multitrade.herokuapp.com/rank_items/"+str(current_tender["_id"])+"\n MultiTrade",
                        current_tender["participants"])

        elif (last_joining_day + timedelta(days=current_tender["daysForRanking"])) < current_date and len(current_tender["participants"]) > 1:
            myAlgo(str(current_tender["_id"]))

def myAlgo(tenderId):

    current_tender = tenders.find_one({'_id': ObjectId(tenderId)})
    if not current_tender["isActive"]:

        owners = current_tender["participants"]  # emails
        # cast to list for keeping the item's keys order
        items = list(current_tender["items"].keys())
        initialOwnerShip = dict(zip(items, owners))

        # change the keys of preferences to be owner email instead of item id
        for i in range(len(owners)):
            # if the user didnt rank any item
            if not current_tender["items"][items[i]]: # preferences list of this item is empty
                (current_tender["items"][items[i]]).append(items[i])  # put his item as first preference

            # change to email prefer items instead of item prefer items
            current_tender["items"][owners[i]] = current_tender["items"].pop(items[i])
        preferences = current_tender["items"]

        results = topTradingCycles(owners, items, preferences, initialOwnerShip)

        updateExchanges(results)

        tenders.update_one({  # update the results of the tender in DB
            '_id': ObjectId(tenderId)},
            {
            '$set': {
                'results': results}}, upsert=False)


def updateExchanges(results):

    receivedSameItem = []
    receivedNewItem = []

    for email, item_received in results.items(): # items method on dict return touple pairs
        current_item = items.find_one({'_id': ObjectId(item_received)})
        if current_item:
            if (email == current_item["owner"]):  # received his item
                receivedSameItem.append(email)
                # update inUse to False
                items.update_one({  # update the tender in DB
                    '_id': ObjectId(item_received)},
                    {
                    '$set': {
                        'inUse': False}}, upsert=False)
            else:  # received another item
                receivedNewItem.append(email)
                items.update_one({  # update the item in DB
                    'owner': email, 'inTender': current_item["inTender"]},
                    {
                    '$set': {  # create new field that contains which item we will receive
                        'itemReceived': ObjectId(item_received)}}, upsert=False)

    with app.app_context(): # for sending emails need to use app context
        sendEmail("Results for tender "+current_tender["name"],
        "Click here to see the results: https://multitrade.herokuapp.com/results/"+str(current_tender["_id"])+"\n MultiTrade",
        receivedNewItem)

    with app.app_context(): # for sending emails need to use app context
        sendEmail("Unfortunately you got the same item in tender "+current_tender["name"],
        "Click here to see the results: https://multitrade.herokuapp.com/results/"+str(current_tender["_id"])+"\n try your luck next time \n MultiTrade",
        receivedSameItem)


def sendEmail(subject, body, participants):
    try:
        if len(participants) > 0:
            msg = Message(subject, recipients=participants)
            msg.body = body
            mail.send(msg)
    except:
        print("send email failed")


def addDays(tenderDates, numOfDays):
    return tenderDates + timedelta(days=numOfDays)

app.jinja_env.filters['addDays'] = addDays # add fuction addDays as custon filter to ninja environment

if __name__ == '__main__':
    scheduler.add_job(id='activation task', func=allJobs, trigger='interval', seconds=10)
    scheduler.start()
    app.run(debug=True)
