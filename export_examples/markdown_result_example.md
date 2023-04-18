# Imports

## To print markdown in notebook


```python
from IPython.display import Markdown as md
```

## arcgis imports


```python
from arcgis.gis import GIS
from arcgis.geometry import Geometry
from arcgis.geometry import Point
from arcgis.geometry import SpatialReference

```

## Date package


```python
import arrow
```

# My First Code


```python
gis = GIS('pro', trust_env=True)
```

## My gis instance


```python
gis
```




GIS @ <a href="https://imagem.maps.arcgis.com/">https://imagem.maps.arcgis.com/</a>




```python
if gis:
    print('Sucess')
else:
    print('Some Error Happend')
```

    Sucess
    

# My Geometry

## My datum


```python
WGS_84 = SpatialReference(4326)
```

## My geometrys

### Points


```python
point = Geometry({'x': -43.214, 'y': -24.341, "SpatialReference": WGS_84})
point
```




![svg](markdown_result_example_files/markdown_result_example_17_0.svg)




```python
point2 = Point({'x': -43.214, 'y': -24.341, "SpatialReference": WGS_84})
point2
```




![svg](markdown_result_example_files/markdown_result_example_18_0.svg)




```python
point.equals(point2)
```




    True



### Lines


```python
Geometry({"rings" : [[
    [-97.06138,32.837],[-97.06133,32.836],[-97.06124,32.834],[-97.06127,32.832],
    [-97.06138,32.837]],[[-97.06326,32.759],[-97.06298,32.755],[-97.06153,32.749],
      [-97.06326,32.759]]],
 "spatialReference" : WGS_84}).buffer(0.0055)
```




![svg](markdown_result_example_files/markdown_result_example_21_0.svg)



# Executed in:


```python
today = arrow.now()
today
```




    <Arrow [2023-04-18T16:57:32.133714-03:00]>




```python
md(f"# Run {today.format('DD/MM/YYYY')}")
```




# Run 18/04/2023


