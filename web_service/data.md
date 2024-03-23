# СТРУКТУРА ДАТАСЕТА
Датасет состоит из пересечения двух публичных датасетов, которые связывают изображения со словесным описанием их содержимого на английском языке - MS COCO и VisualGenome.
Датасет содержит 49312 наблюдений.

Данные в формате pickle доступны для скачивания по [ссылке](https://drive.google.com/file/d/1KTq20OiwUeXSc1KCu2tnmwcMk0qoY2_w/view?usp=sharing).

Для каждого наблюдения существуют следующие параметры:

``vg_id`` - уникальный id изображения из visual_genome <br>
``coco_id`` - уникальный id изображения из coco <br>
``objects``<br>
``attributes``<br>
``relationships``<br>
``regional descriptions``<br>
``caption``

## [COCO](https://cocodataset.org/#home)
Из датасета COCO были взяты аннотации к изображениям. Каждое изображение содержит 5 вариаций аннотаций. Планируется из 5 аннотаций оставить одно с наибольшим кол-вом различных частей речи.

## [VisualGenome](https://homes.cs.washington.edu/~ranjay/visualgenome/index.html)
Были использованы следующие части датасета:
- objects_v1.2.0
- attributes_v1.2.0
- regional descriptions_v1.2.0
- relationships_v1.2.0

Все примеры ниже произведены для ![этого изображения](https://huggingface.co/datasets/visual_genome/viewer/attributes_v1.2.0?row=0&image-viewer=image-0-0CC2DCEE6FA307D330BD85DD3826A9B055277CE1):


### 1. Objects -> List[Dict]
``object_id``: уникальный id объекта <br>
``names``: список имен, ассоциированных с объектом<br>
``synsets``: список синсетов [WordNet](https://www.tutorialspoint.com/synsets-for-a-word-in-wordnet-in-nlp) <br>
<hr>

*Пример:*

```
[{
    "object_id": 1058498,
    "names": [ "clock" ], 
    "synsets": [ "clock.n.01" ], 
    }, 
{
    "object_id": 5046,
    "names": [ "street" ],
    "synsets": [ "street.n.01" ] 
    },
{
    "object_id": 5045,
    "names": [ "shade" ],
    "synsets": [ "shade.n.01" ]}, 
{
    "object_id": 1058529, 
    "names": [ "man" ],
    "synsets": [ "man.n.01" ]},
{
    "object_id": 5048, 
    "names": [ "sneakers" ],
    "synsets": [ "gym_shoe.n.01" ]}, 
    
    ...

]
```

### 2. Attributes -> List[Dict]

Описания объектов (какой? какого рода?)

Структура:

*часть описывающая **объект**:*<br>

``object_id``: уникальный id объекта<br>
``names``: список имен, ассоциированных с объектом<br>
``synsets``: список WordNet synsets<br>

*часть, описывающая **атрибуты** объекта:*<br>

``attributes``: список атрибутов объекта
<hr>

*Пример:*
```
[{
    "object_id": 1058498, 
    "names": [ "clock" ],
    "synsets": [ "clock.n.01" ],
    "attributes": [ "green", "tall" ]},
{
    "object_id": 5046,
    "names": [ "street" ],
    "synsets": [ "street.n.01" ],
    "attributes": [ "sidewalk" ]},
{
     "object_id": 5045, 
     "names": [ "shade" ],
     "synsets": [ "shade.n.01" ],
     "attributes": null },
{
    "object_id": 1058529,
    "names": [ "man" ], 
    "synsets": [ "man.n.01" ],
    "attributes": null }, 
{
    "object_id": 5048,
    "names": [ "sneakers" ],
    "synsets": [ "gym_shoe.n.01" ],
    "attributes": [ "grey" ]}, 
{
    "object_id": 5050, 
    "names": [ "headlight" ],
    "synsets": [ "headlight.n.01" ],
    "attributes": [ "off" ]}

    ...

]
```

### 3. Relationships -> List[Dict]
Глаголы и глагольные производные, описывающие связь объект-субъект. <br>
Объект и субъект содержатся ``objects``.

<br>

Структура:

``relationship_id``: уникальный id связи/отношения

*часть, описывающая **объект**:*

``object_id``: уникальный id объекта<br>
``names``: список имен, ассоциированных с объектом<br>
``synsets``: список WordNet synsets<br>

*часть, описывающая **субъект**:*

``object_id``: уникальный id объекта<br>
``names``: список имен, ассоциированных с объектом<br>
``synsets``: список WordNet synsets<br>

``predicate``: предикат, описывающий отношения между субъектом и объектом 
<hr>

*Пример:*
```
[{
    "relationship_id": 15927, 
    "predicate": "ON", 
    "synsets": "['along.r.01']", 
    "subject": 
        { "object_id": 5045, 
        "names": [ "shade" ], 
        "synsets": [ "shade.n.01" ]}, 
    "object": 
        { "object_id": 5046, 
        "names": [ "street" ], 
        "synsets": [ "street.n.01" ]}}, 
{
    "relationship_id": 15928, 
    "predicate": "wears", 
    "synsets": "['wear.v.01']", 
    "subject": 
        { "object_id": 1058529, 
        "names": [ "man" ], 
        "synsets": [ "man.n.01" ]}, 
    "object": 
        {"object_id": 5048, 
        "names": [ "sneakers" ], 
        "synsets": [ "gym_shoe.n.01" ]}}, 
{ 
    "relationship_id": 15929, 
    "predicate": "has", 
    "synsets": "['have.v.01']", 
    "subject": 
        {"object_id": 5049, 
        "names": [ "car" ], 
        "synsets": [ "car.n.01" ]}, 
    "object": 
        {"object_id": 5050, 
        "names": [ "headlight" ], 
        "synsets": [ "headlight.n.01" ] }}, 
{ 
    "relationship_id": 15930, 
    "predicate": "ON", 
    "synsets": "['along.r.01']", 
    "subject": 
        {"object_id": 1058507, 
        "names": [ "sign" ], 
        "synsets": [ "sign.n.02" ] }, 
    "object": 
        { "object_id": 1058508, 
        "names": [ "building" ], 
        "synsets": [ "building.n.01" ] } }

        ...
]
```


### 4. Region description -> List[Dict]

``region_id`` - уникальный id региона
``image_id`` - уникальный id изображения (соответсвует vg_id)
``phrase``: фраза, описывающая регион
<hr>

*пример:*

```
[{
    "region_id": 1382, 
    "image_id": 1, 
    "phrase": "the clock is green in colour"}, 
{ 
    "region_id": 1383, 
    "image_id": 1, 
    "phrase": "shade is along the street "}, 
{
    "region_id": 1384, 
    "image_id": 1, 
    "phrase": "man is wearing sneakers"}, 
{ 
    "region_id": 1385,
    "image_id": 1,
    "phrase": "cars headlights are off"}
...

]
```
### 5. Captions -> List

Список из 5 аннотаций
<hr>

*пример:*
```
Tourists will find blue signs like this in Great Britain.
The road sign shows that this too far from  connections.
A blue sign giving directions to three towns.
a close up of a street sogn with buildings in the background
Street signs point people in traffic in the right direction
```

