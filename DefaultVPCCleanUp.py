import boto3

def get_regions_list():
    # authentication happening using default aws profile(CLI)
    ec2_client = boto3.client('ec2')

    region_response = ec2_client.describe_regions()
    region_list = []
    # fetch all aws regions
    for region in region_response["Regions"]:
        region_name = region["RegionName"]
        region_list.append(region_name)

    return region_list


def get_non_default_vpc_details():
    # Get VPC details by region
    # iterate region list and create region specific client
    region_vpc_id_dict = {}
    region_count = 0
    for region in region_list:
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


def get_default_vpc_details():
    # Get VPC details by region
    # iterate region list and create region specific client
    region_vpc_id_dict = {}
    region_count = 0
    for region in region_list:
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


# I needed to delete only below dependencies from default VPC for deleting default VPC
def delete_vpc_dependencies(**region_vpc_id):
    # Get VPC details by region
    # iterate region list and create region specific client
    print("iterating the region vpc dictionary and deleting vpc dependencies")
    for region, vpc_id in region_vpc_id.items():
        print(region, vpc_id)
        ec2 = boto3.resource('ec2', region_name=region)
        vpc = ec2.Vpc(vpc_id)

        for igw in vpc.internet_gateways.all():
            print(igw)
            igw.detach_from_vpc(VpcId=vpc_id)
            igw.delete()
            print(str(igw) + " got deleted")

        for subnets in vpc.subnets.all():
            print(subnets)
            subnets.delete()
            print(str(subnets)+" got deleted")

    print("deleting vpc dependencies done!!!!")


def delete_default_vpc(**region_vpc_id):
    # Get VPC details by region
    # iterate region list and create region specific client
    print("iterating the region vpc dictionary and deleting default VPC")
    for region, vpc_id in region_vpc_id.items():
        print(region, vpc_id)
        ec2_resource = boto3.resource('ec2', region_name=region)
        vpc_resource = ec2_resource.Vpc(vpc_id)
        vpc_resource.delete()
        print("vpc got deleted")

    print("deleting default VPCs done======!!!!")


if __name__ == '__main__':
    region_list = get_regions_list()
    print("Listing all " + str(region_list.__len__()) + " regions: " + str(region_list))
    print()

    region_vpc_id_dict = get_default_vpc_details()
    print("default vpc IDs before deleting: "+str(region_vpc_id_dict))
    print()

    delete_vpc_dependencies(**region_vpc_id_dict)
    print()

    delete_default_vpc(**region_vpc_id_dict)
    print()

    # test default vpc details post deletion
    region_vpc_id_dict = get_default_vpc_details()
    print("default vpc IDs post deleting: "+str(region_vpc_id_dict))
    print()

    # test non-default vpc details post deletion - this should not get deleted, if any.
    region_vpc_id_dict = get_non_default_vpc_details()
    print("non-default vpc IDs: "+str(region_vpc_id_dict))
    print()



