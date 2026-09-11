# Provider configuration (example: AWS). Replace with your provider and credentials pattern.
provider "aws" {
  region = var.region
  # credentials should come from environment (AWS_PROFILE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
}

# Example: for Azure use azurerm provider with managed identity or service principal
# provider "azurerm" {
#   features = {}
# }
