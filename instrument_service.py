import argparse

def setup_parser(parser):
    parser.add_argument('--foo', help='foo help')
    instrument_cmd_parsers = parser.add_subparsers(dest="instrument_cmd")
    channels_parser = instrument_cmd_parsers.add_parser("channels")


def instrument_main(udid, opts):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    setup_parser(parser)
    opt = parser.parse_args()
    print(opt)