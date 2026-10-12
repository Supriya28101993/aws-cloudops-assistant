# Runbook: S3 Cost Optimization and Security

Owner: Cloud Operations Team.

## 1. S3 bill increased
1. Open AWS Cost Explorer, filter by service Amazon S3 and group by usage type.
2. Storage usage growth means more data is stored. Request usage growth means an application is calling S3 too often. Data transfer growth means data is being downloaded to the internet or across Regions.
3. Use S3 Storage Lens to find which bucket and prefix grew.
4. Check if versioning is enabled without a lifecycle rule, because old object versions are billed as storage.
5. Check for incomplete multipart uploads, which are hidden but still billed.

## 2. Reducing S3 cost
1. Add lifecycle rules to move objects to S3 Standard-IA after 30 days and to S3 Glacier Flexible Retrieval after 90 days.
2. Expire log files after 365 days unless compliance requires longer retention.
3. Delete noncurrent object versions after 30 days and abort incomplete multipart uploads after 7 days.
4. Use S3 Intelligent-Tiering when the access pattern is unknown.
5. Use a VPC gateway endpoint for S3 so traffic from EC2 does not go through a NAT gateway, which charges per GB.

## 3. Securing an S3 bucket
1. Keep S3 Block Public Access enabled at the account and bucket level.
2. Enable default encryption with SSE-S3 or SSE-KMS.
3. Enable versioning on all production buckets.
4. Add a bucket policy that denies requests not using HTTPS with the aws:SecureTransport condition.
5. Enable server access logging or CloudTrail data events for sensitive buckets.

## 4. Recovering deleted S3 objects
1. If versioning is enabled, a delete only adds a delete marker. Delete the delete marker to restore the object.
2. If versioning was not enabled, restore the object from AWS Backup or the replicated bucket.
3. Without versioning or backups, deleted objects cannot be recovered.
4. Use CloudTrail data events to find who deleted the objects.
