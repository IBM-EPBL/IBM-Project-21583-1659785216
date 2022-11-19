from flask import *
#import re
import ibm_db
import sendgrid
import os
from sendgrid.helpers.mail import *

#SendGrid Integration
sg = sendgrid.SendGridAPIClient(api_key='****SENDGRID API KEY****')

#ibm_db connection
conn = ibm_db.connect("DATABASE=bludb; HOSTNAME=3883e7e4-18f5-4afe-be8c-fa31c41761d2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud; PORT=31498; SECURITY=SSL; SSLServerCertificate=DigiCertGlobalRootCA.crt; UID=ltv80221; PWD=8fS5XCKIWaGcUCUW",'','')


app = Flask(__name__)


@app.route('/')
def hello_world():
  return redirect('/login')
  #return render_template('index.html')

#Registration process
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
  msg = ' '
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    sql = "SELECT * FROM users WHERE email =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if account:
      msg = 'Account already exists !'
    elif not username or not password or not email:
      msg = 'Please fill the Missing Details !'
    
    else:
      insert_sql = "INSERT INTO users VALUES (?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, username)
      ibm_db.bind_param(prep_stmt, 2, email)
      ibm_db.bind_param(prep_stmt, 3, password)
      ibm_db.execute(prep_stmt)
      msg = 'Account created successfully '

      from_email = Email("********")  # sendgrid registered mail id
      to_email = To(email)
      subject = "Thank You For Registration"
      content = Content("text/plain", "Welcome to our S-Mart App")
      mail = Mail(from_email, to_email, subject, content)
      response = sg.client.mail.send.post(request_body=mail.get())
      print(response.status_code)
      print(response.body)
      print(response.headers)
      
      return render_template('login.html',msg=msg)
  return render_template('register.html',msg=msg)

#Login process
@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/checkrec',methods = ['POST', 'GET'])
def checkrec():
  msg = ' '
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']     
    sql = "SELECT * FROM users WHERE Email =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_both(stmt)    
    accounts=account   
    if (account):
      if(password == accounts['PASSWORD']):
        msg = 'Logged in successfully !'
        return render_template('index.html',msg=msg)
      else :
        msg='Wrong Credentials'
  return  render_template('login.html',msg=msg)

#Admin Login process
@app.route('/adminlogin')
def adminlogin():
  return render_template('adminlogin.html')

@app.route('/checkrecadmin',methods = ['POST', 'GET'])
def checkrecadmin():
  msg = ' '
  if request.method == 'POST':
    adminemail = request.form['adminemail']
    adminpassword = request.form['adminpassword']     
    sql = "SELECT * FROM admin WHERE adminemail =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,adminemail)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_both(stmt)    
    accounts=account   
    if (account):
      if(adminpassword == accounts['ADMINPASSWORD']):
        msg = 'Logged in successfully !'
        return redirect('/adminhome')
      else :
        msg='Wrong Credentials'
  return  render_template('adminlogin.html',msg=msg)

#Admin Dashboard
@app.route('/adminhome')
def adminhome():
  products = []
  sql = "SELECT * FROM pro "
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    products.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)
  if products:
    return render_template('adminhome.html',products=products)

#Adding products by Admin
@app.route('/addproduct',methods=['POST','GET'])
def addproduct():
  if request.method == 'POST':
    image = request.form['image']
    productname = request.form['productname']
    cost = request.form['cost']
    category = request.form['category']
    insert_sql = "INSERT INTO pro VALUES (?,?,?,?)"
    stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(stmt, 1, image)
    ibm_db.bind_param(stmt, 2, productname)
    ibm_db.bind_param(stmt, 3, cost)
    ibm_db.bind_param(stmt, 4, category)
    ibm_db.execute(stmt)
    return redirect('/adminhome')

#Deleting products by Admin
@app.route('/delete/<productname>')
def delete(productname):
  sql = f"SELECT * FROM pro WHERE productname='{escape(productname)}'"
  stmt = ibm_db.exec_immediate(conn, sql)
  product = ibm_db.fetch_row(stmt)
  if product:
    sql = f"DELETE FROM pro WHERE productname='{escape(productname)}'"
    print(sql)
    stmt = ibm_db.exec_immediate(conn, sql)
    products = []
    sql = "SELECT * FROM pro"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
      products.append(dictionary)
      dictionary = ibm_db.fetch_both(stmt)
    if products:
      return redirect("/adminhome")


#Order Confirmation Page
@app.route('/ordertracking')
def ordertracking():
  return render_template('ordertracking.html')

@app.route('/proceed')
def proceed(email):
  from_email = Email("*********") #sendgrid registered mail id
  to_email = To(email)
  subject = "Your Payment is Successful"
  content = Content("text/plain", "Thank You For Purchasing our Product. Your order is placed and We will soon let you know about your order status. Stay Connected!")
  mail = Mail(from_email, to_email, subject, content)
  response = sg.client.mail.send.post(request_body=mail.get())
  print(response.status_code)
  print(response.body)
  print(response.headers)
  return redirect('/ordertracking')



#Payment page
@app.route('/payment')
def payment():
    return render_template('payment.html')

#About Page
@app.route('/about')
def about():
    return render_template('about.html')

#Help Page
@app.route('/help')
def help():
    return render_template('help.html')


#User Products Page
@app.route('/shop')
def shop():
  products = []
  sql = "SELECT * FROM pro "
  stmt = ibm_db.exec_immediate(conn, sql)
  dictionary = ibm_db.fetch_both(stmt)
  while dictionary != False:
    products.append(dictionary)
    dictionary = ibm_db.fetch_both(stmt)
  if products:
    return render_template('product.html',products=products)
  
#User products page based on user preference
@app.route('/filter',methods = ['POST', 'GET'])
def filter():
  if request.method == 'POST':
    search = request.form['search']
    if search=="Shirt" or search=="shirt":  
      products = []
      sql = "SELECT * FROM pro where category='Shirt'"
      stmt = ibm_db.exec_immediate(conn, sql)
      dictionary = ibm_db.fetch_both(stmt)
      while dictionary != False:
        products.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
      if products:
        return render_template('product.html',products=products)
    elif search=="Hoodie" or search=="hoodie":
      products = []
      sql = "SELECT * FROM pro where category='Hoodie'"
      stmt = ibm_db.exec_immediate(conn, sql)
      dictionary = ibm_db.fetch_both(stmt)
      while dictionary != False:
        products.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
      if products:
        return render_template('product.html',products=products)
    elif search=="Saree" or search=="saree":
      products = []
      sql = "SELECT * FROM pro where category='Saree'"
      stmt = ibm_db.exec_immediate(conn, sql)
      dictionary = ibm_db.fetch_both(stmt)
      while dictionary != False:
        products.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
      if products:
        return render_template('product.html',products=products)
    elif search=="Chudi" or search=="chudi":
      products = []
      sql = "SELECT * FROM pro where category='Chudi'"
      stmt = ibm_db.exec_immediate(conn, sql)
      dictionary = ibm_db.fetch_both(stmt)
      while dictionary != False:
        products.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
      if products:
        return render_template('product.html',products=products)
  return redirect('/shop')




if __name__ == '__main__':
    app.run(debug=True)






