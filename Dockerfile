FROM python:3.6.2

ENV KBserver=http://localhost:7474
ENV KBuser=neo4j
ENV KBpassword=password
ENV LOAD_TEST_DATA=True

RUN mkdir /code
ADD requirements.txt /code
RUN pip install -r /code/requirements.txt
ADD . /code
WORKDIR /code/vfb_rest

#RUN echo -e "travis_fold:start:processLoad" && \
#cd "/code" && \
#echo '** Git checkout VFB_neo4j **' && \
#git clone --quiet https://github.com/VirtualFlyBrain/VFB_neo4j.git

#RUN cd "/code" && \
#echo -e "travis_fold:end:processLoad"

#RUN mkdir /code/vfb_rest/vfb_rest/vfb
#RUN mv /code/VFB_neo4j/src/* /code/vfb_rest/vfb_rest/vfb

RUN ls -l /code/vfb_curation_api
RUN cd /code && python3 setup.py develop

ENTRYPOINT bash -c "cd /code; python3 vfb_curation_api/app.py"
#&& python manage.py loaddata users
