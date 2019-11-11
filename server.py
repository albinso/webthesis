from flask import Flask, request, send_from_directory
import os
import sys
import re
import zipfile
import shutil
from distutils.dir_util import copy_tree, remove_tree
app = Flask(__name__)
watchpath = sys.argv[1]



fields = ["foo", "bar"]

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def listdirs(regex):
    boxes = []
    page = '<form action="/action" method="post">'
    for f in os.listdir(watchpath):
        box = '<input type="checkbox" name="{0}" value="{0}" {1}>{0}</input><br />'.format(f, "{}") 
        if re.match(regex, f):
            box = box.format("checked")
        else:
            box = box.format("")
        boxes.append(box)
    page += ''.join(boxes)
    page += '<input type="submit" name="submit_button" value="download">'
    page += '<input type="submit" name="submit_button" value="delete">'
    page += "</form>"
    print(page)
    return page

def filterbar(value="regex"):
    page = '<form action="/filter" method="post">'
    bar = '<input type="text" name="filter" value="{}"></input>'.format(value)
    page += bar
    page += '<input type="submit" name="submit_button" value="filter">'
    page += "</form>"
    return page

@app.route('/')
def mainpage():
    return filtermainpage(".*")

@app.route('/<pattern>')
def filtermainpage(pattern):
    page = '''<html>
  <head>
    <title>Flask app</title>
    <link rel="stylesheet" href="static/css/main.css">
  </head>
    '''
    return page + filterbar(pattern) + listdirs(pattern)

@app.route("/action", methods=["POST"])
def delete_or_download():
    if request.form['submit_button'] == "delete":
        return delete()
    elif request.form['submit_button'] == "download":
        return download()

@app.route("/filter", methods=["POST"])
def filter():
    regex = request.form['filter']
    return filtermainpage(regex)


def delete():
    for key in request.form.keys():
        if key == "submit_button":
            continue
        remove_tree(watchpath + "/" + key)
    return filtermainpage("$^")

def download():
    #os.remove("result.zip")
    remove_tree("result")
    zipf = zipfile.ZipFile(app.root_path + '/result.zip', 'w', zipfile.ZIP_DEFLATED)
    print(app.root_path + "/result.zip")
    for key in request.form.keys():
        if key == "submit_button":
            continue
        copy_tree(watchpath + "/" + key, "result/" + key)
    zipdir("result", zipf)
    zipf.close()

    return send_from_directory(app.root_path, "result.zip", as_attachment=True) 

if __name__ == '__main__':
    app.run()
