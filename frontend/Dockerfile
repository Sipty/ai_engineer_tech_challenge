# Use an official Node runtime as the base image
FROM node:14

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the app
RUN npm run build

# Use a lightweight Node image to serve the app
FROM node:14-alpine

# Set the working directory
WORKDIR /app

# Copy the build output from the previous stage
COPY --from=0 /app/build ./build

# Install a simple http server to serve the static content
RUN npm install -g serve

# Expose the port the app runs on
EXPOSE 3000

# Serve the app
CMD ["serve", "-s", "build", "-l", "3000"]