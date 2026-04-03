---
layout: default
title: "Juice Shop"
parent: "Reference"
nav_order: 6
---

```
# Update package lists
sudo apt update

# Install Docker if not already installed
sudo apt install -y docker.io

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Clone the repository
git clone https://github.com/juice-shop/juice-shop.git
cd juice-shop

# Build the Docker image locally
docker build -t juice-shop .

# Run the locally built container
docker run --rm -p 3000:3000 juice-shop
```

