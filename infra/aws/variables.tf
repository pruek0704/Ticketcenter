variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}
variable "project_name" {
  type    = string
  default = "ticketcenter"
}
variable "certificate_arn" {
  type        = string
  description = "Validated ACM certificate ARN for the public HTTPS hostname"
}
variable "web_image" {
  type        = string
  description = "Full ECR image URI for the built frontend image"
}
variable "api_image" {
  type        = string
  description = "Full ECR image URI for the built backend image"
}
variable "jwt_secret_arn" {
  type        = string
  description = "ARN of existing Secrets Manager secret containing a JWT secret of at least 32 characters"
}
variable "db_name" {
  type    = string
  default = "ticketcenter"
}
variable "db_user" {
  type    = string
  default = "ticketcenter"
}
variable "demo_password_secret_arns" {
  type        = map(string)
  default     = {}
  description = "Optional Secrets Manager ARNs keyed DEMO_EMPLOYEE_PASSWORD, DEMO_IT_PASSWORD, DEMO_HR_PASSWORD, DEMO_ADMIN_PASSWORD"
  validation {
    condition     = length(var.demo_password_secret_arns) == 0 || (length(var.demo_password_secret_arns) == 4 && alltrue([for k in ["DEMO_EMPLOYEE_PASSWORD", "DEMO_IT_PASSWORD", "DEMO_HR_PASSWORD", "DEMO_ADMIN_PASSWORD"] : contains(keys(var.demo_password_secret_arns), k)]))
    error_message = "Provide all four demo password secret ARNs or none."
  }
}
