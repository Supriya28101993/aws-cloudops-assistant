# Policy: Resource Tagging and Cost Control

Owner: FinOps Team. Applies to all AWS accounts in the organization.

## 1. Mandatory tags
Every AWS resource must have these tags when it is created.
1. Environment: one of prod, staging or dev.
2. Owner: the email address of the responsible engineer.
3. Project: the project or application name.
4. CostCenter: the cost center code from finance.

## 2. Enforcing tags
1. Tag policies in AWS Organizations standardize tag keys and values.
2. AWS Config rule required-tags reports resources that are missing mandatory tags.
3. Untagged resources in dev accounts are stopped after 7 days if the owner does not respond.

## 3. Cost control rules
1. Every account must have an AWS Budgets alert at 80 percent and 100 percent of the monthly budget.
2. Dev and staging EC2 instances are stopped automatically at 8 PM and started at 8 AM on weekdays using the Instance Scheduler.
3. Unattached EBS volumes and unused Elastic IP addresses are reviewed and deleted every week.
4. Use AWS Compute Optimizer to right-size EC2 instances that use less than 20 percent CPU.
5. Steady production workloads should be covered by Savings Plans. Fault-tolerant batch jobs should use Spot Instances.
6. Prefer gp3 EBS volumes over gp2 and Graviton instance types such as t4g and m7g for lower cost.
