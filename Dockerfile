FROM python:3.6.2

ENV KBserver=http://localhost:7474
ENV KBuser=neo4j
ENV KBpassword=password
ENV LOAD_TEST_DATA=True

RUN mkdir /code
ADD requirements.txt /code
ADD run.sh /code
ADD logging.conf /code
RUN chmod 777 /code/run.sh
RUN pip install -r /code/requirements.txt
ADD vfb_curation_api/ /code/vfb_curation_api
ADD setup.py /code
WORKDIR /code

RUN echo "Installing VFB neo4j tools" && \
cd /tmp && \
git clone --quiet https://github.com/VirtualFlyBrain/VFB_neo4j.git

RUN mkdir /code/vfb

RUN mv /tmp/VFB_neo4j/src/* /code/vfb

RUN ls -l /code && echo "Hello3"
RUN cd /code && python3 setup.py develop

ENTRYPOINT bash -c "cd /code; python3 vfb_curation_api/app.py"