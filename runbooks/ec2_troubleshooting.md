# Runbook: EC2 Troubleshooting

Owner: Cloud Operations Team. Applies to all production and non-production EC2 instances.

## 1. Cannot SSH into an EC2 instance
1. Check that the security group allows inbound TCP port 22 from your IP address only, never from 0.0.0.0/0.
2. Check that the subnet network ACL allows inbound port 22 and outbound ephemeral ports 1024-65535.
3. Check that the instance has a public IP and the subnet route table has a route 0.0.0.0/0 to an Internet Gateway.
4. Use the correct key pair and username: ec2-user for Amazon Linux, ubuntu for Ubuntu. The key file must have permission chmod 400.
5. If SSH still fails, connect with AWS Systems Manager Session Manager, which needs no open port and no key pair.

## 2. Website on EC2 is not loading
1. Check that the security group allows inbound HTTP port 80 and HTTPS port 443.
2. Check that the web server is running with the command systemctl status httpd or systemctl status nginx.
3. A connection timeout usually means a network problem such as a security group, NACL or route table.
4. A connection refused error usually means the application or web server is not running.

## 3. EC2 status check failed
1. A failed system status check means an AWS hardware or host problem. Stop and start the instance to move it to a new host.
2. A failed instance status check means a problem inside the operating system, such as a full disk, wrong network configuration or kernel error.
3. Use Get System Log or the EC2 Serial Console to see boot errors.
4. Create a CloudWatch alarm with the EC2 recover action so instances recover automatically from system check failures.

## 4. High CPU utilization
1. Check the CPUUtilization metric in CloudWatch to see when the spike started.
2. Connect to the instance and run top to find the process using the CPU.
3. For burstable t2, t3 and t4g instances, check the CPUCreditBalance metric. If credits are zero the instance is throttled.
4. Fix by stopping the bad process, moving to a larger instance type, or adding the instance to an Auto Scaling group.

## 5. Disk is full
1. Run df -h to confirm which filesystem is full and du -sh /var/log/* to find large folders.
2. Delete or compress old log files and configure logrotate so logs do not fill the disk again.
3. To add space, modify the EBS volume size in the console, then extend the partition with growpart and the filesystem with resize2fs or xfs_growfs.
4. Disk and memory usage are not available in CloudWatch by default. Install the CloudWatch Agent to collect disk_used_percent and mem_used_percent.
5. Create a CloudWatch alarm at 80 percent disk usage that notifies the on-call team through SNS.
