import logging
import argparse

from include.pmu_adapter_lib import PmuAdapter


def __parse_arguments():
    argp = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    argp.add_argument('-c', '--client-pmu', action='store', metavar='127.0.0.1', type=str,
                      help="Client PMU address [DEFAULT=127.0.0.1]", default='127.0.0.1')
    argp.add_argument('-b', '--mqtt-broker', action='store', metavar='127.0.0.1', type=str,
                      help="MQTT broker address [DEFAULT=127.0.0.1]", default='127.0.0.1')
    argp.add_argument('-p', '--client-pmu-port', action='store', metavar='4712', type=int,
                      help="Client PMU port [DEFAULT=4712]", default=4712)
    argp.add_argument('-P', '--mqtt-broker-port', action='store', metavar='1883', type=int,
                      help="MQTT broker port [DEFAULT=1883]", default=1883)
    argp.add_argument('-i', '--pdc-id', action='store', metavar='1', type=int,
                      help="Virtual PDC id [DEFAULT=1]", default=1)
    argp.add_argument('-q', '--qos', action='store', metavar='1', type=int,
                      help="MQTT message QoS [DEFAULT=1]", default=1)
    argp.add_argument('-v', '--verbosity', action='store', metavar='1', type=int, choices=[0, 1, 2, 3],
                      help="Verbosity level, possible values are DEBUG=0, INFO=1, WARNING=2, ERROR=3 [DEFAULT=1]",
                      default=1)
    # Perform parsing
    return argp.parse_args()


def get_verbosity(level):
    if level == 0:
        return logging.DEBUG
    elif level == 1:
        return logging.INFO
    elif level == 2:
        return logging.WARNING
    else:
        return logging.ERROR


if __name__ == "__main__":
    args = __parse_arguments()

    adapter = PmuAdapter(args.pdc_id, args.client_pmu, args.client_pmu_port, args.mqtt_broker,
                         args.mqtt_broker_port, args.qos, get_verbosity(args.verbosity))
    adapter.connect()
    adapter.start()
