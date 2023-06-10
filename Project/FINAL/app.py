from flask import Flask, render_template, request, redirect
import psycopg2
from datetime import datetime, timezone
import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext


app = Flask(__name__, 
            static_folder='FRONT_END/static',
            template_folder='FRONT_END/templates')
            
def connect_to_db():
    connection = psycopg2.connect(
        host = "localhost",
        port = "5432",
        database = "project",
        user = "manaskopparicloud.com",
        password = "qwertyui"
    )
    return connection 

@app.route('/')
def index():
        con = connect_to_db()
        cur = con.cursor()
        cur.execute("Select * from users order by reputation desc limit 5")
        users = cur.fetchall()
        # print(users)
        stats = []
        cur.execute("Select count(id) from users;")
        stats.append(cur.fetchall()[0][0])
        cur.execute("Select count(id) from questions;")
        stats.append(cur.fetchall()[0][0])
        cur.execute("Select count(id) from answers;")
        stats.append(cur.fetchall()[0][0])
        cur.execute("select count(tag) from (select distinct tag from tags) as t;")
        stats.append(cur.fetchall()[0][0])
        
        cur.execute("select distinct tag from tags order by tag;")
        tags = cur.fetchall()

        cur.execute("select tag from  (select tag,count(tag) from tags group by tag order by count desc) as t limit 5;")
        ptags = cur.fetchall()

        ## ----- upvotes ------

        cur.execute("select title,score,id from questions order by score desc limit 5;")
        upvoted = cur.fetchall()

        ## --- RECEnT -----

        cur.execute("select title,creationdate,id from questions order by creationdate desc limit 5;")
        recent = cur.fetchall()

        ## ---- unanswered -----

        cur.execute("select title,id from questions where id not in (select Parentid from answers ) limit 5;")
        unanswered = cur.fetchall()

        return render_template('index.html',users = users, stats = stats,tags=tags,ptags = ptags, Upvotedquestions = upvoted, recentquestions = recent, unanswered = unanswered)


@app.route('/register',methods = ['POST', 'GET'])
def register():
   if request.method == 'GET':
        return render_template("register.html", error="", error2 = "")


##----- REGISTRATIOn OF nEW USER ---------

@app.route('/user',methods = ['POST', 'GET'])
def user():
   if request.method == 'POST':
        name = request.form['Name']
        age = request.form['Age']
        bio = request.form['AboutMe']
        location = request.form['Location']
        imageurl = request.form['imageurl']
        website = request.form['WebsiteUrl']

        con = connect_to_db()
        cur = con.cursor()

        #check if name already exists
        cur.execute("SELECT * FROM users WHERE display_name=%s", (name,))
        row = cur.fetchone()
        if row:
            # return render_template("user.html",name = name,age = age,bio = bio,location = location,imageurl = imageurl,website = website)
            return render_template('register.html', error="Username already exists", error2 = "")
        else:
            cur.execute("Select max(id) from users;")
            user_id = cur.fetchall()[0][0] + 1
            # print(user_id)

            dt = datetime.now(timezone.utc)

            # print(dt)
            # print(age)
            # print(type(age))
            # print(type(bio))
            if age == "":
                age = None
            else:
                age = int(age)
            query = """
                insert into users values %s
                returning *
            """
            my_tuple = (user_id, name, bio, age, dt, dt, location, 0, 0, 0, 0, imageurl, website)

            cur.execute(query, (my_tuple,)) # Notice the comma after my_tuple
            rs = cur.fetchall()
            con.commit()
            # for row in rs:
            #     print(row)

            return render_template("user.html",name = name,age = age,bio = bio,location = location,imageurl = imageurl,website = website, reputation = 0, up_votes = 0, down_votes = 0)


## ------ FOR SIGn In OPTIOnS ---------

