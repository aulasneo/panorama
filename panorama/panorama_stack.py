from aws_cdk import core
from aws_cdk import aws_s3 as s3


class PanoramaStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # TODO: Create S3 2 buckets:
        # RemovalPolicy should be left to the default RETAIN in production to
        # avoid any data loss. S3 buckets should be manually deleted.

        data_bucket = s3.Bucket(
            self, "-data-", removal_policy=core.RemovalPolicy.DESTROY
        )

        processed_logs_bucket = s3.Bucket(
            self, "-processed-logs-", removal_policy=core.RemovalPolicy.DESTROY
        )

        #

        # TODO: Create the lambda function to process logs

        # TODO: Create the datalake DB in lake formation
        db_name = id + "-db"
        # Check Upgrading AWS Glue Data Permissions to the AWS Lake Formation Model: https://docs.aws.amazon.com/lake-formation/latest/dg/upgrade-glue-lake-formation.html

        # TODO: Create Glue crawlers
        # One crawler for mysql data:
        # Source type: Data stores
        # Data store: s3
        # Crawl data in specified paths
        # Path: s3://data_bucket_name/<table name>
        # Add as many paths as tables
        # IAM role: LakeFormationWorkflowRole
        # Run only once to create the tables
        # Database: db_name
        # Advanced settings:
        # Grouping behavior for S3 data (optional):
        # Create a single schema for each S3 path
        # When the crawler detects schema changes in the data store, how should AWS Glue handle table updates in the data catalog?
        # Ignore the change and don't update the table in the data catalog
        # Update all new and existing partitions with metadata from the table
        # How should AWS Glue handle deleted objects in the data store?
        # Mark the table as deprecated in the data catalog

        # TODO: Crate Glue jobs

        # TODO: Create Athena link to datalake

        # TODO: Create Quicksight basic reports

        core.CfnOutput(self, "{}-unique-id".format(id), value=self.node.unique_id)
