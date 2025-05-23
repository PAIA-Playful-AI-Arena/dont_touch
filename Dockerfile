FROM paiatech/paia-game-env:20250312
ADD . /game
WORKDIR /game
RUN apt update -y && apt install -y swig && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt --no-cache-dir
CMD ["bash"]
