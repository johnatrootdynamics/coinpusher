# Use an appropriate base imagee
FROM python:3.11.2
EXPOSE 80
ENV TZ="America/New_York"
ARG db_user=${db_user}
ARG db_passwd${db_passwd}
ENV db_user=${db_user}
ENV db_passwd=${db_passwd}
# Install Git
RUN apt update  -y
RUN apt install python3-venv -y
RUN apt install -y git
#RUN python -m pip install --upgrade pip
# Clone the repository
# Copy files from the cloned repository to the desired location in the Docker image
RUN mkdir /app
ADD https://www.google.com /time.now
RUN git clone https://github.com/johnatrootdynamics/coinpusher /app
WORKDIR /app
ENV VIRTUAL_ENV=/opt/venv

COPY * /opt/venv/
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:



# Set the working directory
RUN pip3 install -r requirements.txt



# Run the application:
CMD ["python3", "app.py"]