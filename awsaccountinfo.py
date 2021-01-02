import boto3


# list all active regions
def get_regions_list():
    # authentication happening using default aws-examples profile(CLI)
    ec2_client = boto3.client('ec2')

    region_response = ec2_client.describe_regions()
    region_list = []
    # fetch all aws-examples regions
    for region in region_response["Regions"]:
        region_name = region["RegionName"]
        region_list.append(region_name)

    return region_list


# list all non-default VPCs
def get_non_default_vpc_details():
    # Get VPC details by region
    # iterate region list and create region specific client
    region_vpc_id_dict = {}
    region_count = 0
    for region in active_region_list:
        ec2_region_client = boto3.client('ec2', region_name=region)
        vpc_response = ec2_region_client.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['false']}])
        try:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
        except IndexError:
            continue
        region_count = region_count + 1
        print(str(region_count) + " " + region + " " + vpc_id)
        region_vpc_id_dict[region] = vpc_id

    return region_vpc_id_dict


# list all default VPCs
def get_default_vpc_details():
    # Get VPC details by region
    # iterate region list and create region specific client
    region_vpc_id_dict = {}
    region_count = 0
    for region in active_region_list:
        ec2_region_client = boto3.client('ec2', region_name=region)
        vpc_response = ec2_region_client.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        try:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
        except IndexError:
            continue
        region_count = region_count + 1
        print(str(region_count) + " " + region + " " + vpc_id)
        region_vpc_id_dict[region] = vpc_id

    return region_vpc_id_dict


def get_account_id():
    sts_client = boto3.client("sts")
    return sts_client.get_caller_identity()["Account"]


if __name__ == '__main__':
    account_id = get_account_id()
    print()
    print("AWS account id is : " + account_id)
    print()

    # List all active regions
    active_region_list = get_regions_list()
    print("Listing all " + str(active_region_list.__len__()) + " regions: " + str(active_region_list))
    print()

    # List all default VPC in the account
    default_vpc_details = get_default_vpc_details()
    print("default vpc IDs: " + str(default_vpc_details))
    print()

    # Test if non-default vpc exists in the account .
    non_default_vpc_details = get_non_default_vpc_details()
    print("non-default vpc IDs: " + str(non_default_vpc_details))
    print()
