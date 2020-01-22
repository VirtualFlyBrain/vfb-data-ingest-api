FROM python:3.6.2

ENV KBserver=http://localhost:7474
ENV KBuser=neo4j
ENV KBpassword=password
ENV LOAD_TEST_DATA=True

RUN mkdir /code /code/vfb_curation_api/
ADD requirements.txt run.sh setup.py logging.conf /code/

RUN chmod 777 /code/run.sh
RUN pip install -r /code/requirements.txt
ADD vfb_curation_api/database /code/vfb_curation_api/database
ADD vfb_curation_api/api /code/vfb_curation_api/api
ADD vfb_curation_api/app.py vfb_curation_api/db.sqlite vfb_curation_api/settings.py /code/vfb_curation_api/
WORKDIR /code

RUN echo "Installing VFB neo4j tools" && \
cd /tmp && \
git clone --quiet https://github.com/VirtualFlyBrain/VFB_neo4j.git

RUN mkdir -p /code/vfb_curation_api/vfb && \
mv /tmp/VFB_neo4j/src/* /code/vfb_curation_api/vfb

RUN cd /code && python3 setup.py develop
RUN ls -l /code && ls -l /code/vfb_curation_api && ls -l /code/vfb_curation_api/vfb

ENTRYPOINT bash -c "cd /code; python3 vfb_curation_api/app.py"