"""
Grafana:
https://g-69fc276d1e.grafana-workspace.us-east-1.amazonaws.com/
"""

import boto3
from botocore.config import Config
import datetime
import random
import time

import keys.apikeys


class Writer:
    def __init__(self):
        self.session = boto3.Session()
        config = Config(read_timeout=20, max_pool_connections=5000,
                        retries={'max_attempts': 10})
        self.client = self.session.client("timestream-write", config=config)
        self.dbName = "desert_habitat"
        self.tableName = "habitat_iot"

        self.setupDatabase()

    def setupDatabase(self):
        # -------------------------------------------------------
        # Create DB if needed:
        try:
            self.client.create_database(DatabaseName=self.dbName)
            print("Database desert_habitat created.")
        except self.client.exceptions.ConflictException:
            print("Database desert_habitat exists...")
        except Exception as e:
            print("Create database failed:", e)

        # Describe DB (whatever)
        try:
            result = self.client.describe_database(DatabaseName=self.dbName)
            print("Database desert_habitat has id {}".format(result["Database"]["Arn"]))
        except self.client.exceptions.ResourceNotFoundException:
            print("Can't find database desert_habitat")
        except Exception as e:
            print("Describe database failed:", e)

        # Update DB
        print("updating DB...")
        try:
            result = self.client.update_database(DatabaseName=self.dbName, KmsKeyId=keys.apikeys.KMS_ID)
            print("Database desert_habitat updated to use KMS {}".format(result["Database"]["KmsKeyId"]))
        except self.client.exceptions.ResourceNotFoundException:
            print("Database doesn't exist?!")
        except Exception as e:
            print("Update database failed:", e)

        # List DB
        print("Listing databases")
        try:
            result = self.client.list_databases(MaxResults=5)
            for database in result['Databases']:
                print("      ->  " + database['DatabaseName'])
            next_token = result.get('NextToken', None)
            while next_token:
                result = self.client.list_databases(NextToken=next_token, MaxResults=5)
                for database in result['Databases']:
                    print("      ->  " + database['DatabaseName'])
                next_token = result.get('NextToken', None)
        except Exception as err:
                print("List databases failed:", err)

        # -------------------------------------------------------
        # Create Table
        print("Creating table")
        retention_properties = {
            "MemoryStoreRetentionPeriodInHours": 24,
            "MagneticStoreRetentionPeriodInDays": 6
        }
        try:
            self.client.create_table(DatabaseName=self.dbName, TableName=self.tableName,
                                RetentionProperties=retention_properties)
            print("Table [%s] successfully created." % self.tableName)
        except self.client.exceptions.ConflictException:
            print("Table [%s] exists on database [%s]. Skipping table creation" % (
                  self.tableName, self.dbName))
        except Exception as e:
            print("Create table failed:", e)

        # Update Table
        print("Updating table")
        retention_properties = {
            "MemoryStoreRetentionPeriodInHours": 24,
            "MagneticStoreRetentionPeriodInDays": 6
        }

        try:
            self.client.update_table(DatabaseName=self.dbName, TableName=self.tableName,
                                RetentionProperties=retention_properties)
            print("Table updated")
        except Exception as e:
            print("Update table failed:", e)

        # Describe Table (whatever)
        print("Describing table")
        try:
            result = self.client.describe_table(DatabaseName=self.dbName, TableName=self.tableName)
            print("Table habitat_iot has id {}".format(result["Table"]["Arn"]))
        except self.client.exceptions.ResourceNotFoundException:
            print("Table doesn't exist?!")
        except Exception as e:
            print("Describe Table failed:", e)

    def writeRecords(self, thermBaskingVal, thermCoolingVal, humidBaskingVal,
                     humidCoolingVal, waterLevelVal):
        # -------------------------------------------------------
        # Write Records
        print("{}: Writing Records".format(datetime.datetime.now().strftime("%Y.%m.%d - %H:%M:%S")))
        currentTime = str(int(round(time.time() * 1000)))

        dimensions = [
            {"Name": "habitat", "Value": "desert"}
        ]
        commonAttributes = {
            "Dimensions": dimensions,
            "MeasureValueType": "DOUBLE",
            "Time": currentTime
        }

        thermBasking = {
            "MeasureName": "therm_basking",
            "MeasureValue": str(thermBaskingVal),
        }

        thermCooling = {
            "MeasureName": "therm_cooling",
            "MeasureValue": str(thermCoolingVal),
        }

        humidBasking = {
            "MeasureName": "humidity_basking",
            "MeasureValue": str(humidBaskingVal),
        }

        humidCooling = {
            "MeasureName": "humidity_cooling",
            "MeasureValue": str(humidCoolingVal),
        }
        waterLevel = {
            "MeasureName": "water_level",
            "MeasureValue": str(waterLevelVal)
        }

        records = [thermBasking, thermCooling, humidBasking, humidCooling, waterLevel]

        try:
            result = self.client.write_records(DatabaseName=self.dbName, TableName=self.tableName,
                                          Records=records, CommonAttributes=commonAttributes)
            print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
        except self.client.exceptions.RejectedRecordsException as e:
            print("RejectedRecords: ", e)
            for rr in e.response["RejectedRecords"]:
                print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
                if "ExistingVersion" in rr:
                    print("Rejected record existing version: ", rr["ExistingVersion"])
        except Exception as e:
            print("Write Records failed:", e)
