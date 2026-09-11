terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
    # Uncomment and configure the provider you will use (azure, google, etc.)
    # azurerm = { source = "hashicorp/azurerm" , version = ">= 3.0" }
    # google = { source = "hashicorp/google" , version = ">= 4.0" }
  }
}
