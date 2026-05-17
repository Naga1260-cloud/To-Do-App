#!/bin/bash
set -e

# Log all output for debugging
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1

apt-get update
apt-get install -y docker.io awscli nginx
systemctl enable docker nginx
systemctl start docker nginx
usermod -aG docker ubuntu

# Wait for docker to be fully ready
sleep 5

# ECR login
aws ecr get-login-password --region ${aws_region} | \
  docker login --username AWS --password-stdin $(echo ${ecr_frontend_url} | cut -d'/' -f1)

docker pull ${ecr_frontend_url}:latest

# Bug fix 1: run on port 5000 internally (nginx proxies 80→5000)
docker run -d \
  --name todo-frontend \
  --restart unless-stopped \
  -p 5000:5000 \
  -e API_BASE_URL="http://${api_private_ip}:8000" \
  -e FLASK_SECRET_KEY="$(openssl rand -hex 32)" \
  ${ecr_frontend_url}:latest

# Wait for container to start before configuring nginx
sleep 5

# Bug fix 2: configure nginx AFTER container starts
# Bug fix 3: remove default site first, then add todo site
rm -f /etc/nginx/sites-enabled/default

cat > /etc/nginx/sites-available/todo << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass         http://127.0.0.1:5000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
        proxy_connect_timeout 10s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/todo /etc/nginx/sites-enabled/todo
nginx -t && systemctl reload nginx

echo "=== Deployment complete ==="
docker ps
