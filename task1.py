from flask import Flask, render_template, request, url_for, send_file, send_from_directory
from flask_pymongo import PyMongo
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from app import db
db.create_all()
db.session.commit()

import os
import csv
import json
import xlrd
import pandas as pd

app = Flask(__name__, template_folder='Templates')

uploads_dir = os.path.join(app.instance_path,'uploads')

os.makedirs(uploads_dir,0o777,exist_ok=True)

app.config['MONGO_URI'] = 'mongodb://sanchi:qwerty1234@ds147125.mlab.com:47125/backend_task'
app.config['DOWNLOAD_FOLDER'] = uploads_dir
app.config['UPLOAD_FOLDER'] = uploads_dir
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['mongodb://sanchi:qwerty1234@ds147125.mlab.com:47125/backend_task']
mongo = PyMongo(app)

AllowedFiles = ['csv', 'xls', 'xlsx']


#RENDERING INDEX.HTML
@app.route('/', methods=["GET"])
def index():
    return render_template('index.html')


#UPLOAD POST METHOD
@app.route('/upload', methods=["POST"])
def upload():

    if (request.method =="POST"):

        
        FileDetails = mongo.db.FileDetails
        File = request.files['UploadFile']
        
        
        if not File:
            return "No File has been Uploaded!"
        filename = File.filename
        filename = filename.split('.')
        FileDetails = mongo.db[filename[0]]
        # print(File.read())
        if(filename[1].lower() in AllowedFiles):

            # File.save(os.path.join(uploads_dir,secure_filename(File.filename)))

            if filename[1]=='csv':
                data_csv = pd.read_csv(File)
                FileDetails.insert_many(data_csv.T.to_dict().values())
               

            else:
                data_xls = pd.read_excel(File)
                FileDetails.insert_many(data_xls.T.to_dict().values())
               
            return File.filename + " has been uploaded successfully!!"

        else:

            return "Invalid file format. Files with extensions .csv, .xls, .xlsx only are allowed!!"


#UPLOAD GET METHOD
@app.route('/upload', methods=["GET"])
def uploading():
    return render_template("uploading.html")


#VIEW FILES
@app.route('/view_files/', methods=["GET"])
def return_files():
    list_of_files = mongo.db.collection_names()
    list_of_files.remove("system.indexes")
    return render_template("View_files.html",f=list_of_files)


#VIEW FILES NAMEWISE      
@app.route('/view_files/<filename>', methods=["GET"])
def view_files(file_name):
    print(file_name)
    columns = list(mongo.db[file_name].find({},{"_id": 0}))
    headers = list(columns[0].keys())
    print(columns)
    print(headers)
    return render_template("view_data.html", columns=columns, headers=headers)


#DELETE FILE
@app.route('/delete_files/', methods=["GET"])
def show_files():
    list_of_files = mongo.db.collection_names()
    list_of_files.remove("system.indexes")
    return render_template("Delete_files.html",f=list_of_files)


#DELETE FILES NAMEWISE
@app.route('/delete_files/<filename>', methods=["GET"])
def delete_files(filename):
    if filename in mongo.db.collection_names():
        mongo.db[filename].drop()
        return filename+ " has been deleted"
    else:
        return "File not Found!"


if(__name__) == "__main__":
    app.run(debug=True)
