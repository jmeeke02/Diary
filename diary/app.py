import boto3  # pylint: disable=import-error
import logging
import sys

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Diary(object):
    """Diary Secrets Manager"""
    name = None
    value = None
    string_type = None
    description = None
    key_id = None
    overwrite = False
    pattern = None
    session = boto3


    def __init__(self, **kwargs):
        # Get all required paramters in args tuple
        args = (kwargs['name'], kwargs['value'], kwargs['string_type'])
        if not all(args):
            raise RuntimeError("Missing args %r" % (args,))

        for key, value in kwargs.items():
            if hasattr(self, key) and value:
                logger.info("%s == %s", key, value)
                setattr(self, key, value)

    def get_secret(self):
        """Check if this secret already exists"""
        client = self.session.client('ssm')

        try:
            client.get_parameter(
                Name=self.name,
                WithDecryption=False
            )
        except ClientError as error:
            if error.response['Error']['Code'] == 'ParameterNotFound':
                return
            else:
                raise

        raise UserWarning('The parameter already exists. To overwrite this '
                          'value, set the --overwrite flag.')


    def put_secret(self):
        """Put a secret into SSM"""
        client = self.session.client('ssm')

        name = self.name
        string_type = self.string_type
        key_id = self.key_id
        value = self.value

        if self.description is None:
            self.description = 'Secret for AWS'

        params = dict(Name=name,
                      Value=value,
                      Type=string_type,
                      Description=self.description,
                      Overwrite=self.overwrite)
        if key_id is not None:
            params['KeyId'] = key_id

        try:
            response = client.put_parameter(**params)
        except:
            logger.error('Cannot put secret=%s using type=%s and key=%s',
                         name, string_type, key_id)
            raise

        return response

    def check_size(self):
        # NOTE: there is a 4KB limit (~4096 bytes) on ssm values
        # assuming UTF-8, each char will need 1-4 bytes, so we can
        # store between 4096 - 1024 characters depending on bytes used
        size = sys.getsizeof(self.value)

        if size > 4096:
            logger.error('SSM only supports parameters up to 4KB.')
            raise RuntimeError(
                ('SSM only supports parameters up to 4KB. Value of %s '
                 'is %s bytes.') % (self.name, size)
            )


    def assume_role(self, role_arn, name):
        """Assume a role for Diary"""
        client = self.session.client('sts')

        session_name = 'DiarySession_%s' % name
        duration = 900 # minimum 900, maximum 3600

        try:
            role = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=duration
            )

        except:
            logger.error(
                'Unable to assume role role_arn=%s session_name=%s '
                'duration=%s',
                role_arn, session_name, duration
            )
            raise

        session = boto3.Session(
            aws_access_key_id=role['Credentials']['AccessKeyId'],
            aws_secret_access_key=role['Credentials']['SecretAccessKey'],
            aws_session_token=role['Credentials']['SessionToken']
        )

        logging.info('Successfully Assumed Role: %s Expires: %s',
                     role['AssumedRoleUser']['AssumedRoleId'],
                     role['Credentials']['Expiration'])

        self.session = session
