# -*- coding: utf-8 -*-
"""
Created on Sat May 28 09:10:58 2016

@author: mtkessel
"""

from dip.ui import Application, Form


# Every application needs an Application.
app = Application()

# Create the model.
model = dict(name='')

# Define the view.
view_factory = Form()

# Create an instance of the view bound to the model.
view = view_factory(model)

# Make the instance of the view visible.
view.visible = True

# Enter the event loop.
app.execute()

# Show the value of the model.
print("Name:", model['name'])
