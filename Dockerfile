# Base image: ubuntu:22.04
FROM ubuntu:22.04

# ARGs
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive


# neo4j 5.5.0 installation and some cleanup
RUN apt-get update && \
    apt-get install -y wget gnupg software-properties-common unzip git && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y nano unzip neo4j python3-pip && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*



# TODO: Complete the Dockerfile
RUN neo4j-admin dbms set-initial-password "project1phase1"

RUN echo "server.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf && \
    echo "server.bolt.listen_address=:7687" >> /etc/neo4j/neo4j.conf && \
    echo "server.http.listen_address=:7474" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.procedures.unrestricted=gds.*" >> /etc/neo4j/neo4j.conf

# RUN wget https://github.com/neo4j/apoc/releases/download/5.5.0/apoc-5.5.0-extended.jar &&\
# mv apoc-5.5.0-extended.jar /var/lib/neo4j/plugins/

ARG GITHUB_TOKEN

RUN git clone https://$GITHUB_TOKEN@github.com/SP-2025-CSE511-Data-Processing-at-Scale/Project-1-amohan78.git /cse511

WORKDIR /cse511

RUN wget -O yellow_tripdata_2022-03.parquet https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet

RUN pip3 install --upgrade pip && pip3 install neo4j pandas pyarrow

RUN wget -O /tmp/gds.zip https://graphdatascience.ninja/neo4j-graph-data-science-2.15.0.zip && \
    unzip /tmp/gds.zip -d /tmp/gds && \
    cp /tmp/gds/*.jar /var/lib/neo4j/plugins/ && \
    rm -rf /tmp/gds*



# Run the data loader script
RUN chmod +x /cse511/data_loader.py && \
    neo4j start && \
    python3 data_loader.py && \
    neo4j stop

# Expose neo4j ports
EXPOSE 7474 7687

# Start neo4j service and show the logs on container run
CMD ["/bin/bash", "-c", "neo4j start && tail -f /dev/null"]
