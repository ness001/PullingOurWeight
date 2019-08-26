# LiangLi (Ness)
# Developing Duration: 2019/8/10 - 8/16


from flask import Flask, render_template, request, redirect, url_for, send_file, request, flash,send_from_directory
from flask_wtf import FlaskForm
from wtforms import DateField, RadioField, TextAreaField, StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, Optional

from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import os, random, string

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ness001'
app.config['TESTING'] = True  # in order to bypass recaptcha when in developer mode
app.config['UPLOADED_PHOTOS_DEST'] = basedir + '/photos'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


class certform(FlaskForm):
    yourname = StringField('YOURNAME', validators=[InputRequired(message='Please type in your name'),
                                                   Length(min=1, message='must type in 1+ words')])
    yourphoto = FileField('YOURPHOTO', validators=[FileRequired(message='Please upload your ID photo'),
                                                   FileAllowed(photos, 'Images only!')])
    submit = SubmitField()

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def generate_cert(name, photo_path):
    background = Image.open(
        basedir + "/static/template.jpeg")  # need to be edited on server
    portrait = Image.open(photo_path)
    draw = ImageDraw.Draw(background)
    myfont = ImageFont.truetype(basedir + "/static/PingFang.ttc",
                                size=56)  # font type need to be double-checked
    fillcolor = 'black'
    text = name  # name length should take into consideration

    # location of text
    w, h = draw.textsize(text, font=myfont)
    bounding_box = [1437, 334, 1693, 401]  # upper left corner, lowwr right corner
    x1, y1, x2, y2 = bounding_box
    x = (x2 - x1 - w) / 2 + x1
    y = (y2 - y1 - h) / 2 + y1

    # add text
    draw.text((x, y), text, align='center', font=myfont, fill='#193f5e')

    # location of portrait
    box = (227, 256, 698, 858)  # different image size should take into consideration
    # portrait.thumbnail((box[2] - box[0], box[3] - box[1]))
    portrait = portrait.resize((box[2] - box[0], box[3] - box[1]))
    # portrait = portrait.crop(box)


    # add portrait
    background.paste(portrait, box)
    cert_name = ''.join(random.sample(string.ascii_letters + string.digits, 16)) + '.'
    background.save(basedir+'/static/cert/'+cert_name+'png')

    return cert_name


# temporary save img as png file in IO and show img
def show_img(input_image):
    img_io = BytesIO()
    input_image.save(img_io, 'png')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


@app.route('/cert/<username>/<cert_name>')
def user_cert(username,cert_name):
    return render_template('yourcert.html', name=username+ '\'s ' + 'certification',
                           img_path='/static/cert/' + cert_name + 'png')


@app.route('/cert', methods=['get', 'post'])
def cert():
    yourinfo = certform()
    if yourinfo.validate_on_submit():
        yourname = yourinfo.yourname.data  # get inputted name
        ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 16)) + '.'
        filename = photos.save(yourinfo.yourphoto.data, name=ran_str)
        cert_name = generate_cert(yourname, basedir + '/photos' + '/' + filename)
        # pic.save(basedir+'/cert_generated/'+filename)
        # save certification in var pic
        # return show_img(pic)
        # return render_template('/photos/<filename>',filename=filename)
        # return send_from_directory('cert', cert_name+'png')
        # return render_template('yourcert.html',name=yourname+'\'s '+'certification',img_path='/static/cert/'+cert_name+'png')
        return redirect(url_for('user_cert',username=yourname,cert_name=cert_name,_external=True))
    return render_template('certification.html', form=yourinfo)


