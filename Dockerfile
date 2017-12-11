FROM python:3

ADD /master/master.py /

ADD /slave/slave.py /

RUN pip install pystrich

CMD [ "python", "./my_script.py" ]