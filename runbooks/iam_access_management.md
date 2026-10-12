# Runbook: IAM Access Management

Owner: Cloud Security Team. Our policy is least privilege for every user, group and role.

## 1. Onboarding a new team member
1. Create access through IAM Identity Center, not as an IAM user with long-term access keys.
2. Add the person to the correct group, for example Developers, ReadOnly or CloudAdmins.
3. Permissions are always given to groups or permission sets, never directly to a single user.
4. Multi-factor authentication (MFA) is mandatory for every person who signs in to the console.

## 2. Offboarding a team member
1. Disable the user in IAM Identity Center on the person's last working day.
2. Deactivate and delete any IAM access keys the person created.
3. Review CloudTrail for activity by the user during the last 30 days.

## 3. Rotating IAM access keys
1. Access keys must be rotated at least every 90 days.
2. Create a second access key for the user so the application keeps working during rotation.
3. Update the application or secret in AWS Secrets Manager to use the new key.
4. Check the last used date of the old key in the IAM console to confirm it is no longer used.
5. Deactivate the old key first, wait 24 hours, then delete it.

## 4. Leaked access key incident
1. Immediately deactivate and delete the leaked access key in IAM.
2. Search CloudTrail for every API call made with that access key ID.
3. Look for new IAM users, new access keys, new EC2 instances and changes to S3 bucket policies, and remove anything the attacker created.
4. Check AWS Cost Explorer for unexpected charges and open a case with AWS Support if resources were abused.
5. Remove the key from the git history, not only from the latest commit.

## 5. User gets Access Denied
1. Check that the user's IAM policy allows the exact action and resource ARN.
2. Check for an explicit Deny, because an explicit Deny always wins over an Allow.
3. Check resource-based policies such as S3 bucket policies and KMS key policies.
4. Check Service Control Policies (SCPs) and permission boundaries, which limit the maximum permissions.
5. Use the IAM Policy Simulator and the CloudTrail event error message to find the missing permission.

## 6. Applications accessing AWS services
1. Applications on EC2 must use an IAM role attached through an instance profile.
2. Lambda functions use an execution role with only the permissions they need.
3. Never store access keys in code, configuration files or on EC2 instances.
