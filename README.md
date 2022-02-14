#### Что это  
  
Это находящийся в разработке проект по созданию управляющих программ для удаленного управления вегетационными стендами в лаборатории О-125  
Библиотека написана на языке python3 и предназначена для работы на unix-подобных системах.  

#### Что за система управления  

Децентрализованная сеть состоит из узлов-нод, каждая из которых представляет собой отдельный линукс-процесс. Ноды могут быть развернуты на одном или нескольких компьютерах. В случае нескольких компьютеров их нужно объединить в одну локальную сеть, например с помощью openvpn.   
Ноды общаются между собой с помощью передачи пакетов по tcp, это реализовано с помощью фреймворка ZMQ.  
Логика работы с библиотекой такова: пользователь устанавливает себе эту библиотеку, на ее базе пишет свое приложение из нескольких параллельных нод, используя примитивы и абстракции, предлагаемые авторами.  
Затем он переносит их на свой компьютер/компьютеры, и там запускает. Для общения пользователя с нодами есть написанный консольный клиент в папке utils.  

#### Как в целом это устроено  

Проект представляет собой группу подмодулей, содержащих функционально сгруппированные скрипты для создания нод ...  

Все модули хранятся в папке plexus. В ней есть:  
```
plexus/
├── LICENSE
├── dist
├── pyproject.toml
├── README.md
├── requirements.txt
├── setup.cfg
├── src/
│   └──plexus
│		├── __init__.py
│   	└── nodes_package/
│       	├── __init__.py
│       	└── example.py
│   	└── smth_package/
│       	├── __init__.py
│       	└── example.py
│   	└── .../
│       	├── __init__.py
│       	└── ...
└── tests/
```  
Каждая папка в src/plexus/ хранит подмодуль нашей либы, который умеет делать что-то свое. Иногда они могут ссылаться друг на друга таким образом:  
```
from plexus.nodes_package.example import somefunc  
```  
Вроде бы это нормально  

https://packaging.python.org/en/latest/tutorials/packaging-projects/  

#### Как установить простым способом

- Скачать wheel-файл из папки dist репозитория:  

- Сделать новый venv  
```
python3 -m venv new_env  
source new_env/bin/activate  
```  
- войти в созданную папку, скопировать туда скачанный wheel-файл    

- установить wheel-файл:  
```
python3 -m pip install super_package_hahah-0.0.1-py3-none-any.whl --upgrade  
```
- теперь, активируя этот venv вы можете работать с собранным проектом, не боясь загадить всяким мусором свой основной питон и его dist-packages. Чтобы выйти из venv нужно ввести   
```
deactivate
```  
- важное примечание: ваши файлы не должны находиться внутри папки где venv. То есть вы этот venv активируете, а затем идете в другую папку и там пишете код и запускаете его. Питон будет настроен на это виртуальное окружение где бы ни был ваш проект, пока вы не деактивируете venv. Также важно настроить .gitignore так, чтобы папка venv в него не попадала.

- можно настроить ваш Pycharm для работы с вашим кастомным виртуальным окружением.   
https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html#existing-environment  

#### Как установить сложным способом

Для установки кода нужно следующее:  

1. Собрать wheel-файл:  

- Проверить что у вас есть пакеты setuptools, venv, pip
- Склонировать себе на пк репозиторий  
- Перейти в основную папку проекта, где лежит .toml-файл и   
- собрать новый wheel-файл, используя build:  
```
python3 -m build
```
- он появится в подпапке dist  

2. Установить wheel-файл:  

- Сделать новый venv  
```
python3 -m venv new_env  
source new_env/bin/activate  
```  
- войти в созданную папку, скопировать туда созданный wheel-файл    

- установить wheel-файл:  
```
python3 -m pip install super_package_hahah-0.0.1-py3-none-any.whl --upgrade  
```
- теперь используя этот venv вы можете работать с собранным проектом, не боясь загадить всяким мусором свой основной питон и его dist-packages. 

#### Как быть если вы хотите что-то обновить в коде

- Склонировать себе на пк репозиторий  
- Написать крутые улучшения  
- протестить их используя предыдущий пункт  
- создать pull-request и написать разработчикам  


#### Как писать .cfg-файл  

https://setuptools.pypa.io/en/latest/userguide/quickstart.html  

- зависимости после install_requires =  
- модули, которые надо включать после  
```
[options.packages.find]
where = src
```

вот пример  

```
[metadata]
name = example-package-BIG-BROWN-MONKEY
version = 0.0.1
author = Example Author
author_email = author@example.com
description = A small example package
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/pypa/sampleproject
project_urls =
    Bug Tracker = https://github.com/pypa/sampleproject/issues
classifiers =
    Programming Language :: Python :: 3
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent

[options]
package_dir =
    = src
packages = find:
install_requires = 
	requests
	peppercorn
	pytest
python_requires = >=3.6

[options.packages.find]
where = src
include=example_package, example_package_2
```

