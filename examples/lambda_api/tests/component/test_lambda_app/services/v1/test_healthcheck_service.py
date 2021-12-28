import unittest

from lambda_app.config import get_config
from lambda_app.logging import get_logger
from lambda_app.repositories.mysql.product_repository import ProductRepository
from lambda_app.services.v1.healthcheck import HealthStatus, HealthCheckResult
from lambda_app.services.v1.healthcheck.resources import MysqlConnectionHealthCheck, RedisConnectionHealthCheck, \
    SQSConnectionHealthCheck, SelfConnectionHealthCheck
from lambda_app.services.v1.healthcheck_service import HealthCheckService
from tests import ROOT_DIR
from tests.component.componenttestutils import BaseComponentTestCase
from tests.component.helpers.database.mysql_helper import MySQLHelper
from tests.component.helpers.events.aws.sqs_helper import SQSHelper
from tests.unit.helpers.aws.sqs_helper import get_sqs_event_sample
from tests.unit.testutils import get_function_name


class HealthCheckServiceTestCase(BaseComponentTestCase):
    EXECUTE_FIXTURE = True
    CONFIG = None

    @classmethod
    def setUpClass(cls):
        BaseComponentTestCase.setUpClass()
        cls.CONFIG = get_config()
        cls.CONFIG.SQS_ENDPOINT = cls.SQS_LOCALSTACK

        # fixture
        if cls.EXECUTE_FIXTURE:
            logger = get_logger()

            logger.info("Fixture: MYSQL Database connection")
            logger.info("Fixture: drop table")

            mysql_connection = MySQLHelper.get_connection()
            table_name = ProductRepository.BASE_TABLE
            cls.fixture_table(logger, mysql_connection, table_name)

            logger.info('Fixture: create sqs queue')

            queue_url = cls.CONFIG.APP_QUEUE
            cls.fixture_sqs(logger, queue_url)

    @classmethod
    def fixture_sqs(cls, logger, queue_url):
        queue_name = SQSHelper.get_queue_name(queue_url)
        deleted = SQSHelper.delete_queue(queue_url)
        if deleted:
            logger.info(f'Deleting queue name: {queue_name}')

        attributes = {'DelaySeconds': '1'}
        result = SQSHelper.create_queue(queue_url, attributes)
        if result is not None:
            logger.info(f'queue {queue_name} created')
        else:
            logger.error(f'queue {queue_name} not created')

        event = get_sqs_event_sample()
        message = event['Records'][0]
        SQSHelper.create_message(message, queue_url)
        logger.info('created message: {}'.format(message))

    @classmethod
    def fixture_table(cls, logger, mysql_connection, table_name):
        dropped = MySQLHelper.drop_table(mysql_connection, table_name)
        if dropped:
            logger.info(f"Table dropped:: {table_name}")
        file_name = ROOT_DIR + f"tests/datasets/database/structure/mysql/create.table.store.{table_name}.sql"
        created = MySQLHelper.create_table(mysql_connection, table_name, file_name)
        if created:
            logger.info(f"Table created:: {table_name}")
        file_name = ROOT_DIR + f"tests/datasets/database/seeders/mysql/seeder.table.store.{table_name}.sql"
        populated = MySQLHelper.sow_table(mysql_connection, table_name, file_name)
        if populated:
            logger.info(f"Table populated:: {table_name}")

    def setUp(self):
        super().setUp()
        self.config = get_config()
        self.service = HealthCheckService(self.logger, self.config)

    def test_add_check(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("MysqlConnection", MysqlConnectionHealthCheck(self.logger, self.config), ["db"])

        # self.assertEqual(len(self.service.entries), 1)

        result = self.service.get_result()
        print(result)

        # self.assertEqual(result["status"], HealthStatus.HEALTHY)
        self.assertIsInstance(result, dict)
        self.assertTrue('status' in result)

    def test_add_lambda_check(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("Lambda test", lambda: HealthCheckResult.healthy("test success"), ["lambda_test"])

        result = self.service.get_result()
        print(result)

        # self.assertEqual(result["status"], HealthStatus.HEALTHY)
        self.assertIsInstance(result, dict)
        self.assertTrue('status' in result)

    def test_add_multi_checks(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("self", SelfConnectionHealthCheck(self.logger, self.config), [])
        self.service.add_check("mysql", MysqlConnectionHealthCheck(self.logger, self.config), ["db"])
        self.service.add_check("redis", RedisConnectionHealthCheck(self.logger, self.config), ["redis"])
        # self.service.add_check("SQSConnection", SQSConnectionHealthCheck(self.logger, self.config), ["db"])

        #self.assertEqual(len(self.service.entries), 3)

        result = self.service.get_result()
        print(result)

        # self.assertEqual(result["status"], HealthStatus.HEALTHY)
        self.assertIsInstance(result, dict)
        self.assertTrue('status' in result)

    def test_get_response(self):
        self.logger.info('Running test: %s', get_function_name(__name__))
        self.service.add_check("self", SelfConnectionHealthCheck(self.logger, self.config), [])
        self.service.add_check("mysql", MysqlConnectionHealthCheck(self.logger, self.config), ["db"])
        self.service.add_check("redis", RedisConnectionHealthCheck(self.logger, self.config), ["redis"])

        response = self.service.get_response()
        print(response.data)
        self.assertIsNotNone(response.data)


if __name__ == '__main__':
    unittest.main()
