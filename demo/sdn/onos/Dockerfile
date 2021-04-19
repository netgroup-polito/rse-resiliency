FROM onosproject/onos

# Ports
# 6653 - OpenFlow
# 6640 - OVSDB
# 8181 - GUI
# 8101 - ONOS CLI
# 9876 - ONOS intra-cluster communication
EXPOSE 6653 6640 8181 8101 9876
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git
RUN git clone https://gerrit.onosproject.org/onos
RUN cd onos 
RUN /bin/bash -c "source onos/tools/dev/bash_profile" 


RUN apt-get update && \
    apt-get install maven -y

COPY foo-app /foo-app
RUN cd /foo-app && \
    mvn clean install 
#RUN /bin/bash -c "onos-app localhost install! target/foo-app-1.0-SNAPSHOT.oar"
#RUN cd /bin && \
#    ./onos-app -u onos -p rocks localhost install! /foo-app/target/foo-app-1.0-SNAPSHOT.oar
# Run ONOS
ENTRYPOINT ["./bin/onos-service"]
CMD ["server"]
#CLI:ssh -p 8101 -o StrictHostKeyChecking=no onos@localhost

