from aws_cdk import core


class PanoramaStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        account_id = "function to get the account id"
        data_bucket_name = "Panorama-" + account_id + "-data"
        processed_logs_bucket_name = data_bucket_name + "-processed_logs"

        # TODO: Create S3 2 buckets:
        # data_bucket_name
        # processed_logs_bucket_name

        # TODO: Create the lambda function to process logs

        # TODO: Create the datalake DB in lake formation
        db_name = "Panorama-" + account_id + "-db"
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
