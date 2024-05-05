# Use an appropriate base imagee
FROM python:3.11.2
EXPOSE 80
ENV TZ="America/New_York"
ARG DBUSER=${DBUSER}
ARG DBPASSWD=${DBPASSWD}
ARG DBHOST=${DBHOST}
ENV DBUSER=${DBUSER}
ENV DBPASSWD=${DBPASS}
ENV DBHOST=${DBHOST}
# Install Git
RUN apt install -y git
#RUN python -m pip install --upgrade pip
# Clone the repository
# Copy files from the cloned repository to the desired location in the Docker image
RUN mkdir /app
ADD https://www.google.com /time.now
RUN git clone https://github.com/johnatrootdynamics/coinpusher /app
WORKDIR /app

# Install dependencies:



# Set the working directory
RUN pip3 install -r requirements.txt



# Run the application:
CMD ["python3", "app.py"]