#!/bin/bash
set -e

# Log all output for debugging
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

# Install Docker
apt-get update
apt-get install -y docker.io awscli
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

# Wait for docker to be fully ready
sleep 5

# Login to ECR and pull latest image
aws ecr get-login-password --region ${aws_region} | \
  docker login --username AWS --password-stdin $(echo ${ecr_api_url} | cut -d'/' -f1)

docker pull ${ecr_api_url}:latest

# Run API container
docker run -d \
  --name todo-api \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="${database_url}" \
  ${ecr_api_url}:latest

echo "=== API Deployment complete ==="
docker ps