class surveyform(FlaskForm):
    # date = DateField('Clean Up Date', validators=[InputRequired()])

    identity = RadioField('identity', coerce=int,
                          choices=[(1, 'Dow employee'), (2, 'Dow contractor'), (3, 'Dow customer'),
                                   (4, 'Dow family member'), (5, 'Community partner or other stakeholder')],
                          validators=[InputRequired()])
    satisfactory = RadioField('satisfactory', coerce=int, choices=[
        (2, 'Very satisfied'), (1, 'Somewhat satisfied'), (0, 'Neither satisfied nor dissatisfied'),
        (-1, 'Somewhat dissatisfied'), (-2, 'Very dissatisfied')], validators=[InputRequired()])
    organization = RadioField('organization', coerce=int, choices=[
        (2, 'Very organized'), (1, 'Somewhat organized'), (0, 'Neither organized nor disorganized'),
        (-1, 'Somewhat disorganized'), (-2, 'Very disorganized')], validators=[InputRequired()])
    preparation = RadioField('preparation', coerce=int, choices=[
        (2, 'Very prepared'), (1, 'Somewhat prepared'), (0, 'Neither prepared nor unprepared'),
        (-1, 'Somewhat unprepared'), (-2, 'Very unprepared')], validators=[InputRequired()])
    # colleague = RadioField('colleague', coerce=int,
    #                        choices=[(3, ''), (2, ''), (1, ''), (0, ''), (-1, ''), (-2, ''), (-3, '')])
    # community = RadioField('community', coerce=int,
    #                        choices=[(3, ''), (2, ''), (1, ''), (0, ''), (-1, ''), (-2, ''), (-3, '')])
    # family = RadioField('family', coerce=int,
    #                     choices=[(3, ''), (2, ''), (1, ''), (0, ''), (-1, ''), (-2, ''), (-3, '')])
    colleague = SelectField('colleague', coerce=int,
                            choices=[(3, 'Exceptional'), (2, 'Excellent'), (1, 'Good'), (0, 'Fair'), (-1, 'Poor'),
                                     (-2, 'Very poor'), (-3, 'Not applicable')], validators=[InputRequired()])
    community = SelectField('community', coerce=int,
                            choices=[(3, 'Exceptional'), (2, 'Excellent'), (1, 'Good'), (0, 'Fair'), (-1, 'Poor'),
                                     (-2, 'Very poor'), (-3, 'Not applicable')], validators=[InputRequired()])
    family = SelectField('family', coerce=int,
                         choices=[(3, 'Exceptional'), (2, 'Excellent'), (1, 'Good'), (0, 'Fair'), (-1, 'Poor'),
                                  (-2, 'Very poor'), (-3, 'Not applicable')], validators=[InputRequired()])
    text = TextAreaField('enter your comments', validators=[Optional()])

    submit = SubmitField()


class survey_zh(FlaskForm):
    # date = DateField('Clean Up Date', validators=[InputRequired()])

    identity = RadioField('identity', coerce=int,
                          choices=[(1, '陶氏员工'), (2, '陶氏承包商'), (3, '陶氏顾客'),
                                   (4, '陶氏家庭成员'), (5, '陶氏社区伙伴或利益相关者')],
                          validators=[InputRequired()])
    satisfactory = RadioField('satisfactory', coerce=int, choices=[
        (2, '非常满意'), (1, '比较满意'), (0, '一般'),
        (-1, '比较不满意'), (-2, '非常不满意')], validators=[InputRequired()])
    organization = RadioField('organization', coerce=int, choices=[
        (2, '非常有组织性'), (1, '比较有组织性'), (0, '一般'),
        (-1, '比较无组织性'), (-2, '非常无组织性')], validators=[InputRequired()])
    preparation = RadioField('preparation', coerce=int, choices=[
        (2, '准备充分'), (1, '有点准备'), (0, '一般'),
        (-1, '没怎么准备'), (-2, '毫无准备')], validators=[InputRequired()])
    # colleague = RadioField('colleague', coerce=int,
    #                        choices=[(3, ''), (2, ''), (1, ''), (0, ''), (-1, ''), (-2, ''), (-3, '')])
    # community = RadioField('community', coerce=int,
    #                        choices=[(3, ''), (2, ''), (1, ''), (0, ''), (-1, ''), (-2, ''), (-3, '')])
    # family = RadioField('family', coerce=int,
    #                     choices=[(3, ''), (2, ''), (1, ''), (0, ''), (-1, ''), (-2, ''), (-3, '')])
    colleague = SelectField('colleague', coerce=int,
                            choices=[(3, '棒极了'), (2, '极好'), (1, '好'), (0, '一般'), (-1, '差'),
                                     (-2, '非常差'), (-3, '本条对我不适用')], validators=[InputRequired()])
    community = SelectField('community', coerce=int,
                            choices=[(3, '棒极了'), (2, '极好'), (1, '好'), (0, '一般'), (-1, '差'),
                                     (-2, '非常差'), (-3, '本条对我不适用')], validators=[InputRequired()])
    family = SelectField('family', coerce=int,
                         choices=[(3, '棒极了'), (2, '极好'), (1, '好'), (0, '一般'), (-1, '差'),
                                  (-2, '非常差'), (-3, '本条对我不适用')], validators=[InputRequired()])
    text = TextAreaField('enter your comments', validators=[Optional()])

    submit = SubmitField('提交')