@app.route('/user_signin',methods = ['POST', 'GET'])
def user_signin():
   if request.method == 'POST':
        name = request.form['Name']

        con = connect_to_db()
        cur = con.cursor()

        #check if name already exists
        cur.execute("SELECT * FROM users WHERE display_name=%s", (name,))
        row = cur.fetchone()
        if row:
            # print(row)
            bio = row[2]
            age = row[3]
            location = row[6]
            reputation = row[7]
            up_votes = row[8]
            down_votes = row[9]
            imageurl = row[11]
            website = row[12]
            if bio :
                bio = cleanhtml(bio)
            return render_template("user.html",name = name,age = age,bio = bio,location = location,imageurl = imageurl,website = website, reputation = reputation, up_votes = up_votes, down_votes = down_votes)

        else:
            return render_template('register.html', error="", error2="Name does not exist")

query = ""



@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        results = request.form
        tags_list = results.getlist('tags')
        #print(results.getlist('tags'))
        con = connect_to_db()
        cur = con.cursor()
        # tags_tuple = tuple(tags_list)
        t = ""
        for i in tags_list:
            t += "tag = ""'"+i+"'" + " OR "
        ## ------------ Tag search --------------
        query = "CREATE VIEW t1 AS SELECT id FROM tags WHERE "+ t[:-4] +";"
        print(query)
        cur.execute(query)
        query = "CREATE VIEW t2 AS select id,count(id) from t1 group by id order by count(id) desc;"
        cur.execute(query)
        
        cur.execute("select id from t2 limit 10;")
        relevant_question_ids = cur.fetchall()
        question_answer = []
        for i in relevant_question_ids:
            cur.execute("""select * from questions where id= (%s) limit 5;""",(i[0],))
            question_temp = cur.fetchall()
            #print(question_temp)
            question_answer.append(question_temp)
        answers = []
        j = -1
        for i in relevant_question_ids:
            j += 1
            cur.execute("""select * from answers where parentid= (%s) order by score desc limit 1;""",(i[0],))
            answer_temp = cur.fetchall()
            if(len(answer_temp)==0):
                answer_temp.append(("","","","","","NOT ANSWERED YET"))
            question_answer[j].append(answer_temp)

        
        for item in question_answer:
            item[0] = list(item[0])
            item[0][4] = cleanhtml(item[0][4])
            item[0] = tuple(item[0])

            item[1][0] = list(item[1][0])
            item[1][0][5] = cleanhtml(item[1][0][5])
            item[1][0] =tuple(item[1][0])

        return render_template("result.html", results=tags_list,question_answer = question_answer)

# ---- ask questio-------

@app.route('/askquestion',methods = ['POST', 'GET'])
def askquestion():
    if request.method == 'GET':
        return render_template("ask.html")
    elif request.method == 'POST':
        username = request.form['username']
        title = request.form['title']
        body = request.form['body']
        tags = request.form['tags']

        con = connect_to_db()
        cur = con.cursor()
        cur.execute("Select max(id) from users;")
        user_id = cur.fetchall()[0][0] + 1


        query = "select id from users where display_name='"+username+"';"
        cur.execute(query)
        temp = cur.fetchall()
        if(len(temp)==0): 
            return render_template("ask.html")
        OwnerUserId = temp[0][0]

        cur.execute("Select max(id) from questions;")
        Id = cur.fetchall()[0][0] + 1
        print(id)

        CreationDate = datetime.now(timezone.utc)

        query = """
            insert into questions values %s
            returning *
        """

        body = "    "+body+"     "
        my_tuple = (Id,OwnerUserId,CreationDate,0,title,body)

        cur.execute(query, (my_tuple,)) # Notice the comma after my_tuple
        #rs = cur.fetchall()
        con.commit()

        tags = tags.replace(" ", "")
        tags = tags.split(',')
        for tag in tags:
            query = """
                insert into tags values %s
                returning *
            """
            my_tuple = (Id,tag)  
            cur.execute(query, (my_tuple,))

        con.commit()

        return redirect('/question/'+str(Id))


