output "alb_dns_name" { value = aws_lb.main.dns_name }
output "api_subnet_ids" { value = aws_subnet.private[*].id }
output "db_publicly_accessible" { value = aws_db_instance.main.publicly_accessible }
output "api_security_group_id" { value = aws_security_group.api.id }
output "db_security_group_id" { value = aws_security_group.db.id }

