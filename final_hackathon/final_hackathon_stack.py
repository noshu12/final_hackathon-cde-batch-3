from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_msk as msk,
    CfnOutput,
    RemovalPolicy
)
from constructs import Construct

class FinalHackathonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. VPC Creation (Update to avoid deprecation warning)
        vpc = ec2.Vpc(
            self, "HackathonVPC",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16")
        )

        # 2. PostgreSQL RDS Database Security Group & Instance
        postgres_sg = ec2.SecurityGroup(
            self, "PostgresSG",
            vpc=vpc,
            description="Allow inbound access to Postgres",
            allow_all_outbound=True
        )
        postgres_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(5432),
            "Allow Postgres access from anywhere"
        )

        database = rds.DatabaseInstance(
            self, "PostgresDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[postgres_sg],
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MEDIUM),
            database_name="hackathon_onprem",
            credentials=rds.Credentials.from_generated_secret("postgres"), # Yahan change kiya hai
            removal_policy=RemovalPolicy.DESTROY,
            deletion_protection=False
        )

        # 3. MSK Cluster (Kafka)
        msk_sg = ec2.SecurityGroup(
            self, "MSKSG",
            vpc=vpc,
            description="Security group for MSK Cluster",
            allow_all_outbound=True
        )
        msk_sg.add_ingress_rule(msk_sg, ec2.Port.all_traffic(), "Self-referencing rule for MSK")

        cluster = msk.CfnCluster(
            self, "KafkaCluster",
            cluster_name="hackathon-msk-cluster",
            kafka_version="3.7.x",
            number_of_broker_nodes=2,
            broker_node_group_info=msk.CfnCluster.BrokerNodeGroupInfoProperty(
                instance_type="kafka.m5.large",
                client_subnets=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS).subnet_ids,
                security_groups=[msk_sg.security_group_id],
                storage_info=msk.CfnCluster.StorageInfoProperty(
                    ebs_storage_info=msk.CfnCluster.EBSStorageInfoProperty(volume_size=1000)
                )
            )
        )

        # Outputs
        CfnOutput(self, "DBEndpoint", value=database.db_instance_endpoint_address)
        CfnOutput(self, "DBName", value="hackathon_onprem")
        CfnOutput(self, "KafkaClusterArn", value=cluster.ref)