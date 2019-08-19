#!/usr/bin/env python
# coding: utf-8

# In[10]:


from PIL import Image,ImageDraw,ImageFont


# In[17]:


background = Image.open(r"/Users/ness001/Library/Mobile Documents/com~apple~CloudDocs/intern/certification/image001.png")
portrait = Image.open('/Users/ness001/Library/Mobile Documents/com~apple~CloudDocs/梁力个人信息/证件头像/梁力证件照.JPG')

draw = ImageDraw.Draw(background)
myfont = ImageFont.truetype(u"/System/Library/Fonts/STHeiti Medium.ttc", size=20) #font type need to be double-checked
fillcolor = 'black'
text=u"梁力" # name length should take into consideration

# location of text
w,h=draw.textsize(text, font=myfont)
bounding_box = [248, 370, 374, 396] #upper left corner, lowwr right corner 
x1, y1, x2, y2 = bounding_box 
x = (x2 - x1 - w)/2 + x1
y = (y2 - y1 - h)/2 + y1

#add text
draw.text((x, y), text, align='center', font=myfont,fill='black')

#location of portrait
box=(474,279,573,406)#different image size should take into consideration
portrait=portrait.resize((box[2] - box[0], box[3] - box[1]))

#add portrait
background.paste(portrait,box)

background.show()
background.save('edited.png')


# In[14]:


#apply it on a server


# In[ ]:




