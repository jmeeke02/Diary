import argparse
import logging

from diary import loggers, app

logger = logging.getLogger(__name__)

__version__ = '0.0.1'

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Diary: A Keeper for your secrets'
    )

    parser.add_argument('-V', '--version', action='version',
                        version=__version__)

    parser.add_argument('-vv', '--verbosity', action='count',
                        help='increase output verbosity', default=0)

    parser.add_argument('-n', '--name', required=True,
                        help=('The name of the parameter you want to add. '
                              'Should correspond to the name of the parameter '
                              'thats already been created.'))

    parser.add_argument('-d', '--description', required=False,
                        help='Information about this parameter.')

    parser.add_argument('-v', '--value', required=True,
                        help='The parameter value.')

    parser.add_argument('-t', '--type', required=True,
                        help=('They type of parameter to add '
                              '{String, StringList, SecureString}.'))

    parser.add_argument('-k', '--key-id', dest='key', required=False,
                        help=('The KMS Key ID you want to use to encrypt '
                              'this parameter'))

    parser.add_argument('--overwrite', action='store_true', required=False,
                        help=('Overwrite an existing parameter. If not '
                              'specified will default to false'))

    parser.add_argument('-p', '--allowed-pattern', dest='pattern',
                        required=False,
                        help='Regex used to validate parameter value.')

    parser.add_argument('-r', '--role', required=False,
                        help=('[Optional] The arn of the role for '
                              'Diary to run under'))

    parser.set_defaults(feature=False)
    return parser.parse_args()

def configure_logging(verbosity):
    log_level = logging.WARNING - (verbosity * 10)
    if log_level < 10:
        log_level = 10

    loggers.configure(logging.getLogger(), log_level)

def main():
    args = parse_arguments()
    configure_logging(args.verbosity)
    diary_app = app.Diary(name=args.name, description=args.description,
                          value=args.value, string_type=args.type,
                          key_id=args.key, overwrite=args.overwrite,
                          pattern=args.pattern)


    # Check size of SSM parameter
    diary_app.check_size()

    if not args.overwrite:
        diary_app.get_secret()

    if args.role is not None and args.name is not None:
        diary_app.assume_role(role_arn=args.role, name=args.name)

    diary_app.put_secret()


if __name__ == '__main__':
    main()
