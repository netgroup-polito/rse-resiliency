FROM ubuntu:focal as build

COPY PMUSimulator-1.3.1 PMUSimulator-1.3.1

# Set timezone
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install dependencies
RUN apt-get update && \
    apt-get install -y libgtk2.0-dev ntp

# Install PMU
RUN cd PMUSimulator-1.3.1 && make install


# Create running container
FROM ubuntu:focal

RUN useradd -m polito

COPY --from=build /usr/local/share/PMU /usr/local/share/PMU
COPY --from=build /usr/local/bin/PMU /usr/local/bin/PMU
COPY --from=build /root/iPDC /home/polito/iPDC

# Set timezone
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install running dependencies
RUN apt-get update && \
    apt-get install -y libgtk2.0-0 ntp && \
    apt-get clean

# Change iPDC folder permissions
RUN chown -R polito /home/polito/iPDC

USER polito
ENTRYPOINT ["PMU"]
