# Stage 1: Build the React application
FROM node:20-alpine AS build

WORKDIR /app

# Accept build arguments for service URLs
ARG VITE_AUTH_API_URL
ARG VITE_CAMERA_API_URL
ARG VITE_ANALYSIS_API_URL
ARG VITE_DVR_API_URL

# Make them available during the build
ENV VITE_AUTH_API_URL=$VITE_AUTH_API_URL
ENV VITE_CAMERA_API_URL=$VITE_CAMERA_API_URL
ENV VITE_ANALYSIS_API_URL=$VITE_ANALYSIS_API_URL
ENV VITE_DVR_API_URL=$VITE_DVR_API_URL

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy a custom nginx configuration to handle routing if needed
# For Vite/React Router, we need to redirect all requests to index.html
RUN echo 'server { \
    listen 80; \
    location / { \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    try_files $uri $uri/ /index.html; \
    } \
    }' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
