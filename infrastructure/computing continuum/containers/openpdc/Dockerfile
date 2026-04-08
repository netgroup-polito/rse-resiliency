FROM mono:6.12.0 as builder

COPY ./packages.config ./openPDC/packages.config

COPY ./install-openPDC.sh ./openPDC/install-openPDC.sh

RUN apt update && apt install wget unzip nuget -y --no-install-recommends

RUN cd ./openPDC && chmod +x ./install-openPDC.sh && ./install-openPDC.sh

FROM ubuntu:focal

RUN useradd -m polito

COPY --from=builder --chown=polito /opt/openPDC /opt/openPDC

# Set timezone
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install running dependencies
RUN apt-get update && \
    apt-get install -y mono-complete unzip zstd screen wget iproute2 && \
    apt-get clean   

RUN wget https://dev.mysql.com/get/Downloads/Connector-Net/mysql-connector-net-8.0.25-noinstall.zip && \
    unzip mysql-connector-net-8.0.25-noinstall.zip -d connector && \
    cd connector/v4.8 && \
    # fix delayed signature of a package
    sn -k keyPair.snk && \
    ikdasm System.Runtime.CompilerServices.Unsafe.dll -out && \
    ilasm out /dll /key=keyPair.snk /output:System.Runtime.CompilerServices.Unsafe.dll && \
    rm libzstd.dll out keyPair.snk && \
    cp ./* /opt/openPDC/ && \
    ln -s /lib/$(uname -i)-linux-gnu/libz.so.1 /opt/openPDC/libz.so && \
    cd / && rm -rf mysql-connector-net-8.0.25-noinstall.zip connector

COPY init.sh init.sh

COPY liveness.sh liveness.sh

RUN chmod +x init.sh && chmod +x liveness.sh

COPY openPDC.exe.config.template openPDC.exe.config.template

USER polito

CMD ["./init.sh"]
