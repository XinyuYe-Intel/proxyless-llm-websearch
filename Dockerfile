FROM python:3.11-slim

RUN apt-get update -y && apt-get install -y --no-install-recommends --fix-missing \
    vim

COPY ./ /home/proxyless-llm-websearch

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /home/proxyless-llm-websearch/requirements.txt && \
    pip install crawl4ai

RUN python -m playwright install --with-deps

ENV PYTHONPATH=$PYTHONPATH:/home/proxyless-llm-websearch

WORKDIR /home/proxyless-llm-websearch

ENTRYPOINT ["bash", "launch.sh"]