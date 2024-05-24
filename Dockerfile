FROM paiatech/mlgame:10.4.5.3-slim
ADD . /game
WORKDIR /game
RUN apt update -y && apt install -y swig && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt --no-cache-dir
CMD ["bash"]
