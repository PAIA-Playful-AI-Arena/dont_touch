export tag=latest
export game="dont_touch"

docker build \
-t ${game}:${tag} \
-f ./Dockerfile .
