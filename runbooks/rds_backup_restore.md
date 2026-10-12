# Runbook: RDS Backup, Restore and High Availability

Owner: Database Operations Team.

## 1. Backup standards
1. Automated backups are enabled on all production RDS databases with a retention period of 14 days.
2. A manual snapshot is taken before every major change or database engine upgrade.
3. Production snapshots are copied to a second Region every day for disaster recovery.

## 2. Restoring an RDS database
1. Point-in-time restore can recover a database to any second within the backup retention period.
2. A restore always creates a new DB instance with a new endpoint. It does not overwrite the existing database.
3. After the restore, update the application connection string or DNS record to the new endpoint.
4. Apply the same security groups, parameter group and option group to the restored instance.

## 3. Multi-AZ and read replicas
1. All production databases must use Multi-AZ for high availability.
2. Multi-AZ keeps a synchronous standby in another Availability Zone and fails over automatically in about one to two minutes.
3. Read replicas use asynchronous replication and are used to scale read traffic, not for high availability.
4. A read replica can be promoted to a standalone database during a disaster.

## 4. Database is slow (performance problems)
1. Check CPUUtilization, FreeableMemory, DatabaseConnections and ReadIOPS in CloudWatch.
2. Use Performance Insights to find the slowest SQL queries.
3. Too many connections from Lambda functions can be solved with RDS Proxy.
4. Low free storage space can be fixed by enabling storage autoscaling.