import datetime
import json
import csv


def gmt_converter(o):
    if isinstance(o, datetime.datetime):
        GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
        return datetime.datetime.strptime('Wed, 02 Jan 2019 00:00:00 GMT', GMT_FORMAT) + datetime.timedelta(hours=8)

@app.route('/zh',methods=['get','post'])
def zh():
    szh= survey_zh()
    if szh.validate_on_submit():
        data = szh.data

        toCSV = [data]
        keys = toCSV[0].keys()
        with open(basedir+'/static/data.csv', 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(toCSV)
        return redirect(url_for('cert'))
    return render_template('survey2019_zh.html', form=szh)



@app.route('/', methods=['get', 'post'])
def survey():
    sform = surveyform()
    if sform.validate_on_submit():
        data = sform.data

        toCSV = [data]
        keys = toCSV[0].keys()
        with open(basedir+'/static/data.csv', 'a') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(toCSV)

        # with open(basedir+'/static/survey_data.json') as f:
        #     j = json.load(f)
        # j.update(data)
        # with open(basedir + '/static/survey_data.json','w') as f:
        #     json.dump(j,f,default=str)


        # with open(basedir+'/static/survey_data.json', 'w', encoding='utf-8') as file:
        #     nj=json.dumps(data,default=str)
        #     file.write(nj)
        #     file.close()
        # flash(json.dumps(data, default=str))
        # flash(data)
        return redirect(url_for('cert'))
    return render_template('survey2019.html', form=sform)




class meme_form(FlaskForm):
    words = StringField('words', validators=[InputRequired(message='Please type in your words'),
                                                   Length(min=1, message='must type in 1+ words')])
    submit = SubmitField()


def gen_meme(words):
    background = Image.open(
        basedir + "/static/IMG_8223.jpg")  # need to be edited on server
    draw = ImageDraw.Draw(background)
    myfont = ImageFont.truetype(basedir + "/static/PingFang.ttc", #you should not use right click copy path on pycharm since it wont include /
                                size=36)  # font type need to be double-checked
    text = words  # name length should take into consideration

    # location of text
    w, h = draw.textsize(text, font=myfont)
    bounding_box = [63, 243, 404, 284]  # upper left corner, lowwr right corner
    x1, y1, x2, y2 = bounding_box
    x = (x2 - x1 - w) / 2 + x1
    y = (y2 - y1 - h) / 2 + y1

    # add text
    draw.text((x, y), text, align='center', font=myfont, fill='black')
    return background


@app.route('/meme', methods=['get', 'post'])
def meme():
    yourmeme = meme_form()
    if yourmeme.validate_on_submit():
        words = yourmeme.words.data  # get inputted name

        pic = gen_meme(words)
        # pic.save(basedir+'/cert_generated/'+filename)
        # save certification in var pic
        return show_img(pic)
        # return
    return render_template('meme.html', form=yourmeme)



if __name__ == '__main__':
    app.run(debug=True)
