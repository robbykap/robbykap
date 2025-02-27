set -e  # Return non-zero exit code if any command fails

# Build the CS 110 HW1b Autograder Docker

IMAGE_NAME="byucscourseops/test-assignment-2"
IMAGE_TAG="winter2025-newbit"

docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t ${IMAGE_NAME}:${IMAGE_TAG} \
    --push \
    -f - . <<EOF

FROM byucscourseops/cs110-autograder-bit-base:winter2025-newbit

ADD solutions/worlds /autograder/src/worlds

ADD activities.json /autograder/activities.json

EOF

docker pull ${IMAGE_NAME}:${IMAGE_TAG}