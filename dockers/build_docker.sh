IMAGE_NAME="byucs235staff/cs235-hw-1a"
IMAGE_TAG="winter2025"

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t ${IMAGE_NAME}:${IMAGE_TAG} \
    --push \
    -f - . <<EOF

FROM byucs235staff/cs235-autograder-base:latest

COPY solution/test_files /autograder/src/test_files/
COPY solution/run_tests.py /autograder/src/

EOF

 docker pull ${IMAGE_NAME}:${IMAGE_TAG}
