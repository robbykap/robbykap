IMAGE_NAME="byucscourseops/cs235-hw-1a"
IMAGE_TAG="winter2025-test-image-2"

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t ${IMAGE_NAME}:${IMAGE_TAG} \
    --push \
    -f - . <<EOF

FROM byucscourseops/cs235-autograder-base:latest

COPY solution/test_files /autograder/src/test_files/
COPY solution/run_tests.py /autograder/src/

EOF

# docker pull ${IMAGE_NAME}:${IMAGE_TAG}
