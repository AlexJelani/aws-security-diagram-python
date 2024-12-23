from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, VPC, InternetGateway, NATGateway
from diagrams.generic.network import Firewall
from diagrams.onprem.client import Users
from diagrams.saas.chat import Slack

with Diagram("AWS VPC Architecture", show=False, direction="LR"):
    # External Users and Services
    end_users = Users("End Users")
    developers = Users("Developers")
    data_science = Users("Data Science")
    mailgun = Slack("Mailgun")

    # Add Firewall before VPC
    firewall = Firewall("Network Firewall")

    with Cluster("AWS VPC") as vpc:
        # Add VPC resource
        vpc_resource = VPC("Main VPC")
        igw = InternetGateway("Internet Gateway")

        with Cluster("Public Subnet"):
            nat = NATGateway("NAT Gateway")

            # Security group as a cluster (since there's no direct SecurityGroup resource)
            with Cluster("Security Group: SGALB"):
                lb = ELB("External Load Balancer")

            # New Security Group for Bastion Host or VPN Clients
            with Cluster("Security Group: SGBastion"):
                bastion = Users("Bastion Host/VPN Clients")

        with Cluster("Private Subnet"):
            # Updated Kubernetes cluster's security group
            with Cluster("Security Group: SGAPP"):
                k8s = EKS("Kubernetes Cluster")

            # Updated RDS database's security group
            with Cluster("Security Group: SGDB"):
                db = RDS("RDS Database")

    # Updated connection flows including firewall and security groups
    end_users >> firewall >> igw >> lb >> k8s
    developers >> firewall >> igw >> lb >> Edge(label="port 6443") >> k8s
    data_science >> firewall >> igw >> Edge(label="Postgres port") >> db
    bastion >> Edge(label="SSH") >> igw >> k8s
    k8s >> nat >> igw >> mailgun
    k8s >> Edge(label="Postgres port") >> db

    # Updated Security Group rules
    # SGAPP: Allow incoming traffic on port 6443 from SGBastion only
    # SGAPP: Allow outgoing traffic on Postgres port to SGDB only

    # SGDB: Allow incoming traffic on Postgres port from SGAPP and Data Science IPs

    # SGBastion: Allow SSH access only from team members' IPs

    # Comments for additional tools:
    # To monitor network traffic, consider using a container-based IDS/IPS like Aqua, Sysdig, AlertLogic, or Twistlock.
    # For managing external service access, consider a service mesh like Istio or Linkerd.

    # Implement least privilege principles: ensure security group rules are as specific as possible.
    # Team members should use the bastion host or VPN client to securely connect to the environment via SGBastion Security Group.