@app.route('/question/<id>', methods=['GET', 'POST'])
def dashboard(id):
    if request.method == 'GET':
        con = connect_to_db()
        cur = con.cursor()
        cur.execute("Select * from questions where id = '%s'"%str(id))
        question = cur.fetchall()
        print("Questions", question)
        question[0] = list(question[0])
        question[0][5] = cleanhtml(question[0][5])
        question[0] = tuple(question[0])
        cur.execute("Select * from users where id = '%s'"%str(question[0][1]))
        user = cur.fetchall()
        cur.execute("Select body, score, creationdate, display_name, answers.id from answers, users where answers.owneruserid = users.id and parentid = '%s' order by score desc"%str(id))
        answers = cur.fetchall()
        for i in range(len(answers)):
            temp = list(answers[i])
            temp[0] = cleanhtml(temp[0])
            answers[i] = tuple(temp)
        return render_template("questions.html", question = question, user = user, answers = answers, num_answer = str(len(answers)))
    if request.method == 'POST':
        username = request.form['username']
        body = request.form['body']

        con = connect_to_db()
        cur = con.cursor()
        cur.execute("Select max(id) from answers;")
        answer_id = cur.fetchall()[0][0] + 1

        # print(username)
        # print(title)
        # print(body)
        # print(tags)

        query = "select id from users where display_name='"+username+"';"
        cur.execute(query)
        temp = cur.fetchall()
        if(len(temp)==0): 
            return redirect("/question/"+str(id))
        OwnerUserId = temp[0][0]

        CreationDate = datetime.now(timezone.utc)

        query = """
            insert into answers values %s
            returning *
        """

        my_tuple = (answer_id,OwnerUserId,CreationDate,id,0,body)

        cur.execute(query, (my_tuple,)) # Notice the comma after my_tuple
        #rs = cur.fetchall()
        con.commit()


        return redirect('/question/'+str(id))


@app.route('/upvote_question/<id>', methods=['GET', 'POST'])
def upvote_question(id):
    con = connect_to_db()
    cur = con.cursor()
    cur.execute("Update questions set score = score + 1 where id = %s;",(id,))
    cur.execute("Select owneruserid from questions where id = %s;",(id,))
    user_id = cur.fetchall()[0][0]
    cur.execute("Update users set up_votes = up_votes + 1  where id  = %s;",(user_id,))
    con.commit()
    return redirect('/question/'+str(id))

@app.route('/downvote_question/<id>', methods=['GET', 'POST'])
def downvote_question(id):
    con = connect_to_db()
    cur = con.cursor()
    cur.execute("Update questions set score = score - 1 where id = %s;",(id,))
    cur.execute("Select owneruserid from questions where id = %s;",(id,))
    user_id = cur.fetchall()[0][0]
    cur.execute("Update users set down_votes = down_votes + 1  where id  = %s;",(user_id,))
    con.commit()
    return redirect('/question/'+str(id))

@app.route('/upvote_answer/<id>/<answerid>', methods=['GET', 'POST'])
def upvote_answer(id,answerid):
    con = connect_to_db()
    cur = con.cursor()
    cur.execute("Update answers set score = score + 1 where id = %s;",(answerid,))
    cur.execute("Select owneruserid from answers where id = %s;",(answerid,))
    user_id = cur.fetchall()[0][0]
    cur.execute("Update users set reputation = reputation + 1  where id  = %s;",(user_id,))
    con.commit()
    return redirect('/question/'+str(id))

@app.route('/downvote_answer/<id>/<answerid>', methods=['GET', 'POST'])
def downvote_answer(id,answerid):
    con = connect_to_db()
    cur = con.cursor()
    cur.execute("Update answers set score = score - 1 where id = %s;",(answerid,))
    cur.execute("Select owneruserid from answers where id = %s;",(answerid,))
    user_id = cur.fetchall()[0][0]
    cur.execute("Update users set reputation = reputation - 1  where id  = %s;",(user_id,))
    con.commit()
    return redirect('/question/'+str(id))
