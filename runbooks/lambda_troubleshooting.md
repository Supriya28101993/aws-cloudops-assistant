# Runbook: Lambda Troubleshooting

Owner: Cloud Operations Team.

## 1. Lambda function timing out
1. The default Lambda timeout is 3 seconds and the maximum timeout is 15 minutes.
2. Increase the timeout in Configuration, General configuration, based on the longest expected run time.
3. Increase memory, because Lambda gives more CPU when you add memory, so the function often runs faster.
4. Check the Duration metric in CloudWatch to choose the right timeout.
5. For work longer than 15 minutes, use AWS Step Functions, AWS Batch or ECS Fargate.

## 2. Lambda function errors
1. Every Lambda function writes logs automatically to CloudWatch Logs in the log group /aws/lambda/function-name.
2. Open the latest log stream and search for ERROR, Exception or Traceback.
3. AccessDeniedException means the execution role is missing a permission.
4. Configure a dead-letter queue or an on-failure destination so failed asynchronous events are not lost.
5. Create a CloudWatch alarm on the Errors metric that notifies the team through SNS.

## 3. Lambda cannot reach a database or the internet
1. To reach a database in a VPC, the Lambda function must be attached to the VPC subnets and a security group.
2. The database security group must allow inbound traffic from the Lambda security group on the database port.
3. A Lambda function in a VPC needs a NAT gateway to reach the internet.
4. The execution role needs permissions to create network interfaces, which AWSLambdaVPCAccessExecutionRole provides.

## 4. Throttling
1. A Throttles metric above zero means the function hit its concurrency limit.
2. The default account concurrency limit is 1000 per Region and can be increased through Service Quotas.
3. Use reserved concurrency to guarantee capacity for critical functions.
