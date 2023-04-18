#!/usr/bin/env python
# coding: utf-8

# # Imports

# ## To print markdown in notebook

# In[1]:


from IPython.display import Markdown as md


# ## arcgis imports

# In[2]:


from arcgis.gis import GIS
from arcgis.geometry import Geometry
from arcgis.geometry import Point
from arcgis.geometry import SpatialReference


# ## Date package

# In[3]:


import arrow


# # My First Code

# In[4]:


gis = GIS('pro', trust_env=True)


# ## My gis instance

# In[5]:


gis


# In[6]:


if gis:
    print('Sucess')
else:
    print('Some Error Happend')


# # My Geometry

# ## My datum

# In[7]:


WGS_84 = SpatialReference(4326)


# ## My geometrys

# ### Points

# In[8]:


point = Geometry({'x': -43.214, 'y': -24.341, "SpatialReference": WGS_84})
point


# In[9]:


point2 = Point({'x': -43.214, 'y': -24.341, "SpatialReference": WGS_84})
point2


# In[10]:


point.equals(point2)


# ### Lines

# In[11]:


Geometry({"rings" : [[
    [-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832],
    [-97.06138,32.837]],[[-97.06326,32.759],[-97.06298,32.755],[-97.06153,32.749],
      [-97.06326,32.759]]],
 "spatialReference" : WGS_84}).buffer(0.0055)


# # Executed in:

# In[12]:


today = arrow.now()
today


# In[13]:


md(f"# Run {today.format('DD/MM/YYYY')}")

