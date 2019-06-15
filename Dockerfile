FROM python:3.7
RUN mkdir /ip_pool
WORKDIR /ip_pool
ADD . /ip_pool
RUN pip install -i https://pypi.doubanio.com/simple/ -r requirements.txt
EXPOSE 80 5000

